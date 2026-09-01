from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace


def load_retrieval_v3():
    path = Path(__file__).resolve().parents[1] / "retrieval" / "retrieval.v3.py"
    spec = importlib.util.spec_from_file_location("retrieval_v3", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


retrieval_v3 = load_retrieval_v3()


class RetrievalV3SelectionTests(unittest.TestCase):
    def test_review_cap_skips_excess_reviews_and_fills_from_other_types(self) -> None:
        ranked = [
            SimpleNamespace(record_id=f"review_{index}")
            for index in range(1, 7)
        ] + [
            SimpleNamespace(record_id=f"experimental_{index}")
            for index in range(1, 5)
        ]
        paper_types = {
            **{f"review_{index}": "Review" for index in range(1, 7)},
            **{
                f"experimental_{index}": "Experimental"
                for index in range(1, 5)
            },
        }

        selected = retrieval_v3.select_with_review_cap(
            ranked, paper_types, top_k=8
        )

        selected_ids = [candidate.record_id for candidate in selected]
        self.assertEqual(len(selected), 8)
        self.assertEqual(selected_ids[:4], [f"review_{i}" for i in range(1, 5)])
        self.assertEqual(
            selected_ids[4:], [f"experimental_{i}" for i in range(1, 5)]
        )


if __name__ == "__main__":
    unittest.main()
