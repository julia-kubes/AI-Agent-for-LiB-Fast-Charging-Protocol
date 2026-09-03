"""Bounded, provider-neutral agent loop for evidence-grounded retrieval."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

from .config import Settings
from .interfaces import LLMBackend, RetrievalBackend
from .prompts import (
    SYSTEM_PROMPT,
    TOOLS,
    final_answer_instruction,
    initial_user_message,
    repair_answer_instruction,
    repair_validation_instruction,
)
from .schemas import AgentResult, Usage
from .scope import is_out_of_domain, out_of_domain_answer
from .tools import ToolExecutor
from .validation import normalize_user_specified_values, parse_final_answer, validate_answer


class ResearchAgent:
    def __init__(
        self, retrieval: RetrievalBackend, llm: LLMBackend, settings: Settings
    ) -> None:
        self.retrieval = retrieval
        self.llm = llm
        self.settings = settings

    def answer(
        self, question: str, conditions: dict[str, str] | None = None
    ) -> AgentResult:
        if not question.strip():
            raise ValueError("Question cannot be empty")
        if len(question) > 4_000:
            raise ValueError("Question is too long")

        if is_out_of_domain(question, conditions):
            answer = out_of_domain_answer()
            evidence = ()
            return AgentResult(
                answer=answer,
                evidence=evidence,
                validation=validate_answer(answer, evidence),
                usage=Usage(),
                agent_rounds=0,
                tool_calls=0,
                repair_attempts=0,
            )

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": initial_user_message(question, conditions)},
        ]
        executor = ToolExecutor(self.retrieval, self.settings)
        total_usage = Usage()
        tool_call_count = 0
        repair_attempts = 0
        rounds = 0

        for rounds in range(1, self.settings.max_agent_rounds + 1):
            reply = self.llm.complete(messages, tools=TOOLS)
            total_usage = Usage(
                total_usage.input_tokens + reply.usage.input_tokens,
                total_usage.output_tokens + reply.usage.output_tokens,
            )
            if not reply.tool_calls:
                if not executor.evidence:
                    raise RuntimeError("Model attempted to answer before retrieving evidence")
                evidence = tuple(executor.evidence.values())
                try:
                    if reply.finish_reason == "length":
                        raise ValueError("response reached the output-token limit")
                    answer = normalize_user_specified_values(parse_final_answer(reply.content))
                except ValueError as first_error:
                    repair_attempts = 1
                    messages.append(
                        {"role": "assistant", "content": reply.content or ""}
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": repair_answer_instruction(
                                evidence, str(first_error)
                            ),
                        }
                    )
                    repaired = self.llm.complete(messages, tools=None)
                    rounds += 1
                    total_usage = Usage(
                        total_usage.input_tokens + repaired.usage.input_tokens,
                        total_usage.output_tokens + repaired.usage.output_tokens,
                    )
                    if repaired.tool_calls:
                        raise RuntimeError(
                            "LLM returned tool calls during the final JSON repair"
                        )
                    if repaired.finish_reason == "length":
                        raise RuntimeError(
                            "LLM final answer remained truncated after one repair attempt"
                        )
                    try:
                        answer = normalize_user_specified_values(
                            parse_final_answer(repaired.content)
                        )
                    except ValueError as repair_error:
                        raise RuntimeError(
                            "LLM final answer remained invalid after one repair attempt"
                        ) from repair_error
                validation = validate_answer(answer, evidence)
                if validation.status == "reject" and repair_attempts == 0:
                    repair_attempts = 1
                    messages.append(
                        {"role": "assistant", "content": json.dumps(answer)}
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": repair_validation_instruction(
                                evidence, validation.errors
                            ),
                        }
                    )
                    repaired = self.llm.complete(messages, tools=None)
                    rounds += 1
                    total_usage = Usage(
                        total_usage.input_tokens + repaired.usage.input_tokens,
                        total_usage.output_tokens + repaired.usage.output_tokens,
                    )
                    if repaired.tool_calls:
                        raise RuntimeError(
                            "LLM returned tool calls during protocol validation repair"
                        )
                    answer = normalize_user_specified_values(
                        parse_final_answer(repaired.content)
                    )
                    validation = validate_answer(answer, evidence)
                    if validation.status == "reject":
                        raise RuntimeError(
                            "LLM protocol remained invalid after one repair attempt: "
                            + "; ".join(validation.errors)
                        )
                evidence = self._enrich_final_evidence(answer, evidence)
                return AgentResult(
                    answer,
                    evidence,
                    validation,
                    total_usage,
                    rounds,
                    tool_call_count,
                    repair_attempts,
                )

            assistant_tool_calls = []
            for call in reply.tool_calls:
                assistant_tool_calls.append(
                    {
                        "id": call.call_id,
                        "type": "function",
                        "function": {
                            "name": call.name,
                            "arguments": json.dumps(call.arguments),
                        },
                    }
                )
            messages.append(
                {
                    "role": "assistant",
                    "content": reply.content,
                    "tool_calls": assistant_tool_calls,
                }
            )
            for call in reply.tool_calls:
                tool_call_count += 1
                try:
                    output = executor.execute(call)
                    content = json.dumps(output, ensure_ascii=False)
                except (ValueError, RuntimeError) as error:
                    content = json.dumps({"error": str(error)})
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.call_id,
                        "name": call.name,
                        "content": content,
                    }
                )

            if rounds == self.settings.max_agent_rounds - 1 and executor.evidence:
                messages.append(
                    {
                        "role": "user",
                        "content": final_answer_instruction(tuple(executor.evidence.values())),
                    }
                )

        raise RuntimeError("Agent reached its maximum rounds without a final answer")

    def _enrich_final_evidence(self, answer, evidence):
        """Fetch paper metadata for chunks cited by the final answer."""
        cited_ids = {
            chunk_id
            for suggestion in answer.get("protocol_suggestions") or []
            if isinstance(suggestion, dict)
            for chunk_id in suggestion.get("evidence_chunk_ids") or []
            if isinstance(chunk_id, str)
        }
        cited_record_ids = {
            chunk.record_id for chunk in evidence if chunk.chunk_id in cited_ids
        }
        paper_metadata = {}
        for record_id in cited_record_ids:
            try:
                paper_metadata[record_id] = self.retrieval.get_paper_metadata(record_id)
            except Exception:
                paper_metadata[record_id] = {}
        return tuple(
            replace(
                chunk,
                metadata={**chunk.metadata, **paper_metadata.get(chunk.record_id, {})},
            )
            if chunk.chunk_id in cited_ids
            else chunk
            for chunk in evidence
        )
