"""Deterministic validation for model-produced protocol suggestions."""

from __future__ import annotations

import json
import re
from typing import Any, Sequence

from .schemas import EvidenceChunk, ValidationResult


REQUIRED_TOP_LEVEL = {
    "summary",
    "protocol_suggestions",
    "conflicting_evidence",
    "missing_information",
    "safety_notes",
    "follow_up_questions",
}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
ALLOWED_ORIGIN = {"reported", "synthesized", "inferred"}
NUMBER_WITH_UNIT = re.compile(
    r"(?<!\w)[+-]?(?:\d+(?:\.\d+)?|\.\d+)\s*(?:C|°C|K|V|mV|A|mA|%|SOC|h|min|s)\b",
    re.IGNORECASE,
)


def parse_final_answer(content: str | None) -> dict[str, Any]:
    if not content or not content.strip():
        raise ValueError("Model returned an empty final answer")
    try:
        value = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError("Model final answer is not valid JSON") from error
    if not isinstance(value, dict):
        raise ValueError("Model final answer must be a JSON object")
    return value


def validate_answer(
    answer: dict[str, Any], evidence: Sequence[EvidenceChunk]
) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    missing = REQUIRED_TOP_LEVEL - answer.keys()
    if missing:
        errors.append("Missing fields: " + ", ".join(sorted(missing)))

    suggestions = answer.get("protocol_suggestions")
    if not isinstance(suggestions, list):
        errors.append("protocol_suggestions must be a list")
        suggestions = []

    allowed_ids = {chunk.chunk_id for chunk in evidence}
    evidence_by_id = {chunk.chunk_id: chunk.text for chunk in evidence}
    for index, suggestion in enumerate(suggestions, start=1):
        label = f"protocol_suggestions[{index}]"
        if not isinstance(suggestion, dict):
            errors.append(f"{label} must be an object")
            continue
        citations = suggestion.get("evidence_chunk_ids")
        if not isinstance(citations, list) or not citations:
            errors.append(f"{label} requires at least one evidence_chunk_id")
            citations = []
        invalid = [citation for citation in citations if citation not in allowed_ids]
        if invalid:
            errors.append(f"{label} cites unavailable chunks: {invalid}")
        if suggestion.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append(f"{label} has invalid confidence")
        if suggestion.get("reported_or_inferred") not in ALLOWED_ORIGIN:
            errors.append(f"{label} has invalid reported_or_inferred value")

        cited_text = " ".join(evidence_by_id.get(citation, "") for citation in citations)
        claim_text = " ".join(
            str(suggestion.get(field, "")) for field in ("strategy", "rationale")
        )
        unsupported_numbers = [
            match.group(0)
            for match in NUMBER_WITH_UNIT.finditer(claim_text)
            if match.group(0).lower().replace(" ", "")
            not in cited_text.lower().replace(" ", "")
        ]
        if unsupported_numbers:
            warnings.append(
                f"{label} contains numerical values not found verbatim in cited evidence: "
                + ", ".join(unsupported_numbers)
            )

    if errors:
        return ValidationResult("reject", tuple(errors), tuple(warnings))
    if warnings:
        return ValidationResult("pass_with_warnings", (), tuple(warnings))
    return ValidationResult("pass")

