"""Validated execution of the only tools exposed to the language model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import Settings
from .interfaces import RetrievalBackend
from .schemas import EvidenceChunk, SearchFilters, ToolCall


@dataclass
class ToolExecutor:
    retrieval: RetrievalBackend
    settings: Settings
    search_count: int = 0
    evidence: dict[str, EvidenceChunk] = field(default_factory=dict)

    def execute(self, call: ToolCall) -> Any:
        if call.name == "search_chunks":
            return self._search(call.arguments)
        if call.name == "fetch_neighbors":
            return self._neighbors(call.arguments)
        if call.name == "get_paper_metadata":
            return self._metadata(call.arguments)
        raise ValueError(f"Tool {call.name!r} is not allowed")

    def _search(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        if self.search_count >= self.settings.max_searches:
            raise ValueError("Maximum search count reached")
        query = arguments.get("query")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("search_chunks requires a non-empty query")
        requested = arguments.get("top_k", self.settings.max_retrieved_chunks)
        if not isinstance(requested, int):
            raise ValueError("top_k must be an integer")
        top_k = min(max(requested, 1), self.settings.max_retrieved_chunks)
        filters = SearchFilters.from_mapping(arguments.get("filters"))
        chunks = self.retrieval.search_chunks(query.strip(), filters, top_k)
        self.search_count += 1
        return self._remember(chunks)

    def _neighbors(self, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        chunk_id = arguments.get("chunk_id")
        if not isinstance(chunk_id, str) or not chunk_id:
            raise ValueError("fetch_neighbors requires chunk_id")
        before = arguments.get("before", 1)
        after = arguments.get("after", 1)
        if not isinstance(before, int) or not isinstance(after, int):
            raise ValueError("before and after must be integers")
        chunks = self.retrieval.fetch_neighbors(
            chunk_id, before=min(max(before, 0), 2), after=min(max(after, 0), 2)
        )
        return self._remember(chunks)

    def _metadata(self, arguments: dict[str, Any]) -> dict[str, Any]:
        record_id = arguments.get("record_id")
        if not isinstance(record_id, str) or not record_id:
            raise ValueError("get_paper_metadata requires record_id")
        return self.retrieval.get_paper_metadata(record_id)

    def _remember(self, chunks: list[EvidenceChunk]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        used_characters = sum(len(chunk.text) for chunk in self.evidence.values())
        for chunk in chunks:
            if chunk.chunk_id in self.evidence:
                continue
            if used_characters + len(chunk.text) > self.settings.max_evidence_characters:
                break
            self.evidence[chunk.chunk_id] = chunk
            used_characters += len(chunk.text)
            result.append(chunk.to_dict())
        return result

