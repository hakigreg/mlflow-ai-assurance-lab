"""Versioned static metadata for the measured control traceability chain."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTROL_CATALOG_PATH = ROOT / "config/control-catalog-v1.json"

RISK_ID_PATTERN = re.compile(r"^RISK-[A-Z]+-\d{3}$")
CONTROL_ID_PATTERN = re.compile(r"^CTRL-[A-Z]+-\d{3}$")
OBSERVATION_METHODS = {
    "aggregate_metric",
    "case_metric",
    "case_metric_and_persistence",
    "evidence_preconditions",
    "release_decision",
    "trace_coverage",
}


class ControlCatalogError(ValueError):
    """Raised when static control metadata is incomplete or inconsistent."""


def _exact_keys(value: dict[str, Any], expected: set[str], location: str) -> None:
    observed = set(value)
    if observed != expected:
        raise ControlCatalogError(
            f"{location} fields must be {sorted(expected)}; "
            f"missing={sorted(expected - observed)}, extra={sorted(observed - expected)}"
        )


def _object(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ControlCatalogError(f"{location} must be an object")
    return cast(dict[str, Any], value)


def _string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ControlCatalogError(f"{location} must be a non-empty string")
    return value


def _strings(value: Any, location: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ControlCatalogError(f"{location} must be a non-empty list")
    result = [_string(item, f"{location} item") for item in value]
    if len(result) != len(set(result)):
        raise ControlCatalogError(f"{location} values must be unique")
    return result


def load_control_catalog(
    path: Path = DEFAULT_CONTROL_CATALOG_PATH,
) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ControlCatalogError(f"required control catalog is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ControlCatalogError(f"invalid JSON in control catalog {path}: {exc}") from exc
    catalog = _object(raw, "control catalog")
    _exact_keys(
        catalog,
        {"schema_version", "catalog_version", "risk_ids", "controls"},
        "control catalog",
    )
    if catalog["schema_version"] != "1.0":
        raise ControlCatalogError("unsupported control catalog schema_version")
    _string(catalog["catalog_version"], "control catalog catalog_version")
    risk_ids = _strings(catalog["risk_ids"], "control catalog risk_ids")
    if any(RISK_ID_PATTERN.fullmatch(risk_id) is None for risk_id in risk_ids):
        raise ControlCatalogError("control catalog contains an invalid risk ID")
    if not isinstance(catalog["controls"], list) or not catalog["controls"]:
        raise ControlCatalogError("control catalog controls must be a non-empty list")

    controls: list[dict[str, Any]] = []
    control_ids: list[str] = []
    observed_risks: set[str] = set()
    observed_metrics: set[str] = set()
    for index, raw_control in enumerate(catalog["controls"]):
        location = f"control catalog controls[{index}]"
        control = _object(raw_control, location)
        _exact_keys(
            control,
            {
                "control_id",
                "risk_ids",
                "intent",
                "implementation_refs",
                "test_refs",
                "evidence_paths",
                "observation",
                "release_decision_contribution",
                "residual_risk",
            },
            location,
        )
        control_id = _string(control["control_id"], f"{location}.control_id")
        if CONTROL_ID_PATTERN.fullmatch(control_id) is None:
            raise ControlCatalogError(f"invalid control ID: {control_id}")
        control_ids.append(control_id)
        control_risks = _strings(control["risk_ids"], f"{location}.risk_ids")
        unknown_risks = set(control_risks) - set(risk_ids)
        if unknown_risks:
            raise ControlCatalogError(
                f"{control_id} references unknown risk IDs: {sorted(unknown_risks)}"
            )
        observed_risks.update(control_risks)
        _string(control["intent"], f"{location}.intent")
        _strings(control["implementation_refs"], f"{location}.implementation_refs")
        _strings(control["test_refs"], f"{location}.test_refs")
        _strings(control["evidence_paths"], f"{location}.evidence_paths")
        _string(control["residual_risk"], f"{location}.residual_risk")

        observation = _object(control["observation"], f"{location}.observation")
        method = _string(observation.get("method"), f"{location}.observation.method")
        if method not in OBSERVATION_METHODS:
            raise ControlCatalogError(f"unsupported observation method: {method}")
        if method in {"aggregate_metric"}:
            _exact_keys(observation, {"method", "metric"}, f"{location}.observation")
        elif method in {"case_metric", "case_metric_and_persistence"}:
            _exact_keys(
                observation,
                {"method", "metric", "case_ids"},
                f"{location}.observation",
            )
            _strings(observation["case_ids"], f"{location}.observation.case_ids")
        else:
            _exact_keys(observation, {"method"}, f"{location}.observation")
        if "metric" in observation:
            observed_metrics.add(_string(observation["metric"], f"{location}.observation.metric"))

        contribution = _object(
            control["release_decision_contribution"],
            f"{location}.release_decision_contribution",
        )
        _exact_keys(contribution, {"kind", "detail"}, f"{location}.release_decision_contribution")
        _string(contribution["kind"], f"{location}.release_decision_contribution.kind")
        _string(contribution["detail"], f"{location}.release_decision_contribution.detail")
        controls.append(control)

    if len(control_ids) != len(set(control_ids)):
        raise ControlCatalogError("control catalog control IDs must be unique")
    missing_risks = set(risk_ids) - observed_risks
    if missing_risks:
        raise ControlCatalogError(f"material risks lack controls: {sorted(missing_risks)}")
    catalog["controls"] = controls
    catalog["observed_metrics"] = sorted(observed_metrics)
    return catalog


def catalog_risk_ids(path: Path = DEFAULT_CONTROL_CATALOG_PATH) -> set[str]:
    return set(cast(list[str], load_control_catalog(path)["risk_ids"]))


def catalog_control_ids(path: Path = DEFAULT_CONTROL_CATALOG_PATH) -> set[str]:
    catalog = load_control_catalog(path)
    return {str(item["control_id"]) for item in catalog["controls"]}
