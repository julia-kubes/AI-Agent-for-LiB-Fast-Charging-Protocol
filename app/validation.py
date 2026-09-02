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
ALLOWED_ORIGIN = {"reported", "synthesized", "extrapolated", "inferred"}
ALLOWED_VALUE_BASIS = {"reported", "extrapolated", "unresolved"}
REQUIRED_SUGGESTION_FIELDS = {
    "strategy",
    "reported_or_inferred",
    "applicable_conditions",
    "protocol_steps",
    "rationale",
    "evidence_chunk_ids",
    "extrapolation",
    "validation_plan",
    "limitations",
    "confidence",
}
REQUIRED_STEP_FIELDS = {
    "stage",
    "current_or_c_rate",
    "start_condition",
    "transition_criterion",
    "temperature_constraints",
    "monitoring",
    "stop_conditions",
    "value_basis",
}
NUMBER_WITH_UNIT = re.compile(
    r"(?<!\w)[+-]?(?:\d+(?:\.\d+)?|\.\d+)\s*(?:C|°C|K|V|mV|A|mA|%|SOC|h|min|s)\b",
    re.IGNORECASE,
)


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_flatten_text(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return " ".join(_flatten_text(item) for item in value)
    return str(value or "")


def parse_final_answer(content: str | None) -> dict[str, Any]:
    if not content or not content.strip():
        raise ValueError("Model returned an empty final answer")
    normalized = content.strip()
    if normalized.startswith("```") and normalized.endswith("```"):
        first_newline = normalized.find("\n")
        if first_newline != -1:
            normalized = normalized[first_newline + 1 : -3].strip()
    try:
        value = json.loads(normalized)
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
    elif len(suggestions) > 3:
        errors.append("protocol_suggestions must contain no more than three protocols")

    allowed_ids = {chunk.chunk_id for chunk in evidence}
    evidence_by_id = {chunk.chunk_id: chunk.text for chunk in evidence}
    for index, suggestion in enumerate(suggestions, start=1):
        label = f"protocol_suggestions[{index}]"
        if not isinstance(suggestion, dict):
            errors.append(f"{label} must be an object")
            continue
        missing_suggestion = REQUIRED_SUGGESTION_FIELDS - suggestion.keys()
        if missing_suggestion:
            errors.append(
                f"{label} is missing fields: " + ", ".join(sorted(missing_suggestion))
            )
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

        steps = suggestion.get("protocol_steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"{label} requires at least one protocol step")
            steps = []
        for step_index, step in enumerate(steps, start=1):
            step_label = f"{label}.protocol_steps[{step_index}]"
            if not isinstance(step, dict):
                errors.append(f"{step_label} must be an object")
                continue
            missing_step = REQUIRED_STEP_FIELDS - step.keys()
            if missing_step:
                errors.append(
                    f"{step_label} is missing fields: "
                    + ", ".join(sorted(missing_step))
                )
            if step.get("value_basis") not in ALLOWED_VALUE_BASIS:
                errors.append(f"{step_label} has invalid value_basis")

        extrapolation = suggestion.get("extrapolation")
        if not isinstance(extrapolation, dict) or not isinstance(
            extrapolation.get("used"), bool
        ):
            errors.append(f"{label}.extrapolation requires a boolean used field")
            extrapolation_used = False
        else:
            extrapolation_used = extrapolation["used"]
            if extrapolation_used:
                for field in (
                    "source_conditions",
                    "target_conditions",
                    "justification",
                    "key_differences",
                ):
                    if not extrapolation.get(field):
                        errors.append(
                            f"{label}.extrapolation requires {field} when used is true"
                        )
        if suggestion.get("reported_or_inferred") == "extrapolated" and not extrapolation_used:
            errors.append(f"{label} must disclose extrapolation details")

        validation_plan = suggestion.get("validation_plan")
        if not isinstance(validation_plan, list) or not validation_plan:
            errors.append(f"{label} requires a non-empty validation_plan")

        cited_text = " ".join(evidence_by_id.get(citation, "") for citation in citations)
        claim_text = " ".join(
            _flatten_text(suggestion.get(field))
            for field in (
                "strategy",
                "rationale",
                "applicable_conditions",
                "protocol_steps",
            )
        )
        unsupported_numbers = [
            match.group(0)
            for match in NUMBER_WITH_UNIT.finditer(claim_text)
            if match.group(0).lower().replace(" ", "")
            not in cited_text.lower().replace(" ", "")
        ]
        if unsupported_numbers:
            message = (
                f"{label} contains numerical values not found verbatim in cited evidence: "
                + ", ".join(unsupported_numbers)
            )
            if extrapolation_used:
                warnings.append(message + "; disclosed as extrapolation")
            else:
                errors.append(message + "; extrapolation was not disclosed")

    if errors:
        return ValidationResult("reject", tuple(errors), tuple(warnings))
    if warnings:
        return ValidationResult("pass_with_warnings", (), tuple(warnings))
    return ValidationResult("pass")
