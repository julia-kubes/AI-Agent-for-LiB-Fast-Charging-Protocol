"""Shared normalization helpers for answer presentation."""

from __future__ import annotations

from typing import Any


def text_items(value: Any, fallback: list[str] | None = None) -> list[str]:
    """Return a scalar or collection as clean display strings."""
    if value is None:
        return list(fallback or [])
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        items = [value]
    rendered = [str(item).strip() for item in items if str(item).strip()]
    return rendered or list(fallback or [])
