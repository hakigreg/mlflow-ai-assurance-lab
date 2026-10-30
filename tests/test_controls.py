from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, cast

import pytest

from mlflow_ai_assurance_lab.control_catalog import (
    DEFAULT_CONTROL_CATALOG_PATH,
    ControlCatalogError,
    load_control_catalog,
)
from mlflow_ai_assurance_lab.controls import (
    ControlTraceabilityError,
    derive_control_status,
    validate_static_traceability,
)

ROOT = Path(__file__).resolve().parents[1]


def _sample_results() -> dict[str, Any]:
    summary = json.loads((ROOT / "evidence/sample/summary.json").read_text(encoding="utf-8"))
    cases = json.loads((ROOT / "evidence/sample/case-results.json").read_text(encoding="utf-8"))
    summary["variants"] = {
        variant: {**summary["variants"][variant], "cases": cases["variants"][variant]}
        for variant in ("baseline", "governed")
    }
    return cast(dict[str, Any], summary)


def _catalog_payload() -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads(DEFAULT_CONTROL_CATALOG_PATH.read_text(encoding="utf-8")),
    )


def _write_catalog(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_measured_regression_changes_affected_control_and_decision() -> None:
    results = copy.deepcopy(_sample_results())
    governed = results["variants"]["governed"]
    governed["metrics"]["citation_source_match"] = 0.875
    governed["decision"] = "FAIL"
    governed["failed_metrics"] = ["citation_source_match"]
    citation_case = next(item for item in governed["cases"] if item["case_id"] == "CASE-CIT-001")
    citation_case["scores"]["citation_source_match"] = 0.0

    status = derive_control_status(results)
    citation = next(item for item in status["controls"] if item["control_id"] == "CTRL-CITE-001")
    gate = next(item for item in status["controls"] if item["control_id"] == "CTRL-GATE-001")

    assert citation["status"] == "FAIL"
    assert citation["observed_value"] == 0.875
    assert citation["decision"] == "FAIL"
    assert gate["status"] == "FAIL"
    assert gate["observed_value"] == "FAIL"


@pytest.mark.parametrize(
    ("defect", "message"),
    [
        ("unknown_risk", "unknown risk IDs"),
        ("empty_tests", "must be a non-empty list"),
        ("empty_evidence", "must be a non-empty list"),
        ("hardcoded_status", r"extra=\['status'\]"),
    ],
)
def test_control_catalog_rejects_incomplete_or_hardcoded_metadata(
    tmp_path: Path, defect: str, message: str
) -> None:
    payload = _catalog_payload()
    control = payload["controls"][0]
    if defect == "unknown_risk":
        control["risk_ids"] = ["RISK-UNKNOWN-999"]
    elif defect == "empty_tests":
        control["test_refs"] = []
    elif defect == "empty_evidence":
        control["evidence_paths"] = []
    else:
        control["status"] = "PASS"
    path = tmp_path / "invalid-control-catalog.json"
    _write_catalog(path, payload)

    with pytest.raises(ControlCatalogError, match=message):
        load_control_catalog(path)


def test_static_traceability_rejects_orphan_case_anchor() -> None:
    catalog = copy.deepcopy(load_control_catalog())
    scope = next(item for item in catalog["controls"] if item["control_id"] == "CTRL-SCOPE-001")
    scope["observation"]["case_ids"] = ["CASE-UNKNOWN-999"]

    with pytest.raises(ControlTraceabilityError, match="observes unknown case"):
        validate_static_traceability(catalog=catalog)
