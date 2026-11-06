"""Derive and validate measured control status with bidirectional traceability."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, cast

from mlflow_ai_assurance_lab.config import (
    DEFAULT_CORPUS_PATH,
    DEFAULT_DATASET_PATH,
    DEFAULT_POLICY_PATH,
    load_evaluation_records,
    load_release_policy,
)
from mlflow_ai_assurance_lab.control_catalog import (
    DEFAULT_CONTROL_CATALOG_PATH,
    ROOT,
    load_control_catalog,
)
from mlflow_ai_assurance_lab.domain import ReleasePolicy, Variant
from mlflow_ai_assurance_lab.evaluation import sha256_file
from mlflow_ai_assurance_lab.gate import GateInputError, assess_recorded_results

CONTROL_STATUS_SCHEMA_VERSION = "2.0"


class ControlTraceabilityError(ValueError):
    """Raised when a control chain is incomplete, orphaned, or contradictory."""


def _ids(value: Any) -> set[str]:
    if not isinstance(value, str):
        raise ControlTraceabilityError("dataset traceability tags must be comma-separated strings")
    return {item.strip() for item in value.split(",") if item.strip()}


def _validate_json_anchor(path: Path, anchor: str, reference: str) -> None:
    try:
        current: Any = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise ControlTraceabilityError(
            f"cannot resolve configuration reference {reference}"
        ) from exc
    for token in anchor.split("."):
        if not isinstance(current, dict) or token not in current:
            raise ControlTraceabilityError(f"unknown configuration anchor: {reference}")
        current = current[token]


def _validate_repository_reference(reference: str, *, test: bool = False) -> None:
    if "::" in reference:
        relative, symbol = reference.split("::", 1)
        path = ROOT / relative
        if not path.is_file() or not symbol:
            raise ControlTraceabilityError(f"unknown repository reference: {reference}")
        if test and not relative.startswith("tests/"):
            raise ControlTraceabilityError(f"control test must reference tests/: {reference}")
        name = symbol.rsplit(".", 1)[-1]
        pattern = re.compile(rf"\b(?:def|class)\s+{re.escape(name)}\b")
        if pattern.search(path.read_text(encoding="utf-8")) is None:
            raise ControlTraceabilityError(f"unknown symbol in repository reference: {reference}")
        return
    relative, separator, anchor = reference.partition("#")
    path = ROOT / relative
    if not path.is_file():
        raise ControlTraceabilityError(f"unknown repository reference: {reference}")
    if separator:
        if not anchor:
            raise ControlTraceabilityError(f"empty repository anchor: {reference}")
        _validate_json_anchor(path, anchor, reference)


def validate_static_traceability(
    catalog: dict[str, Any] | None = None,
    records: list[dict[str, Any]] | None = None,
    policy: ReleasePolicy | None = None,
) -> None:
    """Reject unknown and orphaned risk, control, code, test, case, and metric references."""

    catalog = catalog or load_control_catalog()
    records = records or load_evaluation_records()
    policy = policy or load_release_policy()
    controls = cast(list[dict[str, Any]], catalog["controls"])
    controls_by_id = {str(item["control_id"]): item for item in controls}
    known_risks = set(cast(list[str], catalog["risk_ids"]))
    case_records = {str(item["inputs"]["case_id"]): item for item in records}

    observed_metrics = set(cast(list[str], catalog["observed_metrics"]))
    if observed_metrics != set(policy.required_scorers):
        raise ControlTraceabilityError(
            "release-policy metrics and measured-control observers differ: "
            f"missing={sorted(set(policy.required_scorers) - observed_metrics)}, "
            f"extra={sorted(observed_metrics - set(policy.required_scorers))}"
        )

    dataset_risks: set[str] = set()
    dataset_controls: set[str] = set()
    for case_id, record in case_records.items():
        risk_ids = _ids(record["tags"]["risk_ids"])
        control_ids = _ids(record["tags"]["control_ids"])
        unknown_risks = risk_ids - known_risks
        unknown_controls = control_ids - set(controls_by_id)
        if unknown_risks or unknown_controls:
            raise ControlTraceabilityError(
                f"{case_id} has unknown traceability references: "
                f"risks={sorted(unknown_risks)}, controls={sorted(unknown_controls)}"
            )
        for control_id in control_ids:
            control_risks = set(cast(list[str], controls_by_id[control_id]["risk_ids"]))
            if not risk_ids & control_risks:
                raise ControlTraceabilityError(
                    f"{case_id} links {control_id} without a shared risk ID"
                )
        dataset_risks.update(risk_ids)
        dataset_controls.update(control_ids)

    if not dataset_risks <= known_risks or not dataset_controls <= set(controls_by_id):
        raise ControlTraceabilityError("dataset contains orphan traceability references")

    for control in controls:
        control_id = str(control["control_id"])
        for reference in cast(list[str], control["implementation_refs"]):
            _validate_repository_reference(reference)
        for reference in cast(list[str], control["test_refs"]):
            _validate_repository_reference(reference, test=True)
        observation = cast(dict[str, Any], control["observation"])
        metric = observation.get("metric")
        if metric is not None and metric not in policy.required_scorers:
            raise ControlTraceabilityError(f"{control_id} observes unknown metric {metric!r}")
        for case_id in cast(list[str], observation.get("case_ids", [])):
            if case_id not in case_records:
                raise ControlTraceabilityError(f"{control_id} observes unknown case {case_id}")
            tagged_controls = _ids(case_records[case_id]["tags"]["control_ids"])
            if control_id not in tagged_controls:
                raise ControlTraceabilityError(
                    f"{control_id} case anchor {case_id} does not link back to the control"
                )


def _variants(results: dict[str, Any]) -> dict[str, dict[str, Any]]:
    value = results.get("variants")
    if not isinstance(value, dict) or set(value) != {"baseline", "governed"}:
        raise ControlTraceabilityError(
            "results must contain exactly baseline and governed variants"
        )
    if not all(isinstance(item, dict) for item in value.values()):
        raise ControlTraceabilityError("variant results must be objects")
    return cast(dict[str, dict[str, Any]], value)


def _case_map(variant_result: dict[str, Any], variant: str) -> dict[str, dict[str, Any]]:
    raw_cases = variant_result.get("cases")
    if not isinstance(raw_cases, list):
        raise ControlTraceabilityError(f"{variant} results must contain per-case evidence")
    cases: dict[str, dict[str, Any]] = {}
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict) or not isinstance(raw_case.get("case_id"), str):
            raise ControlTraceabilityError(f"{variant} contains an invalid case result")
        case = cast(dict[str, Any], raw_case)
        case_id = str(case["case_id"])
        if case_id in cases:
            raise ControlTraceabilityError(f"{variant} contains duplicate case {case_id}")
        cases[case_id] = case
    return cases


def _validate_results(results: dict[str, Any], policy: ReleasePolicy) -> None:
    expected_digests = {
        "dataset_sha256": sha256_file(DEFAULT_DATASET_PATH),
        "corpus_sha256": sha256_file(DEFAULT_CORPUS_PATH),
        "release_policy_sha256": sha256_file(DEFAULT_POLICY_PATH),
        "control_catalog_sha256": sha256_file(DEFAULT_CONTROL_CATALOG_PATH),
    }
    for key, expected in expected_digests.items():
        if results.get(key) != expected:
            raise ControlTraceabilityError(f"results have stale or missing {key}")
    if results.get("control_catalog_version") != load_control_catalog()["catalog_version"]:
        raise ControlTraceabilityError("results use an unexpected control catalog version")

    variants = _variants(results)
    expected_cases = {str(item["inputs"]["case_id"]) for item in load_evaluation_records()}
    for variant in ("baseline", "governed"):
        try:
            assess_recorded_results(
                results,
                variant,
                policy,
                expected_digests["release_policy_sha256"],
            )
        except GateInputError as exc:
            raise ControlTraceabilityError(
                f"{variant} decision cannot be recomputed: {exc}"
            ) from exc
        cases = _case_map(variants[variant], variant)
        if set(cases) != expected_cases:
            raise ControlTraceabilityError(
                f"{variant} case coverage mismatch: "
                f"missing={sorted(expected_cases - set(cases))}, "
                f"extra={sorted(set(cases) - expected_cases)}"
            )
        trace_ids = variants[variant].get("trace_ids")
        if not isinstance(trace_ids, list) or not all(
            isinstance(trace_id, str) and trace_id for trace_id in trace_ids
        ):
            raise ControlTraceabilityError(f"{variant} trace IDs must be non-empty strings")
        case_trace_ids = [str(item.get("trace_id", "")) for item in cases.values()]
        if set(trace_ids) != set(case_trace_ids) or len(trace_ids) != len(set(trace_ids)):
            raise ControlTraceabilityError(f"{variant} case-to-trace coverage is inconsistent")
        if variants[variant].get("persistence_safe") is not True:
            raise ControlTraceabilityError(f"{variant} lacks a successful persistence assertion")


def _status(satisfied: bool) -> str:
    return "PASS" if satisfied else "FAIL"


def _selected_case_ids(control: dict[str, Any], cases: dict[str, dict[str, Any]]) -> list[str]:
    observation = cast(dict[str, Any], control["observation"])
    configured = observation.get("case_ids")
    if isinstance(configured, list):
        return cast(list[str], configured)
    if observation["method"] in {"aggregate_metric", "trace_coverage"}:
        return sorted(cases)
    return []


def _variant_anchor(
    control: dict[str, Any], variant_result: dict[str, Any], cases: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    return {
        "run_id": variant_result["run_id"],
        "cases": [
            {"case_id": case_id, "trace_id": cases[case_id]["trace_id"]}
            for case_id in _selected_case_ids(control, cases)
        ],
    }


def _observe_variant(
    control: dict[str, Any],
    variant: Variant,
    variant_result: dict[str, Any],
    cases: dict[str, dict[str, Any]],
    policy: ReleasePolicy,
) -> tuple[Any, Any, str | None, str]:
    observation = cast(dict[str, Any], control["observation"])
    method = str(observation["method"])
    metric = cast(str | None, observation.get("metric"))
    if method == "aggregate_metric":
        assert metric is not None
        metric_value = variant_result["metrics"][metric]
        metric_threshold = policy.thresholds[metric]
        return metric_value, metric_threshold, metric, _status(metric_value >= metric_threshold)
    if method in {"case_metric", "case_metric_and_persistence"}:
        assert metric is not None
        case_ids = cast(list[str], observation["case_ids"])
        case_scores = {case_id: cases[case_id]["scores"][metric] for case_id in case_ids}
        case_threshold = policy.thresholds[metric]
        minimum = min(case_scores.values())
        case_observation: dict[str, Any] = {
            "case_scores": case_scores,
            "minimum_case_score": minimum,
        }
        satisfied = minimum >= case_threshold
        if method == "case_metric_and_persistence":
            case_observation["persistence_safe"] = variant_result["persistence_safe"]
            satisfied = satisfied and variant_result["persistence_safe"] is True
        return case_observation, case_threshold, metric, _status(satisfied)
    if method == "trace_coverage":
        trace_ids = cast(list[str], variant_result["trace_ids"])
        trace_observation = {
            "case_count": len(cases),
            "trace_count": len(trace_ids),
            "unique_trace_count": len(set(trace_ids)),
            "persistence_safe": variant_result["persistence_safe"],
        }
        trace_threshold = {
            "complete_case_to_trace_coverage": True,
            "persistence_safe": True,
        }
        satisfied = (
            trace_observation["case_count"]
            == trace_observation["trace_count"]
            == trace_observation["unique_trace_count"]
            and trace_observation["persistence_safe"] is True
        )
        return trace_observation, trace_threshold, None, _status(satisfied)
    if method == "release_decision":
        observed_decision = variant_result["decision"]
        expected_decision = policy.expected_decisions[variant]
        return (
            observed_decision,
            expected_decision,
            None,
            _status(observed_decision == expected_decision),
        )
    if method == "evidence_preconditions":
        evidence_observation = {
            "current_input_digests": True,
            "complete_case_coverage": True,
            "recomputed_decision_matches": True,
        }
        evidence_threshold = {key: True for key in evidence_observation}
        return (
            evidence_observation,
            evidence_threshold,
            None,
            _status(all(evidence_observation.values())),
        )
    raise ControlTraceabilityError(f"unsupported observation method: {method}")


def derive_control_status(results: dict[str, Any]) -> dict[str, Any]:
    """Compute every material control status from recorded results and versioned configuration."""

    catalog = load_control_catalog()
    policy = load_release_policy()
    records = load_evaluation_records()
    validate_static_traceability(catalog, records, policy)
    _validate_results(results, policy)
    variants = _variants(results)
    case_maps = {
        variant: _case_map(variants[variant], variant) for variant in ("baseline", "governed")
    }
    controls: list[dict[str, Any]] = []
    for static in cast(list[dict[str, Any]], catalog["controls"]):
        baseline_value, baseline_threshold, baseline_metric, baseline_status = _observe_variant(
            static, "baseline", variants["baseline"], case_maps["baseline"], policy
        )
        governed_value, governed_threshold, governed_metric, governed_status = _observe_variant(
            static, "governed", variants["governed"], case_maps["governed"], policy
        )
        method = static["observation"]["method"]
        if baseline_metric != governed_metric or (
            method != "release_decision" and baseline_threshold != governed_threshold
        ):
            raise ControlTraceabilityError(
                f"{static['control_id']} produced inconsistent observation semantics"
            )
        controls.append(
            {
                "control_id": static["control_id"],
                "risk_ids": static["risk_ids"],
                "intent": static["intent"],
                "implementation_refs": static["implementation_refs"],
                "test_refs": static["test_refs"],
                "observation_method": static["observation"]["method"],
                "metric": governed_metric,
                "observed_value": governed_value,
                "threshold": governed_threshold,
                "status": governed_status,
                "decision": variants["governed"]["decision"],
                "baseline_observation": {
                    "metric": baseline_metric,
                    "observed_value": baseline_value,
                    "threshold": baseline_threshold,
                    "status": baseline_status,
                    "decision": variants["baseline"]["decision"],
                    "interpretation": (
                        "The baseline is independently observed and is excluded from the "
                        "governed release decision."
                    ),
                },
                "mlflow_anchors": {
                    "baseline": _variant_anchor(
                        static, variants["baseline"], case_maps["baseline"]
                    ),
                    "governed": _variant_anchor(
                        static, variants["governed"], case_maps["governed"]
                    ),
                },
                "evidence_paths": static["evidence_paths"],
                "release_decision_contribution": static["release_decision_contribution"],
                "residual_risk": static["residual_risk"],
            }
        )
    return {
        "schema_version": CONTROL_STATUS_SCHEMA_VERSION,
        "catalog_version": catalog["catalog_version"],
        "control_catalog_sha256": sha256_file(DEFAULT_CONTROL_CATALOG_PATH),
        "baseline_decision": variants["baseline"]["decision"],
        "decision": variants["governed"]["decision"],
        "controls": controls,
    }


def validate_control_status(status: dict[str, Any], results: dict[str, Any]) -> None:
    expected = derive_control_status(results)
    if status != expected:
        raise ControlTraceabilityError(
            "control status contradicts measured results or versioned static metadata"
        )


def _resolve_evidence_anchor(value: Any, tokens: list[str], reference: str) -> Any:
    current = value
    for token in tokens:
        if isinstance(current, dict) and token in current:
            current = current[token]
            continue
        if isinstance(current, list):
            key = "control_id" if token.startswith("CTRL-") else "case_id"
            matches = [
                item for item in current if isinstance(item, dict) and item.get(key) == token
            ]
            if len(matches) == 1:
                current = matches[0]
                continue
        raise ControlTraceabilityError(f"unknown evidence anchor: {reference}")
    return current


def validate_evidence_references(status: dict[str, Any], output_dir: Path) -> None:
    for control in cast(list[dict[str, Any]], status.get("controls", [])):
        paths = control.get("evidence_paths")
        if not isinstance(paths, list) or not paths:
            raise ControlTraceabilityError(
                f"{control.get('control_id', '<unknown>')} has no evidence path"
            )
        for reference in paths:
            if not isinstance(reference, str) or not reference:
                raise ControlTraceabilityError("control evidence references must be non-empty")
            relative, separator, anchor = reference.partition("#")
            path = output_dir / relative
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (FileNotFoundError, json.JSONDecodeError) as exc:
                raise ControlTraceabilityError(
                    f"cannot resolve evidence reference: {reference}"
                ) from exc
            if not separator or not anchor:
                raise ControlTraceabilityError(
                    f"evidence reference needs a stable anchor: {reference}"
                )
            _resolve_evidence_anchor(value, anchor.split("."), reference)


def _display(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


def _refs(values: list[str]) -> str:
    return "<br>".join(f"`{value}`" for value in values)


def _anchor_summary(control: dict[str, Any]) -> str:
    governed = cast(dict[str, Any], control["mlflow_anchors"])["governed"]
    cases = cast(list[dict[str, str]], governed["cases"])
    if cases and len(cases) <= 2:
        case_text = "<br>".join(f"`{item['case_id']}` → `{item['trace_id']}`" for item in cases)
    elif cases:
        case_text = f"{len(cases)} case/trace anchors in `control-status.json`"
    else:
        case_text = "Decision/evidence-level observation"
    return f"run `{governed['run_id']}`<br>{case_text}"


def render_control_matrix(status: dict[str, Any]) -> str:
    """Render the human matrix from the same derived rows used by machine evidence."""

    controls = cast(list[dict[str, Any]], status["controls"])
    lines = [
        "# Control matrix",
        "",
        "This file is generated from `config/control-catalog-v1.json` and the committed measured",
        "sample in `evidence/sample/`. Edit the catalog or regenerate evidence; do not hand-edit",
        "material results. `PASS` is the governed observation only. Baseline observations remain",
        "separate and do not contribute to the governed release decision.",
        "",
        f"- Catalog: `{status['catalog_version']}`",
        f"- Governed decision: `{status['decision']}`",
        f"- Baseline decision: `{status['baseline_decision']}` (intentional comparison gap)",
        "",
        "| Control | Risks | Intent | Implementation/config | Tests | MLflow run/trace or case "
        "anchor | Result, metric, observed, threshold | Evidence | Release-decision contribution "
        "| Residual risk |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for control in controls:
        metric = control["metric"] or "non-metric"
        governed = (
            f"Governed **{control['status']}**; `{metric}`; observed "
            f"`{_display(control['observed_value'])}`; threshold "
            f"`{_display(control['threshold'])}`"
        )
        baseline = cast(dict[str, Any], control["baseline_observation"])
        status_cell = (
            f"{governed}<br>Baseline control result **{baseline['status']}**; "
            f"observed `{_display(baseline['observed_value'])}`; decision "
            f"`{baseline['decision']}`"
        )
        contribution = cast(dict[str, str], control["release_decision_contribution"])
        lines.append(
            "| "
            + " | ".join(
                [
                    str(control["control_id"]),
                    ", ".join(cast(list[str], control["risk_ids"])),
                    str(control["intent"]),
                    _refs(cast(list[str], control["implementation_refs"])),
                    _refs(cast(list[str], control["test_refs"])),
                    _anchor_summary(control),
                    status_cell,
                    _refs(cast(list[str], control["evidence_paths"])),
                    f"`{contribution['kind']}` — {contribution['detail']}",
                    str(control["residual_risk"]),
                ]
            )
            + " |"
        )
    sample = next(item for item in controls if item["control_id"] == "CTRL-CITE-001")
    sample_anchor = cast(dict[str, Any], sample["mlflow_anchors"])["governed"]
    sample_case = next(item for item in sample_anchor["cases"] if item["case_id"] == "CASE-CIT-001")
    lines.extend(
        [
            "",
            "## Complete chain example — CTRL-CITE-001",
            "",
            "`RISK-CITE-001` / `RISK-GROUND-001` → `CTRL-CITE-001` →",
            "`src/mlflow_ai_assurance_lab/scorers.py::citation_source_match` plus",
            "`config/release-policy-v1.json#thresholds.citation_source_match` →",
            "`tests/test_scorers.py::"
            "test_citation_source_match_accepts_only_expected_retrieved_ids` →",
            f"`CASE-CIT-001` / run `{sample_anchor['run_id']}` / trace "
            f"`{sample_case['trace_id']}` →",
            "`summary.json#variants.governed.metrics.citation_source_match` and",
            "`case-results.json#variants.governed.CASE-CIT-001` → governed release decision →",
            f"residual risk: {sample['residual_risk']}",
            "",
            "Machine-readable rows are in",
            "[`../evidence/sample/control-status.json`](../evidence/sample/control-status.json).",
            "Schema, provenance, validation, and material-comparison semantics are documented in",
            "[`evidence-provenance.md`](evidence-provenance.md).",
            "",
        ]
    )
    return "\n".join(lines)


def control_catalog_digest() -> str:
    return hashlib.sha256(DEFAULT_CONTROL_CATALOG_PATH.read_bytes()).hexdigest()
