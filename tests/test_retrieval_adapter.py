from __future__ import annotations

import unittest

from app.retrieval_adapter import (
    NeonRetrievalAdapter,
    filter_excluded_sections,
    select_with_review_cap,
)
from app.schemas import SearchFilters
from retrieval.retrieval import Candidate


class RetrievalAdapterTests(unittest.TestCase):
    def test_section_filter_excludes_non_evidence_sections(self) -> None:
        candidates = [
            self._candidate("intro", ["1 Introduction"]),
            self._candidate("references", ["IV. References"]),
            self._candidate("acknowledgements", ["Acknowledgements"]),
            self._candidate("results", ["Results", "Cycling performance"]),
        ]

        selected = filter_excluded_sections(candidates, SearchFilters())

        self.assertEqual(selected, [candidates[-1]])

    def test_review_cap_fills_remaining_slots_from_other_types(self) -> None:
        ranked = [
            self._candidate(f"review_{index}") for index in range(1, 7)
        ] + [
            self._candidate(f"experimental_{index}") for index in range(1, 5)
        ]
        paper_types = {
            **{f"review_{index}": "Review" for index in range(1, 7)},
            **{f"experimental_{index}": "Experimental" for index in range(1, 5)},
        }

        selected = select_with_review_cap(ranked, paper_types, top_k=8)

        self.assertEqual(
            [candidate.record_id for candidate in selected],
            [
                *(f"review_{i}" for i in range(1, 5)),
                *(f"experimental_{i}" for i in range(1, 5)),
            ],
        )

    @staticmethod
    def _candidate(
        record_id: str, section_headings: list[str] | None = None
    ) -> Candidate:
        return Candidate(
            chunk_id=f"{record_id}::chunk::0001",
            record_id=record_id,
            chunk_index=1,
            text="Evidence",
            page_numbers=[1],
            title="Paper title",
            doi=None,
            battery_chemistry_cathode=None,
            manufacturer=None,
            form_factor=None,
            section_headings=section_headings or ["Results"],
            vector_rank=1,
            vector_similarity=0.9,
        )

    def test_candidate_mapping_preserves_ranking_and_provenance(self) -> None:
        candidate = Candidate(
            chunk_id="paper::chunk::0003",
            record_id="paper",
            chunk_index=3,
            text="Charging evidence",
            page_numbers=[4, 5],
            title="Paper title",
            doi="10.1234/example",
            battery_chemistry_cathode="LFP",
            manufacturer=None,
            form_factor="pouch",
            section_headings=["Results", "Fast charging"],
            vector_rank=7,
            vector_similarity=0.81,
            reranker_score=2.4,
        )

        evidence = NeonRetrievalAdapter._to_evidence(candidate)

        self.assertEqual(evidence.chunk_id, candidate.chunk_id)
        self.assertEqual(evidence.page_numbers, (4, 5))
        self.assertEqual(evidence.section, "Results > Fast charging")
        self.assertEqual(evidence.similarity, 2.4)
        self.assertEqual(evidence.metadata["vector_rank"], 7)
        self.assertEqual(evidence.metadata["doi"], "10.1234/example")


if __name__ == "__main__":
    unittest.main()
