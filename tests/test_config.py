from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, cast

import pytest

from mlflow_ai_assurance_lab.config import (
    DEFAULT_DATASET_PATH,
    DEFAULT_POLICY_PATH,
    ConfigurationError,
    load_evaluation_records,
    load_release_policy,
)


def _dataset_payload() -> dict[str, Any]:
    value = json.loads(DEFAULT_DATASET_PATH.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return cast(dict[str, Any], value)


def _write_dataset(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], payload["records"])


def test_versioned_dataset_has_stable_ids_risks_expectations_and_rationales() -> None:
    records = load_evaluation_records()
    assert {record["inputs"]["case_id"] for record in records} == {
        "CASE-CIT-001",
        "CASE-PI-DIRECT-001",
        "CASE-PI-INDIRECT-001",
        "CASE-POS-001",
        "CASE-POS-002",
        "CASE-SCOPE-001",
        "CASE-SENS-001",
        "CASE-SUPPORT-001",
    }
    for record in records:
        assert record["tags"]["risk_ids"]
        assert record["expectations"]["expected_action"]
        assert record["expectations"]["rationale"]


@pytest.mark.parametrize(
    ("defect", "message"),
    [
        ("missing_field", "fields must be"),
        ("wrong_type", "must be a boolean"),
        ("unknown_category", "unsupported evaluation category"),
        ("unknown_control", "unsupported IDs"),
    ],
)
def test_dataset_loader_rejects_invalid_contracts(
    tmp_path: Path, defect: str, message: str
) -> None:
    payload = copy.deepcopy(_dataset_payload())
    first = _records(payload)[0]
    if defect == "missing_field":
        del first["expectations"]["rationale"]
    elif defect == "wrong_type":
        first["expectations"]["should_refuse"] = "false"
    elif defect == "unknown_category":
        first["expectations"]["category"] = "semantic_truth"
    else:
        first["tags"]["control_ids"] = "CTRL-UNKNOWN-999"
    path = tmp_path / "invalid-dataset.json"
    _write_dataset(path, payload)

    with pytest.raises(ConfigurationError, match=message):
        load_evaluation_records(path)


def test_dataset_loader_rejects_duplicate_case_ids(tmp_path: Path) -> None:
    payload = copy.deepcopy(_dataset_payload())
    records = _records(payload)
    records[1]["inputs"]["case_id"] = records[0]["inputs"]["case_id"]
    path = tmp_path / "duplicate-id.json"
    _write_dataset(path, payload)

    with pytest.raises(ConfigurationError, match="case IDs must be unique"):
        load_evaluation_records(path)


def test_dataset_loader_rejects_citation_absent_from_corpus(tmp_path: Path) -> None:
    payload = copy.deepcopy(_dataset_payload())
    _records(payload)[0]["expectations"]["expected_citations"] = ["POL-ABSENT-999"]
    path = tmp_path / "absent-citation.json"
    _write_dataset(path, payload)

    with pytest.raises(ConfigurationError, match="absent from the corpus"):
        load_evaluation_records(path)


def test_release_policy_rejects_non_finite_threshold(tmp_path: Path) -> None:
    payload = json.loads(DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))
    payload["thresholds"]["citation_source_match"] = float("nan")
    path = tmp_path / "invalid-policy.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ConfigurationError, match="thresholds must be finite"):
        load_release_policy(path)
