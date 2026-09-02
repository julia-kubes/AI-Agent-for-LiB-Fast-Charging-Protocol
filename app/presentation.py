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
