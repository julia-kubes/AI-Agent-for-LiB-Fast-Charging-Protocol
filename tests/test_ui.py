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
            "experimental_starting_protocol",
            "Initial charge",
            "1 C",
            "10% SOC",
            "SOC >= 50 %",
            "Provisional transfer",
            "Cell format",
            "Begin with a limited pilot test",
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
                    "designation": "primary",
                    "protocol_status": "experimental_starting_protocol",
                    "reported_or_inferred": "synthesized",
                    "confidence": "medium",
                    "target_conditions": {
                        "chemistry": "graphite/NMC",
                        "form_factor": "pouch cell",
                        "temperature_c": 25,
                    },
                    "protocol_steps": [
                        {
                            "stage_number": 1,
                            "stage_name": "Initial charge",
                            "control_mode": "CC",
                            "start_condition": "10% SOC",
                            "current": {"value": 1, "unit": "C", "basis": "reported"},
                            "voltage_limit": {"value": 4.2, "unit": "V", "basis": "reported"},
                            "temperature_limit": {"value": 25, "unit": "°C", "basis": "reported"},
                            "transition": {
                                "variable": "SOC", "operator": ">=", "value": 50,
                                "unit": "%", "basis": "reported",
                            },
                            "monitoring": ["Voltage"],
                            "stop_conditions": ["Manufacturer voltage limit"],
                        }
                    ],
                    "extrapolation": {
                        "used": True,
                        "source_conditions": ["Laboratory cell"],
                        "target_conditions": ["Pouch cell"],
                        "justification": "Provisional transfer",
                        "key_differences": ["Cell format"],
                    },
                    "validation_plan": ["Begin with a limited pilot test"],
                    "limitations": ["Requires validation"],
                    "evidence_chunk_ids": ["paper::chunk::0001"],
                }
            ],
            "conflicting_evidence": ["Conflict"],
            "missing_information": ["Capacity"],
            "safety_notes": ["Validate experimentally"],
            "follow_up_questions": ["Legacy field must not be rendered"],
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
                "follow_up_questions": ["Legacy field must not be rendered"],
            },
            self._evidence(),
        )

        self.assertIn("Outside scope", rendered)
        self.assertIn("No protocol suggestions provided.", rendered)
        self.assertNotIn("Follow-up questions", rendered)
        self.assertNotIn("Legacy field must not be rendered", rendered)

    def test_single_string_limitation_is_not_split_into_characters(self) -> None:
        rendered = format_response_for_clipboard(
            {
                "summary": "Summary",
                "protocol_suggestions": [
                    {
                        "strategy": "Strategy",
                        "rationale": "Rationale",
                        "reported_or_inferred": "synthesized",
                        "confidence": "medium",
                        "applicable_conditions": "30 °C laboratory cell",
                        "limitations": "The exact waveform is not specified.",
                        "evidence_chunk_ids": "paper::chunk::0001",
                    }
                ],
                "conflicting_evidence": [],
                "missing_information": [],
                "safety_notes": [],
            },
            self._evidence(),
        )

        self.assertIn("- Limitations: The exact waveform is not specified.", rendered)
        self.assertIn("- Applicable conditions: 30 °C laboratory cell", rendered)
        self.assertIn("- DOI: 10.1234/example", rendered)
        self.assertNotIn("T; h; e", rendered)


if __name__ == "__main__":
    unittest.main()
