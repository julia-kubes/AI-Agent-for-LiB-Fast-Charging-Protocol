from __future__ import annotations

import unittest

from app.retrieval_adapter import NeonRetrievalAdapter
from retrieval.retrieval import Candidate


class RetrievalAdapterTests(unittest.TestCase):
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
