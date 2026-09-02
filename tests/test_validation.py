from __future__ import annotations

import unittest

from app.schemas import EvidenceChunk
from app.validation import parse_final_answer, validate_answer


def base_answer() -> dict:
    return {
        "summary": "Summary",
        "protocol_suggestions": [
            {
                "strategy": "Use the reported approach.",
                "reported_or_inferred": "reported",
                "applicable_conditions": [],
                "protocol_steps": [
                    {
                        "stage": "Constant-current charge",
                        "current_or_c_rate": "1 C",
                        "start_condition": "Begin at 25 °C",
                        "transition_criterion": "End at the reported voltage limit",
                        "temperature_constraints": ["25 °C"],
                        "monitoring": ["Voltage", "Temperature"],
                        "stop_conditions": ["Manufacturer limit"],
                        "value_basis": "reported",
                    }
                ],
                "rationale": "The result was reported.",
                "evidence_chunk_ids": ["paper::chunk::0001"],
                "extrapolation": {
                    "used": False,
                    "source_conditions": [],
                    "target_conditions": [],
                    "justification": "",
                    "key_differences": [],
                },
                "validation_plan": ["Verify the response on the target cell"],
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
                text="The experiment used 1 C at 25 °C.",
            ),
        )

    def test_valid_citation_passes(self) -> None:
        self.assertEqual(validate_answer(base_answer(), self.evidence).status, "pass")

    def test_unknown_citation_is_rejected(self) -> None:
        answer = base_answer()
        answer["protocol_suggestions"][0]["evidence_chunk_ids"] = ["invented"]
        result = validate_answer(answer, self.evidence)
        self.assertEqual(result.status, "reject")
        self.assertTrue(any("unavailable" in error for error in result.errors))

    def test_markdown_fenced_json_is_accepted(self) -> None:
        content = "```json\n" + __import__("json").dumps(base_answer()) + "\n```"
        self.assertEqual(parse_final_answer(content), base_answer())

    def test_undisclosed_extrapolated_number_is_rejected(self) -> None:
        answer = base_answer()
        answer["protocol_suggestions"][0]["protocol_steps"][0][
            "current_or_c_rate"
        ] = "2 C"
        result = validate_answer(answer, self.evidence)
        self.assertEqual(result.status, "reject")
        self.assertTrue(any("extrapolation was not disclosed" in error for error in result.errors))

    def test_disclosed_extrapolated_number_passes_with_warning(self) -> None:
        answer = base_answer()
        suggestion = answer["protocol_suggestions"][0]
        suggestion["reported_or_inferred"] = "extrapolated"
        suggestion["protocol_steps"][0]["current_or_c_rate"] = "2 C"
        suggestion["protocol_steps"][0]["value_basis"] = "extrapolated"
        suggestion["extrapolation"] = {
            "used": True,
            "source_conditions": ["Reported laboratory cell"],
            "target_conditions": ["Target pouch cell"],
            "justification": "Use as a provisional starting value.",
            "key_differences": ["Different form factor"],
        }
        result = validate_answer(answer, self.evidence)
        self.assertEqual(result.status, "pass_with_warnings")
        self.assertTrue(any("disclosed as extrapolation" in warning for warning in result.warnings))


if __name__ == "__main__":
    unittest.main()
