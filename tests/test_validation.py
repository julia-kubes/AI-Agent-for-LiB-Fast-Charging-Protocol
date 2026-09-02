from __future__ import annotations

import unittest

from app.schemas import EvidenceChunk
from app.validation import parse_final_answer, validate_answer


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
                "protocol_status": "executable_candidate",
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

    def test_unanchored_extrapolation_is_rejected(self) -> None:
        answer = base_answer()
        current = answer["protocol_suggestions"][0]["protocol_steps"][0]["current"]
        current.update(
            {
                "value": 2,
                "basis": "anchored_extrapolation",
                "source_value": None,
                "source_unit": None,
            }
        )
        result = validate_answer(answer, self.evidence)
        self.assertEqual(result.status, "reject")
        self.assertTrue(any("source_value" in error for error in result.errors))

    def test_anchored_extrapolation_passes(self) -> None:
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
                "basis": "anchored_extrapolation",
                "source_value": 1,
                "source_unit": "C",
                "source_conditions": ["Reported laboratory cell at 25 °C"],
                "adjustment_rule": "Reduce the reported current by 50%.",
                "rationale": "Begin conservatively for the different form factor.",
            }
        )
        self.assertEqual(validate_answer(answer, self.evidence).status, "pass")

    def test_executable_protocol_cannot_contain_unresolved_parameter(self) -> None:
        answer = base_answer()
        answer["protocol_suggestions"][0]["protocol_steps"][0]["current"] = parameter(
            None, "C", "unresolved"
        )
        result = validate_answer(answer, self.evidence)
        self.assertEqual(result.status, "reject")
        self.assertTrue(any("cannot be executable_candidate" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
