"""Narrow, versioned redaction before values cross a persistence boundary."""

from __future__ import annotations

import json
import re
from typing import Any

REDACTION_POLICY_VERSION = "persistence-redaction-v2"
REDACTED = "[REDACTED:SYNTHETIC_SENSITIVE]"
REDACTED_SECRET = "[REDACTED:SECRET_PATTERN]"
REDACTED_PROMPT = "[REDACTED:PROHIBITED_PROMPT]"
SENSITIVE_PATTERNS = (
    re.compile(r"\bSYNTH-SSN-\d{3}-\d{2}-\d{4}\b", re.IGNORECASE),
    re.compile(r"\bSYNTH-SECRET-[A-Z0-9-]+\b", re.IGNORECASE),
    re.compile(r"\bsynthetic\.[a-z0-9._%+-]+@example\.invalid\b", re.IGNORECASE),
)
SECRET_PATTERNS = (
    re.compile(r"\b(?:sk|rk|pk)-(?:test-)?[A-Za-z0-9_-]{16,}\b", re.IGNORECASE),
    re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bapi[_-]?key\s*[:=]\s*[^\s,;]+", re.IGNORECASE),
)
PROHIBITED_PROMPT_PHRASES = (
    "ignore previous",
    "ignore all previous",
    "reveal system prompt",
    "override instructions",
)
PROHIBITED_PROMPT_PATTERNS = tuple(
    re.compile(re.escape(phrase), re.IGNORECASE) for phrase in PROHIBITED_PROMPT_PHRASES
)


class PersistenceRedactionError(ValueError):
    """Raised when content remains unsafe after the configured redaction boundary."""


def _serialized(value: Any) -> str:
    return value if isinstance(value, str) else json.dumps(value, sort_keys=True)


def contains_sensitive_marker(value: Any) -> bool:
    """Check only the configured synthetic markers; this is not general PII detection."""

    text = _serialized(value)
    return any(pattern.search(text) for pattern in SENSITIVE_PATTERNS)


def contains_prohibited_prompt(value: Any) -> bool:
    text = _serialized(value)
    return any(pattern.search(text) for pattern in PROHIBITED_PROMPT_PATTERNS)


def contains_unsafe_persistence_content(value: Any) -> bool:
    """Check configured markers, credential shapes, and prohibited prompt phrases."""

    text = _serialized(value)
    patterns = (*SENSITIVE_PATTERNS, *SECRET_PATTERNS, *PROHIBITED_PROMPT_PATTERNS)
    return any(pattern.search(text) for pattern in patterns)


def redact_text(value: str) -> str:
    redacted = value
    for pattern in SENSITIVE_PATTERNS:
        redacted = pattern.sub(REDACTED, redacted)
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(REDACTED_SECRET, redacted)
    for pattern in PROHIBITED_PROMPT_PATTERNS:
        redacted = pattern.sub(REDACTED_PROMPT, redacted)
    return redacted


def _redact(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {redact_text(str(key)): _redact(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(item) for item in value]
    return value


def assert_safe_for_persistence(value: Any) -> None:
    if contains_unsafe_persistence_content(value):
        raise PersistenceRedactionError(
            f"{REDACTION_POLICY_VERSION} left configured prohibited content before persistence"
        )


def redact_for_persistence(value: Any) -> Any:
    redacted = _redact(value)
    assert_safe_for_persistence(redacted)
    return redacted


def redact(value: Any) -> Any:
    """Backward-compatible name for the persistence redactor."""

    return redact_for_persistence(value)
