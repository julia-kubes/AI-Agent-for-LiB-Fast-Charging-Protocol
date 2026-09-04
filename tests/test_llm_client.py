from __future__ import annotations

import unittest
from unittest.mock import patch

import httpx

from app.config import Settings
from app.llm_client import OpenAICompatibleLLM


def settings() -> Settings:
    return Settings(
        database_url=None,
        llm_base_url="https://example.test/v1",
        llm_api_key="test-key",
        llm_model="test-model",
        embedding_model="test-embedding",
        max_agent_rounds=3,
        max_searches=2,
        max_retrieved_chunks=12,
        max_evidence_characters=36_000,
        max_output_tokens=3_000,
        request_timeout_seconds=90,
    )


def response(status: int, body: dict | None = None) -> httpx.Response:
    request = httpx.Request("POST", "https://example.test/v1/chat/completions")
    return httpx.Response(status, request=request, json=body or {})


class LLMClientRetryTests(unittest.TestCase):
    @patch("app.llm_client.time.sleep")
    @patch("app.llm_client.httpx.post")
    def test_retries_a_transient_gateway_error(self, post, sleep) -> None:
        post.side_effect = [
            response(502),
            response(
                200,
                {
                    "choices": [
                        {"message": {"content": "OK"}, "finish_reason": "stop"}
                    ]
                },
            ),
        ]

        reply = OpenAICompatibleLLM(settings()).complete([{"role": "user", "content": "Hi"}])

        self.assertEqual(reply.content, "OK")
        self.assertEqual(post.call_count, 2)
        sleep.assert_called_once_with(1)

    @patch("app.llm_client.time.sleep")
    @patch("app.llm_client.httpx.post")
    def test_stops_after_three_gateway_errors(self, post, sleep) -> None:
        post.side_effect = [response(503), response(503), response(503)]

        with self.assertRaisesRegex(RuntimeError, "HTTP 503"):
            OpenAICompatibleLLM(settings()).complete([{"role": "user", "content": "Hi"}])

        self.assertEqual(post.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2])


if __name__ == "__main__":
    unittest.main()
