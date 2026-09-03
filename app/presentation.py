"""Shared normalization helpers for rendering model-produced response fields."""

from __future__ import annotations

from typing import Any, Iterable


def text_items(value: Any, fallback: Iterable[str] = ()) -> list[str]:
    """Normalize a string or collection into non-empty display strings.

    Model providers occasionally return a single string for a schema field that is
    normally a list. Treating that string as an iterable produces character-by-
    character output such as ``T; h; e``. Presentation layers use this helper to be
    tolerant of that shape without changing the stored raw model response.
    """

    if value is None:
        items: list[Any] = []
    elif isinstance(value, str):
        items = [value]
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        items = [value]

    normalized = [str(item).strip() for item in items if str(item).strip()]
    return normalized or [str(item) for item in fallback]


def format_parameter(parameter: Any) -> str:
    """Render one structured protocol parameter without narrative filler."""
    if not isinstance(parameter, dict) or parameter.get("value") is None:
        return "Unresolved"
    return (
        f"{parameter['value']} {parameter.get('unit', '')} "
        f"({parameter.get('basis', 'unknown')})"
    )


def format_transition(transition: Any) -> str:
    """Render one structured transition condition."""
    if not isinstance(transition, dict) or transition.get("value") is None:
        return "Unresolved"
    return (
        f"{transition.get('variable', 'value')} {transition.get('operator', '')} "
        f"{transition['value']} {transition.get('unit', '')} "
        f"({transition.get('basis', 'unknown')})"
    )
