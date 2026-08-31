"""Interfaces that isolate the in-progress retrieval implementation."""

from __future__ import annotations

from typing import Any, Protocol, Sequence

from .schemas import EvidenceChunk, ModelReply, SearchFilters


class RetrievalBackend(Protocol):
    def search_chunks(
        self, query: str, filters: SearchFilters, top_k: int
    ) -> list[EvidenceChunk]: ...

    def fetch_neighbors(
        self, chunk_id: str, before: int = 1, after: int = 1
    ) -> list[EvidenceChunk]: ...

    def get_paper_metadata(self, record_id: str) -> dict[str, Any]: ...


class LLMBackend(Protocol):
    def complete(
        self,
        messages: Sequence[dict[str, Any]],
        tools: Sequence[dict[str, Any]] | None = None,
    ) -> ModelReply: ...

