from __future__ import annotations

import unittest

from app.agent import ResearchAgent
from app.config import Settings
from app.demo import DemoLLM, DemoRetrieval
from app.schemas import ModelReply, Usage


def settings() -> Settings:
    return Settings(
        database_url=None,
        llm_base_url="https://example.invalid/v1",
        llm_api_key=None,
        llm_model="demo",
        embedding_model="demo",
        max_agent_rounds=3,
        max_searches=2,
        max_retrieved_chunks=12,
        max_evidence_characters=36_000,
        max_output_tokens=1_500,
        request_timeout_seconds=10,
    )


class ResearchAgentTests(unittest.TestCase):
    def test_casual_query_is_rejected_before_llm_or_retrieval(self) -> None:
        class FailingLLM:
            def complete(self, messages, tools=None):
                raise AssertionError("The LLM must not be called for unrelated input")

        class FailingRetrieval:
            def search_chunks(self, query, filters, top_k):
                raise AssertionError("Retrieval must not run for unrelated input")

            def fetch_neighbors(self, chunk_id, before=1, after=1):
                raise AssertionError("Retrieval must not run for unrelated input")

            def get_paper_metadata(self, record_id):
                raise AssertionError("Retrieval must not run for unrelated input")

        result = ResearchAgent(FailingRetrieval(), FailingLLM(), settings()).answer(
            "What's up?"
        )

        self.assertEqual(result.validation.status, "pass")
        self.assertEqual(result.agent_rounds, 0)
        self.assertEqual(result.tool_calls, 0)
        self.assertEqual(result.usage.total_tokens, 0)
        self.assertEqual(result.evidence, ())
        self.assertEqual(result.answer["protocol_suggestions"], [])
        self.assertIn("outside my current scope", result.answer["summary"])

    def test_clearly_unrelated_question_is_rejected(self) -> None:
        result = ResearchAgent(DemoRetrieval(), DemoLLM(), settings()).answer(
            "How do I bake sourdough bread?"
        )
        self.assertEqual(result.validation.status, "pass")
        self.assertEqual(result.agent_rounds, 0)
        self.assertEqual(result.tool_calls, 0)

    def test_short_question_with_battery_conditions_stays_in_scope(self) -> None:
        result = ResearchAgent(DemoRetrieval(), DemoLLM(), settings()).answer(
            "What approach should I test?", {"chemistry": "graphite/NMC811"}
        )
        self.assertEqual(result.validation.status, "pass")
        self.assertEqual(result.agent_rounds, 2)
        self.assertEqual(result.tool_calls, 1)

    def test_offline_agent_retrieves_and_returns_valid_answer(self) -> None:
        class TrackingRetrieval(DemoRetrieval):
            def __init__(self) -> None:
                self.metadata_requests = []

            def get_paper_metadata(self, record_id):
                self.metadata_requests.append(record_id)
                return super().get_paper_metadata(record_id)

        retrieval = TrackingRetrieval()
        result = ResearchAgent(retrieval, DemoLLM(), settings()).answer(
            "What factors should constrain a fast-charging protocol?"
        )
        self.assertEqual(result.validation.status, "pass")
        self.assertEqual(result.agent_rounds, 2)
        self.assertEqual(result.tool_calls, 1)
        self.assertEqual(len(result.evidence), 2)
        self.assertEqual(result.evidence[0].metadata["doi"], "10.0000/demo")
        self.assertNotIn("doi", result.evidence[1].metadata)
        self.assertEqual(retrieval.metadata_requests, ["demo-paper"])
        self.assertGreater(result.usage.total_tokens, 0)

    def test_empty_question_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            ResearchAgent(DemoRetrieval(), DemoLLM(), settings()).answer("  ")

    def test_truncated_final_answer_is_repaired_once(self) -> None:
        class TruncatedThenRepairedLLM:
            def __init__(self) -> None:
                self.calls = 0
                self.demo = DemoLLM()

            def complete(self, messages, tools=None):
                self.calls += 1
                if self.calls == 1:
                    return self.demo.complete(messages, tools)
                if self.calls == 2:
                    return ModelReply(
                        '{"summary":"truncated',
                        usage=Usage(100, 1500),
                        finish_reason="length",
                    )
                return self.demo.complete(messages, tools)

        llm = TruncatedThenRepairedLLM()
        result = ResearchAgent(DemoRetrieval(), llm, settings()).answer(
            "What factors should constrain a fast-charging protocol?"
        )

        self.assertEqual(llm.calls, 3)
        self.assertEqual(result.agent_rounds, 3)
        self.assertEqual(result.validation.status, "pass")

    def test_invalid_repair_fails_after_one_attempt(self) -> None:
        class AlwaysInvalidFinalLLM:
            def __init__(self) -> None:
                self.calls = 0
                self.demo = DemoLLM()

            def complete(self, messages, tools=None):
                self.calls += 1
                if self.calls == 1:
                    return self.demo.complete(messages, tools)
                return ModelReply("not json", usage=Usage(10, 5))

        llm = AlwaysInvalidFinalLLM()
        with self.assertRaisesRegex(RuntimeError, "after one repair attempt"):
            ResearchAgent(DemoRetrieval(), llm, settings()).answer(
                "What factors should constrain a fast-charging protocol?"
            )
        self.assertEqual(llm.calls, 3)


if __name__ == "__main__":
    unittest.main()
