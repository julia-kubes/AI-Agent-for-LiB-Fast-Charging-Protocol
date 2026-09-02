"""Conservative, deterministic scope checks before paid model or retrieval calls."""

from __future__ import annotations

import re
from typing import Mapping


# These terms identify questions that plausibly concern the application's battery
# literature domain. Ambiguous domain-adjacent questions continue to the agent; the
# gate is intended to reject clearly unrelated input, not determine scientific
# relevance.
DOMAIN_PATTERN = re.compile(
    r"(?:"
    r"\bbatter(?:y|ies)\b|"
    r"\blithium(?:[- ]ion)?\b|\bli[- ]?ion\b|"
    r"\bfast[- ]?charg(?:e|ing)\b|\bcharg(?:e|ing) protocol\b|"
    r"\bstate[- ]of[- ]charge\b|\bSOC\b|\bC[- ]?rate\b|\bCC[- ]?CV\b|"
    r"\blithium plating\b|\bgraphite\b|\banode\b|\bcathode\b|"
    r"\belectrolyte\b|\belectrochemical\b|\bNMC\d*\b|\bNCM\d*\b|"
    r"\bLFP\b|\bLiFePO4\b|\bpouch cell\b|\bcylindrical cell\b|"
    r"\bcell chemistry\b|\bcharging current\b|\bcharge current\b|"
    r"\bcharging voltage\b|\bcharge time\b|\bcharging temperature\b"
    r")",
    re.IGNORECASE,
)


def is_out_of_domain(
    question: str, conditions: Mapping[str, str] | None = None
) -> bool:
    """Return True only when no battery-domain signal is present.

    Supplied operating conditions are themselves a strong signal because the UI
    collects only battery-specific fields. This keeps short follow-up-style prompts
    usable when the user provides chemistry, temperature, SOC, or an objective.
    """

    condition_values = [
        str(value).strip() for value in (conditions or {}).values() if str(value).strip()
    ]
    if condition_values:
        return False
    return DOMAIN_PATTERN.search(question) is None


def out_of_domain_answer() -> dict[str, object]:
    """Return a response that conforms to the normal final-answer schema."""

    return {
        "summary": (
            "I'm a literature assistant for lithium-ion battery fast charging. "
            "That question is outside my current scope, so I did not search the "
            "battery-paper database or generate a charging protocol."
        ),
        "protocol_suggestions": [],
        "conflicting_evidence": [],
        "missing_information": [],
        "safety_notes": [],
        "follow_up_questions": [
            "What would you like to investigate about lithium-ion fast charging?"
        ],
    }
