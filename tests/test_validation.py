from __future__ import annotations

import unittest

from app.schemas import EvidenceChunk
from app.validation import normalize_user_specified_values, parse_final_answer, validate_answer


def parameter(value, unit, basis="reported") -> dict:
    return {
        "value": value,
        "unit": unit,
        "basis": basis,
        "source_value": None,
        "source_unit": None,
        "source_conditions": [],
        "adjustment_rule": None,
        "rationale": "Directly reported.",
        "evidence_chunk_ids": ["paper::chunk::0001"] if basis != "unresolved" else [],
        "confidence": "medium",
    }


def base_answer() -> dict:
    transition = parameter(80, "%")
    transition.update({"variable": "SOC", "operator": ">="})
    return {
        "summary": "Summary",
        "protocol_suggestions": [
            {
                "strategy": "Use the reported protocol.",
                "designation": "primary",
                "protocol_status": "literature_transferred_candidate",
                "reported_or_inferred": "reported",
                "target_conditions": {
                    "chemistry": "graphite/NMC",
                    "form_factor": "laboratory cell",
                    "capacity_ah": None,
                    "temperature_c": 25,
                    "start_soc_percent": None,
                    "end_soc_percent": 80,
                    "target_time_minutes": None,
                },
                "protocol_steps": [
                    {
                        "stage_number": 1,
                        "stage_name": "Constant-current charge",
                        "control_mode": "CC",
                        "start_condition": "Begin at the supplied starting SOC.",
                        "current": parameter(1, "C"),
                        "voltage_limit": parameter(4.2, "V"),
                        "temperature_limit": parameter(25, "°C"),
                        "transition": transition,
                        "monitoring": ["Cell voltage", "Cell temperature"],
                        "stop_conditions": ["Stop at 4.2 V or 25 °C."],
                    }
                ],
                "rationale": "The values are directly reported.",
                "evidence_chunk_ids": ["paper::chunk::0001"],
                "extrapolation": {
                    "used": False,
                    "source_conditions": [],
                    "target_conditions": [],
                    "justification": "",
                    "key_differences": [],
                },
                "validation_plan": ["Verify the protocol on the target cell."],
                "limitations": [],
                "confidence": "medium",
            }
        ],
        "conflicting_evidence": [],
        "missing_information": [],
        "safety_notes": [],
        "follow_up_questions": [],
    }


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence = (
            EvidenceChunk(
                chunk_id="paper::chunk::0001",
                record_id="paper",
                text="The experiment used 1 C at 25 °C with a 4.2 V limit to 80% SOC.",
            ),
        )

    def test_structured_reported_protocol_passes(self) -> None:
        self.assertEqual(validate_answer(base_answer(), self.evidence).status, "pass")

    def test_unknown_citation_is_rejected(self) -> None:
        answer = base_answer()
        answer["protocol_suggestions"][0]["protocol_steps"][0]["current"][
            "evidence_chunk_ids"
        ] = ["invented"]
        result = validate_answer(answer, self.evidence)
        self.assertEqual(result.status, "reject")
        self.assertTrue(any("unavailable" in error for error in result.errors))

    def test_markdown_fenced_json_is_accepted(self) -> None:
        content = "```json\n" + __import__("json").dumps(base_answer()) + "\n```"
        self.assertEqual(parse_final_answer(content), base_answer())

    def test_evidence_transfer_requires_reasoning(self) -> None:
        answer = base_answer()
        current = answer["protocol_suggestions"][0]["protocol_steps"][0]["current"]
        current.update(
            {
                "value": 2,
                "basis": "evidence_informed_transfer",
                "source_value": None,
                "source_unit": None,
                "source_conditions": [],
                "adjustment_rule": None,
            }
        )
        result = validate_answer(answer, self.evidence)
        self.assertEqual(result.status, "reject")
        self.assertTrue(any("source_conditions" in error for error in result.errors))

    def test_evidence_informed_transfer_passes_without_exact_proposed_value_in_evidence(self) -> None:
        answer = base_answer()
        suggestion = answer["protocol_suggestions"][0]
        suggestion["reported_or_inferred"] = "extrapolated"
        suggestion["extrapolation"] = {
            "used": True,
            "source_conditions": ["Reported laboratory cell"],
            "target_conditions": ["Target pouch cell"],
            "justification": "Conservative source-to-target adjustment.",
            "key_differences": ["Different form factor"],
        }
        current = suggestion["protocol_steps"][0]["current"]
        current.update(
            {
                "value": 0.5,
                "basis": "evidence_informed_transfer",
                "source_value": 1,
                "source_unit": "C",
                "source_conditions": ["Reported laboratory cell at 25 °C"],
                "adjustment_rule": "Reduce the reported current by 50%.",
                "rationale": "Begin conservatively for the different form factor.",
            }
        )
        self.assertEqual(validate_answer(answer, self.evidence).status, "pass")

    def test_nonverbatim_transfer_anchor_warns_instead_of_rejecting(self) -> None:
        answer = base_answer()
        suggestion = answer["protocol_suggestions"][0]
        suggestion["reported_or_inferred"] = "extrapolated"
        suggestion["extrapolation"] = {
            "used": True,
            "source_conditions": ["Reported laboratory cell"],
            "target_conditions": ["Target pouch cell"],
            "justification": "Transfer with a source value requiring human review.",
            "key_differences": ["Different form factor"],
        }
        current = suggestion["protocol_steps"][0]["current"]
        current.update(
            {
                "value": 0.75,
                "basis": "evidence_informed_transfer",
                "source_value": 1.5,
                "source_unit": "C",
                "source_conditions": ["Reported laboratory cell"],
                "adjustment_rule": "Reduce the source current by half.",
                "rationale": "Use a conservative transfer for the target cell.",
            }
        )
        result = validate_answer(answer, self.evidence)
        self.assertEqual(result.status, "pass_with_warnings")
        self.assertTrue(any("not found verbatim" in warning for warning in result.warnings))

    def test_engineering_judgment_passes_with_disclosure_and_cited_context(self) -> None:
        answer = base_answer()
        suggestion = answer["protocol_suggestions"][0]
        suggestion["protocol_status"] = "experimental_starting_protocol"
        suggestion["reported_or_inferred"] = "inferred"
        suggestion["extrapolation"] = {
            "used": True,
            "source_conditions": ["Reported graphite/NMC laboratory evidence"],
            "target_conditions": ["Target pouch cell"],
            "justification": "Select a conservative experimental starting point.",
            "key_differences": ["Different cell format and capacity"],
        }
        current = suggestion["protocol_steps"][0]["current"]
        current.update(
            {
                "value": 0.75,
                "basis": "engineering_judgment",
                "source_value": None,
                "source_unit": None,
                "source_conditions": ["Literature establishes the relevant charging mechanism"],
                "adjustment_rule": "Select below the directly reported 1 C condition.",
                "rationale": "A conservative initial test value for the changed form factor.",
                "confidence": "low",
            }
        )
        self.assertEqual(validate_answer(answer, self.evidence).status, "pass")

    def test_engineering_judgment_cannot_claim_high_confidence(self) -> None:
        answer = base_answer()
        suggestion = answer["protocol_suggestions"][0]
        suggestion["protocol_status"] = "experimental_starting_protocol"
        suggestion["extrapolation"]["used"] = True
        suggestion["extrapolation"]["source_conditions"] = ["Literature cell"]
        suggestion["extrapolation"]["target_conditions"] = ["Target cell"]
        suggestion["extrapolation"]["justification"] = "Experimental assumption."
        suggestion["extrapolation"]["key_differences"] = ["Cell format"]
        current = suggestion["protocol_steps"][0]["current"]
        current.update({"value": 0.75, "basis": "engineering_judgment", "confidence": "high"})
        result = validate_answer(answer, self.evidence)
        self.assertEqual(result.status, "reject")
        self.assertTrue(any("high confidence" in error for error in result.errors))

    def test_user_specified_temperature_and_soc_target_pass(self) -> None:
        answer = base_answer()
        step = answer["protocol_suggestions"][0]["protocol_steps"][0]
        step["temperature_limit"].update(
            {
                "value": 25,
                "unit": "°C",
                "basis": "user_specified",
                "source_value": None,
                "source_unit": None,
                "source_conditions": [],
                "adjustment_rule": None,
                "rationale": "The user requested operation at 25 °C.",
                "evidence_chunk_ids": [],
            }
        )
        step["transition"].update(
            {
                "value": 80,
                "unit": "%",
                "basis": "user_specified",
                "source_value": None,
                "source_unit": None,
                "source_conditions": [],
                "adjustment_rule": None,
                "rationale": "The user requested an 80% SOC endpoint.",
                "evidence_chunk_ids": [],
            }
        )
        self.assertEqual(validate_answer(answer, self.evidence).status, "pass")

    def test_user_specified_value_must_match_target_conditions(self) -> None:
        answer = base_answer()
        temperature = answer["protocol_suggestions"][0]["protocol_steps"][0][
            "temperature_limit"
        ]
        temperature.update(
            {
                "value": 30,
                "basis": "user_specified",
                "rationale": "Claimed user target.",
                "evidence_chunk_ids": [],
            }
        )
        result = validate_answer(answer, self.evidence)
        self.assertEqual(result.status, "reject")
        self.assertTrue(any("does not match the target conditions" in error for error in result.errors))

    def test_target_values_are_deterministically_reclassified(self) -> None:
        answer = base_answer()
        step = answer["protocol_suggestions"][0]["protocol_steps"][0]
        step["temperature_limit"]["basis"] = "reported"
        step["transition"]["basis"] = "reported"

        normalize_user_specified_values(answer)

        self.assertEqual(step["temperature_limit"]["basis"], "user_specified")
        self.assertEqual(step["temperature_limit"]["evidence_chunk_ids"], [])
        self.assertEqual(step["transition"]["basis"], "user_specified")
        self.assertEqual(step["transition"]["source_value"], None)

    def test_unresolved_noncritical_limits_do_not_block_experimental_protocol(self) -> None:
        answer = base_answer()
        suggestion = answer["protocol_suggestions"][0]
        suggestion["protocol_status"] = "experimental_starting_protocol"
        suggestion["protocol_steps"][0]["voltage_limit"] = parameter(
            None, "V", "unresolved"
        )
        suggestion["protocol_steps"][0]["temperature_limit"] = parameter(
            None, "°C", "unresolved"
        )
        self.assertEqual(validate_answer(answer, self.evidence).status, "pass")

    def test_experimental_protocol_cannot_contain_unresolved_parameter(self) -> None:
        answer = base_answer()
        answer["protocol_suggestions"][0]["protocol_status"] = "experimental_starting_protocol"
        answer["protocol_suggestions"][0]["protocol_steps"][0]["current"] = parameter(
            None, "C", "unresolved"
        )
        result = validate_answer(answer, self.evidence)
        self.assertEqual(result.status, "reject")
        self.assertTrue(any("cannot be experimental_starting_protocol" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
