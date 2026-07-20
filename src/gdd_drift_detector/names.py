"""Name normalization helpers for deterministic matching."""

from __future__ import annotations

import re

_CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_ACRONYM_BOUNDARY = re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])")


def normalize_name(value: str) -> str:
    """Normalize names for deterministic exact matching."""

    return re.sub(r"[^a-z0-9]+", "", value.lower())


def name_tokens(value: str) -> frozenset[str]:
    value = _ACRONYM_BOUNDARY.sub(" ", value)
    value = _CAMEL_BOUNDARY.sub(" ", value)
    return frozenset(
        token for token in re.split(r"[^A-Za-z0-9]+", value.lower()) if token
    )
