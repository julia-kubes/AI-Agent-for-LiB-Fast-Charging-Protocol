"""Minimal OpenAI-compatible client for Parley and fallback providers."""

from __future__ import annotations

import json
import time
from typing import Any, Sequence

import httpx

from .config import Settings
from .schemas import ModelReply, ToolCall, Usage


RETRYABLE_HTTP_STATUSES = {502, 503, 504}
MAX_REQUEST_ATTEMPTS = 3


class OpenAICompatibleLLM:
    def __init__(self, settings: Settings):
        settings.require_llm()
        self.settings = settings

    def complete(
        self,
        messages: Sequence[dict[str, Any]],
        tools: Sequence[dict[str, Any]] | None = None,
    ) -> ModelReply:
        payload: dict[str, Any] = {
            "model": self.settings.llm_model,
            "messages": list(messages),
            "max_tokens": self.settings.max_output_tokens,
            "temperature": 0.1,
        }
        if tools:
            payload["tools"] = list(tools)
            payload["tool_choice"] = "auto"

        for attempt in range(MAX_REQUEST_ATTEMPTS):
            try:
                response = httpx.post(
                    f"{self.settings.llm_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=self.settings.request_timeout_seconds,
                )
                response.raise_for_status()
                break
            except httpx.HTTPStatusError as error:
                status = error.response.status_code
                if status in RETRYABLE_HTTP_STATUSES and attempt < MAX_REQUEST_ATTEMPTS - 1:
                    time.sleep(2**attempt)
                    continue
                if status == 429:
                    raise RuntimeError("LLM quota or rate limit reached (HTTP 429)") from error
                raise RuntimeError(f"LLM request failed with HTTP {status}") from error
            except httpx.HTTPError as error:
                raise RuntimeError(f"LLM request failed: {type(error).__name__}") from error

        data = response.json()
        try:
            choice = data["choices"][0]
            message = choice["message"]
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError("LLM returned an unexpected response shape") from error

        parsed_calls: list[ToolCall] = []
        for raw in message.get("tool_calls") or []:
            function = raw.get("function") or {}
            try:
                arguments = json.loads(function.get("arguments") or "{}")
            except json.JSONDecodeError as error:
                raise RuntimeError("LLM returned invalid JSON tool arguments") from error
            if not isinstance(arguments, dict):
                raise RuntimeError("LLM tool arguments must be a JSON object")
            parsed_calls.append(
                ToolCall(
                    call_id=str(raw.get("id") or "missing-tool-call-id"),
                    name=str(function.get("name") or ""),
                    arguments=arguments,
                )
            )

        usage = data.get("usage") or {}
        return ModelReply(
            content=message.get("content"),
            tool_calls=tuple(parsed_calls),
            usage=Usage(
                input_tokens=int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0),
                output_tokens=int(
                    usage.get("completion_tokens") or usage.get("output_tokens") or 0
                ),
            ),
            finish_reason=str(choice.get("finish_reason") or "") or None,
        )
