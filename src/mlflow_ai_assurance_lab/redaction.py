"""Trace redaction applied before values cross the persistence boundary."""

from __future__ import annotations

import json
import re
from typing import Any

REDACTION_POLICY_VERSION = "trace-redaction-v1"
REDACTED = "[REDACTED:SYNTHETIC_SENSITIVE]"
SENSITIVE_PATTERNS = (
    re.compile(r"\bSYNTH-SSN-\d{3}-\d{2}-\d{4}\b", re.IGNORECASE),
    re.compile(r"\bSYNTH-SECRET-[A-Z0-9-]+\b", re.IGNORECASE),
    re.compile(r"\bsynthetic\.[a-z0-9._%+-]+@example\.invalid\b", re.IGNORECASE),
)


def contains_sensitive_marker(value: Any) -> bool:
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True)
    return any(pattern.search(text) for pattern in SENSITIVE_PATTERNS)


def redact_text(value: str) -> str:
    redacted = value
    for pattern in SENSITIVE_PATTERNS:
        redacted = pattern.sub(REDACTED, redacted)
    return redacted


def redact(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {str(key): redact(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    return value
