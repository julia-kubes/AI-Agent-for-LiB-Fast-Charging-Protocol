"""Deterministic validation for structured, evidence-anchored protocols."""

from __future__ import annotations

import json
import re
from typing import Any, Sequence

from .schemas import EvidenceChunk, ValidationResult

REQUIRED_TOP_LEVEL = {"summary", "protocol_suggestions", "conflicting_evidence", "missing_information", "safety_notes", "follow_up_questions"}
REQUIRED_SUGGESTION_FIELDS = {"strategy", "designation", "protocol_status", "reported_or_inferred", "target_conditions", "protocol_steps", "rationale", "evidence_chunk_ids", "extrapolation", "validation_plan", "limitations", "confidence"}
REQUIRED_TARGET_FIELDS = {"chemistry", "form_factor", "capacity_ah", "temperature_c", "start_soc_percent", "end_soc_percent", "target_time_minutes"}
REQUIRED_STEP_FIELDS = {"stage_number", "stage_name", "control_mode", "start_condition", "current", "voltage_limit", "temperature_limit", "transition", "monitoring", "stop_conditions"}
REQUIRED_PARAMETER_FIELDS = {"value", "unit", "basis", "source_value", "source_unit", "source_conditions", "adjustment_rule", "rationale", "evidence_chunk_ids", "confidence"}
REQUIRED_TRANSITION_FIELDS = REQUIRED_PARAMETER_FIELDS | {"variable", "operator"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
ALLOWED_ORIGIN = {"reported", "synthesized", "extrapolated", "inferred"}
ALLOWED_DESIGNATION = {"primary", "alternative"}
ALLOWED_STATUS = {"experimental_starting_protocol", "literature_transferred_candidate", "partially_specified"}
ALLOWED_VALUE_BASIS = {"reported", "evidence_informed_transfer", "engineering_judgment", "unresolved"}
ALLOWED_CONTROL_MODE = {"CC", "CV", "rest", "terminate", "other"}
ALLOWED_TRANSITION_VARIABLE = {"SOC", "voltage", "current", "time", "anode_potential", "other"}
ALLOWED_OPERATOR = {">=", "<=", ">", "<", "="}
VAGUE_OPERATIONAL_LANGUAGE = re.compile(r"\b(as needed|near (?:the )?limit|approaches?|low threshold|manufacturer limit|when appropriate|if necessary)\b", re.IGNORECASE)


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


def _normalized_number(value: int | float, unit: str) -> str:
    number = str(value).lower().replace(" ", "")
    if number.endswith(".0"):
        number = number[:-2]
    return number + unit.lower().replace(" ", "")


def _evidence_contains(value: int | float, unit: str, text: str) -> bool:
    return _normalized_number(value, unit) in text.lower().replace(" ", "")


def _validate_citations(citations: Any, label: str, allowed_ids: set[str], errors: list[str]) -> list[str]:
    if not isinstance(citations, list):
        errors.append(f"{label} evidence_chunk_ids must be a list")
        return []
    invalid = [citation for citation in citations if citation not in allowed_ids]
    if invalid:
        errors.append(f"{label} cites unavailable chunks: {invalid}")
    return [citation for citation in citations if citation in allowed_ids]


def _validate_parameter(parameter: Any, label: str, allowed_ids: set[str], evidence_by_id: dict[str, str], errors: list[str], warnings: list[str]) -> str | None:
    if not isinstance(parameter, dict):
        errors.append(f"{label} must be an object")
        return None
    missing = REQUIRED_PARAMETER_FIELDS - parameter.keys()
    if missing:
        errors.append(f"{label} is missing fields: " + ", ".join(sorted(missing)))
    basis = parameter.get("basis")
    if basis not in ALLOWED_VALUE_BASIS:
        errors.append(f"{label} has invalid basis")
        return None
    if parameter.get("confidence") not in ALLOWED_CONFIDENCE:
        errors.append(f"{label} has invalid confidence")
    value = parameter.get("value")
    unit = parameter.get("unit")
    citations = _validate_citations(parameter.get("evidence_chunk_ids"), label, allowed_ids, errors)
    cited_text = " ".join(evidence_by_id[citation] for citation in citations)
    if basis == "unresolved":
        if value is not None:
            errors.append(f"{label} must use a null value when basis is unresolved")
        return basis
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        errors.append(f"{label} requires a numeric value")
    if not isinstance(unit, str) or not unit.strip():
        errors.append(f"{label} requires a unit")
    if not citations:
        errors.append(f"{label} requires field-level evidence_chunk_ids")
    if basis == "reported" and isinstance(value, (int, float)) and isinstance(unit, str) and not _evidence_contains(value, unit, cited_text):
        errors.append(f"{label} reported value was not found in its cited evidence")
    if basis == "evidence_informed_transfer":
        source_value = parameter.get("source_value")
        source_unit = parameter.get("source_unit")
        for field in ("source_conditions", "adjustment_rule", "rationale"):
            if not parameter.get(field):
                errors.append(f"{label} requires {field} for evidence-informed transfer")
        if source_value is not None and (not isinstance(source_value, (int, float)) or isinstance(source_value, bool)):
            errors.append(f"{label} source_value must be numeric when supplied")
        if source_value is not None and (not isinstance(source_unit, str) or not source_unit.strip()):
            errors.append(f"{label} requires source_unit when source_value is supplied")
        if isinstance(source_value, (int, float)) and isinstance(source_unit, str) and citations and not _evidence_contains(source_value, source_unit, cited_text):
            warnings.append(f"{label} source value was not found verbatim in its cited evidence; review the transfer rationale")
    if basis == "engineering_judgment":
        if not parameter.get("rationale"):
            errors.append(f"{label} requires a scientific rationale for engineering judgment")
        if parameter.get("confidence") == "high":
            errors.append(f"{label} cannot claim high confidence for engineering judgment")
    return basis


def validate_answer(answer: dict[str, Any], evidence: Sequence[EvidenceChunk]) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    missing = REQUIRED_TOP_LEVEL - answer.keys()
    if missing:
        errors.append("Missing fields: " + ", ".join(sorted(missing)))
    suggestions = answer.get("protocol_suggestions")
    if not isinstance(suggestions, list):
        errors.append("protocol_suggestions must be a list")
        suggestions = []
    elif len(suggestions) > 2:
        errors.append("protocol_suggestions must contain no more than two protocols")
    designations = [s.get("designation") for s in suggestions if isinstance(s, dict)]
    if suggestions and designations.count("primary") != 1:
        errors.append("protocol_suggestions must contain exactly one primary protocol")
    if designations.count("alternative") > 1:
        errors.append("protocol_suggestions may contain at most one alternative protocol")

    allowed_ids = {chunk.chunk_id for chunk in evidence}
    evidence_by_id = {chunk.chunk_id: chunk.text for chunk in evidence}
    for index, suggestion in enumerate(suggestions, start=1):
        label = f"protocol_suggestions[{index}]"
        if not isinstance(suggestion, dict):
            errors.append(f"{label} must be an object")
            continue
        missing_suggestion = REQUIRED_SUGGESTION_FIELDS - suggestion.keys()
        if missing_suggestion:
            errors.append(f"{label} is missing fields: " + ", ".join(sorted(missing_suggestion)))
        if suggestion.get("designation") not in ALLOWED_DESIGNATION:
            errors.append(f"{label} has invalid designation")
        status = suggestion.get("protocol_status")
        if status not in ALLOWED_STATUS:
            errors.append(f"{label} has invalid protocol_status")
        if suggestion.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append(f"{label} has invalid confidence")
        if suggestion.get("reported_or_inferred") not in ALLOWED_ORIGIN:
            errors.append(f"{label} has invalid reported_or_inferred value")
        citations = _validate_citations(suggestion.get("evidence_chunk_ids"), label, allowed_ids, errors)
        if not citations:
            errors.append(f"{label} requires at least one evidence_chunk_id")
        target = suggestion.get("target_conditions")
        if not isinstance(target, dict):
            errors.append(f"{label}.target_conditions must be an object")
        else:
            missing_target = REQUIRED_TARGET_FIELDS - target.keys()
            if missing_target:
                errors.append(f"{label}.target_conditions is missing fields: " + ", ".join(sorted(missing_target)))

        steps = suggestion.get("protocol_steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"{label} requires at least one protocol step")
            steps = []
        unresolved_critical = False
        reasoned_fields = 0
        judgment_fields = 0
        for step_index, step in enumerate(steps, start=1):
            step_label = f"{label}.protocol_steps[{step_index}]"
            if not isinstance(step, dict):
                errors.append(f"{step_label} must be an object")
                continue
            missing_step = REQUIRED_STEP_FIELDS - step.keys()
            if missing_step:
                errors.append(f"{step_label} is missing fields: " + ", ".join(sorted(missing_step)))
            if step.get("stage_number") != step_index:
                errors.append(f"{step_label} stage_number must be {step_index}")
            if step.get("control_mode") not in ALLOWED_CONTROL_MODE:
                errors.append(f"{step_label} has invalid control_mode")
            if not isinstance(step.get("monitoring"), list) or not step.get("monitoring"):
                errors.append(f"{step_label} requires monitoring requirements")
            if not isinstance(step.get("stop_conditions"), list) or not step.get("stop_conditions"):
                errors.append(f"{step_label} requires stop_conditions")
            operational_text = " ".join([str(step.get("start_condition") or "")] + [str(item) for item in step.get("stop_conditions") or []])
            if VAGUE_OPERATIONAL_LANGUAGE.search(operational_text):
                warnings.append(f"{step_label} contains vague operational language")
            for field in ("current", "voltage_limit", "temperature_limit"):
                basis = _validate_parameter(step.get(field), f"{step_label}.{field}", allowed_ids, evidence_by_id, errors, warnings)
                unresolved_critical |= basis == "unresolved"
                reasoned_fields += basis in {"evidence_informed_transfer", "engineering_judgment"}
                judgment_fields += basis == "engineering_judgment"
            transition = step.get("transition")
            transition_basis = _validate_parameter(transition, f"{step_label}.transition", allowed_ids, evidence_by_id, errors, warnings)
            unresolved_critical |= transition_basis == "unresolved"
            reasoned_fields += transition_basis in {"evidence_informed_transfer", "engineering_judgment"}
            judgment_fields += transition_basis == "engineering_judgment"
            if isinstance(transition, dict):
                missing_transition = REQUIRED_TRANSITION_FIELDS - transition.keys()
                if missing_transition:
                    errors.append(f"{step_label}.transition is missing fields: " + ", ".join(sorted(missing_transition)))
                if transition.get("variable") not in ALLOWED_TRANSITION_VARIABLE:
                    errors.append(f"{step_label}.transition has invalid variable")
                if transition.get("operator") not in ALLOWED_OPERATOR:
                    errors.append(f"{step_label}.transition has invalid operator")
        if status in {"experimental_starting_protocol", "literature_transferred_candidate"} and unresolved_critical:
            errors.append(f"{label} cannot be {status} while critical parameters are unresolved")
        if status == "partially_specified" and not unresolved_critical:
            warnings.append(f"{label} is partially_specified but contains no unresolved critical parameters")
        if status == "literature_transferred_candidate" and judgment_fields:
            errors.append(f"{label} must use experimental_starting_protocol when it contains engineering judgment")
        if reasoned_fields and suggestion.get("reported_or_inferred") == "reported":
            errors.append(f"{label} cannot label transferred or judgment-based values as reported")

        extrapolation = suggestion.get("extrapolation")
        extrapolation_used = isinstance(extrapolation, dict) and extrapolation.get("used") is True
        if not isinstance(extrapolation, dict) or not isinstance(extrapolation.get("used"), bool):
            errors.append(f"{label}.extrapolation requires a boolean used field")
        elif extrapolation_used:
            for field in ("source_conditions", "target_conditions", "justification", "key_differences"):
                if not extrapolation.get(field):
                    errors.append(f"{label}.extrapolation requires {field} when used is true")
        if reasoned_fields and not extrapolation_used:
            errors.append(f"{label} uses transferred or judgment-based values without disclosure")
        if extrapolation_used and not reasoned_fields:
            warnings.append(f"{label} discloses reasoning transfer but has no transferred or judgment-based fields")
        validation_plan = suggestion.get("validation_plan")
        if not isinstance(validation_plan, list) or not validation_plan:
            errors.append(f"{label} requires a non-empty validation_plan")

    if errors:
        return ValidationResult("reject", tuple(errors), tuple(warnings))
    if warnings:
        return ValidationResult("pass_with_warnings", (), tuple(warnings))
    return ValidationResult("pass")
