"""Versioned configuration and dataset loading."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from mlflow_ai_assurance_lab.domain import Decision, PolicyDocument, ReleasePolicy, Variant

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = ROOT / "config/release-policy-v1.json"
DEFAULT_CORPUS_PATH = ROOT / "data/policies/policies-v1.json"
DEFAULT_DATASET_PATH = ROOT / "data/evaluation/policy-assurance-v1.json"


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


def load_evaluation_records(path: Path = DEFAULT_DATASET_PATH) -> list[dict[str, Any]]:
    raw = load_json(path)
    if raw.get("schema_version") != "1.0" or not isinstance(raw.get("records"), list):
        raise ConfigurationError(f"unsupported evaluation dataset schema: {path}")
    records = cast(list[dict[str, Any]], raw["records"])
    case_ids = [str(record["inputs"]["case_id"]) for record in records]
    if len(case_ids) != len(set(case_ids)):
        raise ConfigurationError("evaluation case IDs must be unique")
    if not records:
        raise ConfigurationError("evaluation dataset must not be empty")
    return records


def load_release_policy(path: Path = DEFAULT_POLICY_PATH) -> ReleasePolicy:
    raw = load_json(path)
    try:
        thresholds = {str(key): float(value) for key, value in raw["thresholds"].items()}
        expected = {
            cast(Variant, key): cast(Decision, value)
            for key, value in raw["expected_decisions"].items()
        }
        required = tuple(str(value) for value in raw["required_scorers"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigurationError(f"invalid release policy: {path}") from exc
    if set(required) != set(thresholds):
        raise ConfigurationError("release policy scorers and threshold keys must match")
    if any(value < 0.0 or value > 1.0 for value in thresholds.values()):
        raise ConfigurationError("release thresholds must be in the inclusive range [0, 1]")
    if expected != {"baseline": "FAIL", "governed": "PASS"}:
        raise ConfigurationError("Phase 1 expects baseline FAIL and governed PASS")
    return ReleasePolicy(
        schema_version=str(raw["schema_version"]),
        policy_version=str(raw["policy_version"]),
        required_scorers=required,
        thresholds=thresholds,
        expected_decisions=expected,
    )
