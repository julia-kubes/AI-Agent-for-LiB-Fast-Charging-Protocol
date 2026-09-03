from __future__ import annotations

import unittest

from app.pdf_export import build_response_pdf
from app.ui import format_response_for_clipboard
from app.schemas import EvidenceChunk


class UIFormattingTests(unittest.TestCase):
    def test_pdf_contains_complete_generated_response(self) -> None:
        answer = self._complete_answer()

        pdf = build_response_pdf(answer, self._evidence())

        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertTrue(pdf.rstrip().endswith(b"%%EOF"))
        self.assertGreater(len(pdf), 1_000)

    def test_clipboard_text_contains_complete_generated_response(self) -> None:
        answer = self._complete_answer()

        rendered = format_response_for_clipboard(answer, self._evidence())

        for expected in (
            "Summary text",
            "Test strategy",
            "Test rationale",
            "synthesized",
            "25 °C",
            "pouch cell",
            "Requires validation",
            "10.1234/example",
            "Conflict",
            "Capacity",
            "Validate experimentally",
            "What is the form factor?",
        ):
            self.assertIn(expected, rendered)

    @staticmethod
    def _complete_answer() -> dict:
        return {
            "summary": "Summary text",
            "protocol_suggestions": [
                {
                    "strategy": "Test strategy",
                    "rationale": "Test rationale",
                    "reported_or_inferred": "synthesized",
                    "confidence": "medium",
                    "applicable_conditions": ["25 °C", "pouch cell"],
                    "limitations": ["Requires validation"],
                    "evidence_chunk_ids": ["paper::chunk::0001"],
                }
            ],
            "conflicting_evidence": ["Conflict"],
            "missing_information": ["Capacity"],
            "safety_notes": ["Validate experimentally"],
            "follow_up_questions": ["What is the form factor?"],
        }

    @staticmethod
    def _evidence() -> tuple[EvidenceChunk, ...]:
        return (
            EvidenceChunk(
                chunk_id="paper::chunk::0001",
                record_id="paper",
                text="Evidence",
                metadata={"doi": "10.1234/example"},
            ),
        )

    def test_clipboard_text_handles_an_out_of_domain_response(self) -> None:
        rendered = format_response_for_clipboard(
            {
                "summary": "Outside scope",
                "protocol_suggestions": [],
                "conflicting_evidence": [],
                "missing_information": [],
                "safety_notes": [],
                "follow_up_questions": ["Ask a battery question"],
            }
        )

        self.assertIn("Outside scope", rendered)
        self.assertIn("No protocol suggestions provided.", rendered)
        self.assertIn("Ask a battery question", rendered)


if __name__ == "__main__":
    unittest.main()
