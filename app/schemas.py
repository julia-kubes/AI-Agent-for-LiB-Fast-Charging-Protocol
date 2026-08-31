"""Provider-neutral data contracts used across retrieval and generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class SearchFilters:
    record_id: str | None = None
    excluded_sections: tuple[str, ...] = ("introduction", "abstract")

    @classmethod
    def from_mapping(cls, value: dict[str, Any] | None) -> "SearchFilters":
        value = value or {}
        excluded = value.get("excluded_sections", ("introduction", "abstract"))
        if not isinstance(excluded, (list, tuple)) or not all(
            isinstance(item, str) for item in excluded
        ):
            raise ValueError("excluded_sections must be a list of strings")
        record_id = value.get("record_id")
        if record_id is not None and not isinstance(record_id, str):
            raise ValueError("record_id must be a string or null")
        return cls(record_id=record_id, excluded_sections=tuple(excluded))


@dataclass(frozen=True)
class EvidenceChunk:
    chunk_id: str
    record_id: str
    text: str
    title: str | None = None
    section: str | None = None
    page_numbers: tuple[int, ...] = ()
    similarity: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ToolCall:
    call_id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class ModelReply:
    content: str | None
    tool_calls: tuple[ToolCall, ...] = ()
    usage: Usage = Usage()
    finish_reason: str | None = None


@dataclass(frozen=True)
class ValidationResult:
    status: Literal["pass", "pass_with_warnings", "reject"]
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentResult:
    answer: dict[str, Any]
    evidence: tuple[EvidenceChunk, ...]
    validation: ValidationResult
    usage: Usage
    agent_rounds: int
    tool_calls: int
