"""Versioned configuration and dataset loading."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, cast

from mlflow_ai_assurance_lab.domain import Decision, PolicyDocument, ReleasePolicy, Variant

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = ROOT / "config/release-policy-v1.json"
DEFAULT_CORPUS_PATH = ROOT / "data/policies/policies-v1.json"
DEFAULT_DATASET_PATH = ROOT / "data/evaluation/policy-assurance-v1.json"

DATASET_SCHEMA_VERSION = "1.1"
DATASET_VERSION = "policy-assurance-v1"
CASE_ID_PATTERN = re.compile(r"^CASE-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3}$")
CATEGORY_ACTIONS = {
    "normal": "answer",
    "invalid_citation": "answer",
    "out_of_scope": "refuse_scope",
    "sensitive_data": "refuse_sensitive",
    "direct_prompt_injection": "refuse_prompt_injection",
    "indirect_prompt_injection": "refuse_prompt_injection",
    "insufficient_support": "refuse_insufficient_support",
}
ALLOWED_RISK_IDS = {
    "RISK-CITE-001",
    "RISK-GROUND-001",
    "RISK-INJECT-001",
    "RISK-LEAK-001",
    "RISK-SCOPE-001",
}
ALLOWED_CONTROL_IDS = {
    "CTRL-CITE-001",
    "CTRL-GROUND-001",
    "CTRL-INJECT-001",
    "CTRL-REDACT-001",
    "CTRL-REFUSE-001",
    "CTRL-SCOPE-001",
    "CTRL-SUPPORT-001",
}
SCORER_NAMES = (
    "citation_source_match",
    "scope_action_match",
    "synthetic_marker_absence",
    "expected_action_match",
    "lexical_response_match",
)


class ConfigurationError(ValueError):
    """Raised when a versioned input is missing or invalid."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigurationError(f"required configuration is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ConfigurationError(f"JSON root must be an object: {path}")
    return cast(dict[str, Any], value)


def load_documents(path: Path = DEFAULT_CORPUS_PATH) -> tuple[PolicyDocument, ...]:
    raw = load_json(path)
    if raw.get("schema_version") != "1.0" or not isinstance(raw.get("documents"), list):
        raise ConfigurationError(f"unsupported policy corpus schema: {path}")
    documents: list[PolicyDocument] = []
    for item in raw["documents"]:
        if not isinstance(item, dict):
            raise ConfigurationError(f"policy document must be an object: {path}")
        documents.append(
            PolicyDocument(
                document_id=str(item["document_id"]),
                title=str(item["title"]),
                topics=tuple(str(topic) for topic in item["topics"]),
                content=str(item["content"]),
                trusted=bool(item.get("trusted", True)),
            )
        )
    if len({document.document_id for document in documents}) != len(documents):
        raise ConfigurationError("policy document IDs must be unique")
    return tuple(documents)


def _object(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigurationError(f"{location} must be an object")
    return cast(dict[str, Any], value)


def _exact_keys(value: dict[str, Any], expected: set[str], location: str) -> None:
    observed = set(value)
    if observed != expected:
        raise ConfigurationError(
            f"{location} fields must be {sorted(expected)}; "
            f"missing={sorted(expected - observed)}, extra={sorted(observed - expected)}"
        )


def _nonempty_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{location} must be a non-empty string")
    return value


def _string_list(value: Any, location: str) -> list[str]:
    if not isinstance(value, list):
        raise ConfigurationError(f"{location} must be a list")
    strings = [_nonempty_string(item, f"{location} item") for item in value]
    if len(strings) != len(set(strings)):
        raise ConfigurationError(f"{location} values must be unique")
    return strings


def _id_list(value: Any, location: str, allowed: set[str]) -> list[str]:
    raw = _nonempty_string(value, location)
    identifiers = [identifier.strip() for identifier in raw.split(",")]
    if any(not identifier for identifier in identifiers):
        raise ConfigurationError(f"{location} must contain comma-separated IDs")
    if len(identifiers) != len(set(identifiers)):
        raise ConfigurationError(f"{location} IDs must be unique")
    unknown = set(identifiers) - allowed
    if unknown:
        raise ConfigurationError(f"{location} contains unsupported IDs: {sorted(unknown)}")
    return identifiers


def load_evaluation_records(
    path: Path = DEFAULT_DATASET_PATH,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
) -> list[dict[str, Any]]:
    raw = load_json(path)
    _exact_keys(raw, {"schema_version", "dataset_version", "records"}, "evaluation dataset")
    if raw.get("schema_version") != DATASET_SCHEMA_VERSION:
        raise ConfigurationError(f"unsupported evaluation dataset schema: {path}")
    if raw.get("dataset_version") != DATASET_VERSION:
        raise ConfigurationError(f"unsupported evaluation dataset version: {path}")
    if not isinstance(raw.get("records"), list):
        raise ConfigurationError(f"evaluation dataset records must be a list: {path}")
    raw_records = cast(list[Any], raw["records"])
    if not raw_records:
        raise ConfigurationError("evaluation dataset must not be empty")

    source_ids = {document.document_id for document in load_documents(corpus_path)}
    records: list[dict[str, Any]] = []
    case_ids: list[str] = []
    queries: list[str] = []
    for index, raw_record in enumerate(raw_records):
        location = f"evaluation record {index}"
        record = _object(raw_record, location)
        _exact_keys(record, {"inputs", "expectations", "tags"}, location)
        inputs = _object(record["inputs"], f"{location}.inputs")
        expectations = _object(record["expectations"], f"{location}.expectations")
        tags = _object(record["tags"], f"{location}.tags")
        _exact_keys(inputs, {"case_id", "query"}, f"{location}.inputs")
        _exact_keys(
            expectations,
            {
                "category",
                "expected_action",
                "expected_citations",
                "expected_terms",
                "rationale",
                "should_refuse",
            },
            f"{location}.expectations",
        )
        _exact_keys(tags, {"risk_ids", "control_ids"}, f"{location}.tags")

        case_id = _nonempty_string(inputs["case_id"], f"{location}.inputs.case_id")
        if CASE_ID_PATTERN.fullmatch(case_id) is None:
            raise ConfigurationError(f"invalid stable case ID: {case_id}")
        query = _nonempty_string(inputs["query"], f"{location}.inputs.query")
        category = _nonempty_string(expectations["category"], f"{location}.expectations.category")
        if category not in CATEGORY_ACTIONS:
            raise ConfigurationError(f"unsupported evaluation category: {category}")
        expected_action = _nonempty_string(
            expectations["expected_action"], f"{location}.expectations.expected_action"
        )
        if expected_action != CATEGORY_ACTIONS[category]:
            raise ConfigurationError(
                f"expected action {expected_action!r} is invalid for category {category!r}"
            )
        should_refuse = expectations["should_refuse"]
        if not isinstance(should_refuse, bool):
            raise ConfigurationError(f"{location}.expectations.should_refuse must be a boolean")
        if should_refuse != (expected_action != "answer"):
            raise ConfigurationError(
                f"should_refuse is inconsistent with expected action for {case_id}"
            )
        expected_citations = _string_list(
            expectations["expected_citations"],
            f"{location}.expectations.expected_citations",
        )
        expected_terms = _string_list(
            expectations["expected_terms"], f"{location}.expectations.expected_terms"
        )
        _nonempty_string(expectations["rationale"], f"{location}.expectations.rationale")
        if should_refuse and (expected_citations or expected_terms):
            raise ConfigurationError(
                f"expected refusal case {case_id} must not require citations or answer terms"
            )
        if not should_refuse and (not expected_citations or not expected_terms):
            raise ConfigurationError(
                f"expected answer case {case_id} requires citations and lexical terms"
            )
        unknown_citations = set(expected_citations) - source_ids
        if unknown_citations:
            raise ConfigurationError(
                f"{case_id} expects citations absent from the corpus: {sorted(unknown_citations)}"
            )
        _id_list(tags["risk_ids"], f"{location}.tags.risk_ids", ALLOWED_RISK_IDS)
        _id_list(tags["control_ids"], f"{location}.tags.control_ids", ALLOWED_CONTROL_IDS)

        case_ids.append(case_id)
        queries.append(query)
        records.append(record)

    if len(case_ids) != len(set(case_ids)):
        raise ConfigurationError("evaluation case IDs must be unique")
    if len(queries) != len(set(queries)):
        raise ConfigurationError("evaluation queries must be unique")
    return records


def load_release_policy(path: Path = DEFAULT_POLICY_PATH) -> ReleasePolicy:
    raw = load_json(path)
    _exact_keys(
        raw,
        {
            "schema_version",
            "policy_version",
            "required_scorers",
            "thresholds",
            "expected_decisions",
            "rationale",
        },
        "release policy",
    )
    try:
        if raw["schema_version"] != "1.0":
            raise ConfigurationError(f"unsupported release policy schema: {path}")
        _nonempty_string(raw["policy_version"], "release policy policy_version")
        _nonempty_string(raw["rationale"], "release policy rationale")
        if not isinstance(raw["required_scorers"], list):
            raise TypeError
        required = tuple(
            _nonempty_string(value, "release policy required scorer")
            for value in raw["required_scorers"]
        )
        if len(required) != len(set(required)):
            raise ConfigurationError("release policy scorers must be unique")
        threshold_values = _object(raw["thresholds"], "release policy thresholds")
        thresholds: dict[str, float] = {}
        for key, value in threshold_values.items():
            if (
                not isinstance(key, str)
                or not isinstance(value, (int, float))
                or isinstance(value, bool)
            ):
                raise TypeError
            thresholds[key] = float(value)
        expected_values = _object(raw["expected_decisions"], "release policy expected_decisions")
        expected = {
            cast(Variant, key): cast(Decision, value) for key, value in expected_values.items()
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigurationError(f"invalid release policy: {path}") from exc
    if required != SCORER_NAMES:
        raise ConfigurationError(
            f"release policy scorer order must be the supported vocabulary: {list(SCORER_NAMES)}"
        )
    if set(required) != set(thresholds):
        raise ConfigurationError("release policy scorers and threshold keys must match")
    if any(not math.isfinite(value) or value < 0.0 or value > 1.0 for value in thresholds.values()):
        raise ConfigurationError(
            "release thresholds must be finite and in the inclusive range [0, 1]"
        )
    if expected != {"baseline": "FAIL", "governed": "PASS"}:
        raise ConfigurationError("Phase 1 expects baseline FAIL and governed PASS")
    return ReleasePolicy(
        schema_version=str(raw["schema_version"]),
        policy_version=str(raw["policy_version"]),
        required_scorers=required,
        thresholds=thresholds,
        expected_decisions=expected,
    )
