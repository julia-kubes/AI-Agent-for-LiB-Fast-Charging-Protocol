from __future__ import annotations

import unittest

from app.agent import ResearchAgent
from app.config import Settings
from app.demo import DemoLLM, DemoRetrieval


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
    def test_offline_agent_retrieves_and_returns_valid_answer(self) -> None:
        result = ResearchAgent(DemoRetrieval(), DemoLLM(), settings()).answer(
            "What factors should constrain a fast-charging protocol?"
        )
        self.assertEqual(result.validation.status, "pass")
        self.assertEqual(result.agent_rounds, 2)
        self.assertEqual(result.tool_calls, 1)
        self.assertEqual(len(result.evidence), 2)
        self.assertGreater(result.usage.total_tokens, 0)

    def test_empty_question_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            ResearchAgent(DemoRetrieval(), DemoLLM(), settings()).answer("  ")


if __name__ == "__main__":
    unittest.main()

