"""Offline demonstration backends used while retrieval and API access are unavailable."""

from __future__ import annotations

import json
from typing import Any, Sequence

from .schemas import EvidenceChunk, ModelReply, SearchFilters, ToolCall, Usage


DEMO_CHUNKS = [
    EvidenceChunk(
        chunk_id="demo-paper::chunk::0001",
        record_id="demo-paper",
        title="Demonstration paper",
        section="Results",
        page_numbers=(5,),
        similarity=0.88,
        text=(
            "This synthetic demonstration passage reports that charging conditions must be "
            "adapted to cell temperature and validated for the specific cell design."
        ),
    ),
    EvidenceChunk(
        chunk_id="demo-paper::chunk::0002",
        record_id="demo-paper",
        title="Demonstration paper",
        section="Discussion",
        page_numbers=(6,),
        similarity=0.81,
        text=(
            "This synthetic demonstration passage emphasizes monitoring degradation and "
            "avoiding protocol transfer between cell chemistries without experimental validation."
        ),
    ),
]


class DemoRetrieval:
    def search_chunks(
        self, query: str, filters: SearchFilters, top_k: int
    ) -> list[EvidenceChunk]:
        del query, filters
        return DEMO_CHUNKS[:top_k]

    def fetch_neighbors(
        self, chunk_id: str, before: int = 1, after: int = 1
    ) -> list[EvidenceChunk]:
        del before, after
        return [chunk for chunk in DEMO_CHUNKS if chunk.chunk_id != chunk_id]

    def get_paper_metadata(self, record_id: str) -> dict[str, Any]:
        return {"record_id": record_id, "title": "Demonstration paper", "synthetic": True}


class DemoLLM:
    """Deterministic two-turn model: retrieve once, then return valid JSON."""

    def complete(
        self,
        messages: Sequence[dict[str, Any]],
        tools: Sequence[dict[str, Any]] | None = None,
    ) -> ModelReply:
        del tools
        has_tool_result = any(message.get("role") == "tool" for message in messages)
        if not has_tool_result:
            return ModelReply(
                content=None,
                tool_calls=(
                    ToolCall(
                        call_id="demo-search-1",
                        name="search_chunks",
                        arguments={
                            "query": "fast charging protocol evidence",
                            "top_k": 5,
                            "filters": {
                                "excluded_sections": ["introduction", "abstract"]
                            },
                        },
                    ),
                ),
                usage=Usage(300, 25),
            )
        answer = {
            "summary": "The offline infrastructure demonstration completed successfully.",
            "protocol_suggestions": [
                {
                    "strategy": "Adapt the protocol to measured cell conditions.",
                    "reported_or_inferred": "synthesized",
                    "applicable_conditions": ["Cell-specific validation required"],
                    "rationale": "The demonstration evidence cautions against unvalidated transfer.",
                    "evidence_chunk_ids": ["demo-paper::chunk::0001"],
                    "limitations": ["The evidence in demo mode is synthetic."],
                    "confidence": "low",
                }
            ],
            "conflicting_evidence": [],
            "missing_information": ["Real retrieval results"],
            "safety_notes": ["Do not use demo output to control charging hardware."],
            "follow_up_questions": [],
        }
        return ModelReply(json.dumps(answer), usage=Usage(650, 180))

