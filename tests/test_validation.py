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
                "rationale": "The result was reported.",
                "evidence_chunk_ids": ["paper::chunk::0001"],
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


if __name__ == "__main__":
    unittest.main()
