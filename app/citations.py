"""Convert internal chunk citations into reader-facing DOI citations."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from .schemas import EvidenceChunk


def chunk_doi(chunk: EvidenceChunk) -> str | None:
    for key, value in chunk.metadata.items():
        if key.casefold() == "doi" and value:
            return str(value).strip() or None
    return None


def reported_dois(
    chunk_ids: Iterable[str], evidence: Sequence[EvidenceChunk]
) -> list[str]:
    evidence_by_id = {chunk.chunk_id: chunk for chunk in evidence}
    dois: list[str] = []
    for chunk_id in chunk_ids:
        chunk = evidence_by_id.get(chunk_id)
        doi = chunk_doi(chunk) if chunk else None
        label = doi or "DOI unavailable"
        if label not in dois:
            dois.append(label)
    return dois


def answer_dois(
    suggestion: dict[str, Any], evidence: Sequence[EvidenceChunk]
) -> list[str]:
    chunk_ids = suggestion.get("evidence_chunk_ids") or []
    return reported_dois(chunk_ids, evidence)
