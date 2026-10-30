"""Generate and validate the reviewable measured assurance evidence pack."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

from mlflow_ai_assurance_lab.config import (
    DEFAULT_CORPUS_PATH,
    DEFAULT_DATASET_PATH,
    DEFAULT_POLICY_PATH,
    load_evaluation_records,
)
from mlflow_ai_assurance_lab.control_catalog import DEFAULT_CONTROL_CATALOG_PATH
from mlflow_ai_assurance_lab.controls import (
    ControlTraceabilityError,
    derive_control_status,
    render_control_matrix,
    validate_control_status,
    validate_evidence_references,
)
from mlflow_ai_assurance_lab.evaluation import DEFAULT_RESULTS_PATH, sha256_file
from mlflow_ai_assurance_lab.redaction import contains_unsafe_persistence_content

DEFAULT_EVIDENCE_DIR = Path("artifacts/evidence/latest")
SAMPLE_EVIDENCE_DIR = Path(__file__).resolve().parents[2] / "evidence/sample"
CONTROL_MATRIX_PATH = Path(__file__).resolve().parents[2] / "docs/control-matrix.md"
MACHINE_FILES = ("summary.json", "case-results.json", "control-status.json")


class EvidenceValidationError(ValueError):
    """Raised when evidence is missing, stale, unsafe, or internally inconsistent."""


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise EvidenceValidationError(f"cannot read evidence JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvidenceValidationError(f"evidence JSON root must be an object: {path}")
    return cast(dict[str, Any], value)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _render_report(results: dict[str, Any], control_status: dict[str, Any]) -> str:
    variants = cast(dict[str, dict[str, Any]], results["variants"])
    lines = [
        "# Measured assurance evidence report",
        "",
        "This report is generated from deterministic synthetic cases. It demonstrates a bounded",
        "technical comparison; it does not prove production safety, legal compliance, ISO",
        "conformity, certification, or complete audit readiness.",
        "",
        f"- Dataset digest: `{results['dataset_sha256']}`",
        f"- Release policy: `{results['policy_version']}`",
        f"- Generated at (volatile): `{results['generated_at_utc']}`",
        "",
        "## Observed decisions",
        "",
        "| Variant | Decision | MLflow run (volatile) | Failed metrics |",
        "|---|---|---|---|",
    ]
    for name in ("baseline", "governed"):
        value = variants[name]
        failed = ", ".join(value["failed_metrics"]) or "None"
        lines.append(f"| {name} | {value['decision']} | `{value['run_id']}` | {failed} |")
    lines.extend(
        [
            "",
            "## Aggregate metrics",
            "",
            "| Scorer | Baseline | Governed |",
            "|---|---:|---:|",
        ]
    )
    for scorer in variants["governed"]["metrics"]:
        lines.append(
            f"| {scorer} | {variants['baseline']['metrics'][scorer]:.3f} | "
            f"{variants['governed']['metrics'][scorer]:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Measured control status",
            "",
            "| Control | Governed status | Metric or method | Observed | Threshold | "
            "Baseline status |",
            "|---|---|---|---|---|---|",
        ]
    )
    for control in cast(list[dict[str, Any]], control_status["controls"]):
        baseline = cast(dict[str, Any], control["baseline_observation"])
        metric_or_method = control["metric"] or control["observation_method"]
        observed = json.dumps(control["observed_value"], sort_keys=True, separators=(",", ":"))
        threshold = json.dumps(control["threshold"], sort_keys=True, separators=(",", ":"))
        lines.append(
            f"| {control['control_id']} | {control['status']} | `{metric_or_method}` | "
            f"`{observed}` | `{threshold}` | {baseline['status']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation limits",
            "",
            "`lexical_response_match` checks the expected action, lexical terms, and citation IDs",
            "only. It is not a semantic or factual correctness judgment. All scorers use a small",
            "synthetic dataset, and `synthetic_marker_absence` recognizes only configured marker",
            "patterns. The observed PASS applies only to these versioned cases and thresholds.",
            "",
        ]
    )
    return "\n".join(lines)


def generate_evidence(
    results_path: Path = DEFAULT_RESULTS_PATH,
    output_dir: Path = DEFAULT_EVIDENCE_DIR,
) -> Path:
    results = _json(results_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    variants = cast(dict[str, dict[str, Any]], results["variants"])
    control_status = derive_control_status(results)
    summary = {key: value for key, value in results.items() if key != "variants"}
    summary["variants"] = {
        name: {key: value for key, value in variant.items() if key != "cases"}
        for name, variant in variants.items()
    }
    case_results = {
        "schema_version": "1.0",
        "dataset_sha256": results["dataset_sha256"],
        "variants": {name: variant["cases"] for name, variant in variants.items()},
    }
    _write_json(output_dir / "summary.json", summary)
    _write_json(output_dir / "case-results.json", case_results)
    _write_json(output_dir / "control-status.json", control_status)
    (output_dir / "report.md").write_text(_render_report(results, control_status), encoding="utf-8")
    if output_dir.resolve() == SAMPLE_EVIDENCE_DIR.resolve():
        CONTROL_MATRIX_PATH.write_text(render_control_matrix(control_status), encoding="utf-8")
    files = (*MACHINE_FILES, "report.md")
    manifest = {
        "schema_version": "1.0",
        "evidence_version": "phase2-control-traceability-v1",
        "input_digests": {
            "dataset": sha256_file(DEFAULT_DATASET_PATH),
            "corpus": sha256_file(DEFAULT_CORPUS_PATH),
            "release_policy": sha256_file(DEFAULT_POLICY_PATH),
            "control_catalog": sha256_file(DEFAULT_CONTROL_CATALOG_PATH),
        },
        "files": {name: sha256_file(output_dir / name) for name in files},
        "volatile_fields": [
            "summary.generated_at_utc",
            "summary.variants.*.run_id",
            "summary.variants.*.trace_ids",
            "case-results.variants.*.*.trace_id",
            "control-status.controls.*.mlflow_anchors.*.run_id",
            "control-status.controls.*.mlflow_anchors.*.cases.*.trace_id",
            "report generated timestamp and run IDs",
        ],
    }
    _write_json(output_dir / "manifest.json", manifest)
    validate_evidence(output_dir)
    return output_dir


def validate_evidence(output_dir: Path = DEFAULT_EVIDENCE_DIR) -> None:
    manifest = _json(output_dir / "manifest.json")
    expected_inputs = {
        "dataset": sha256_file(DEFAULT_DATASET_PATH),
        "corpus": sha256_file(DEFAULT_CORPUS_PATH),
        "release_policy": sha256_file(DEFAULT_POLICY_PATH),
        "control_catalog": sha256_file(DEFAULT_CONTROL_CATALOG_PATH),
    }
    if manifest.get("input_digests") != expected_inputs:
        raise EvidenceValidationError("evidence input digests are stale")
    files = cast(dict[str, str], manifest.get("files"))
    for name in (*MACHINE_FILES, "report.md"):
        path = output_dir / name
        if files.get(name) != sha256_file(path):
            raise EvidenceValidationError(f"evidence file hash mismatch: {name}")
        if contains_unsafe_persistence_content(path.read_text(encoding="utf-8")):
            raise EvidenceValidationError(
                f"prohibited persistence content found in evidence: {name}"
            )
    summary = _json(output_dir / "summary.json")
    variants = cast(dict[str, dict[str, Any]], summary["variants"])
    if variants["baseline"]["decision"] != "FAIL":
        raise EvidenceValidationError("sample evidence must preserve the intentional baseline FAIL")
    if variants["governed"]["decision"] != "PASS":
        raise EvidenceValidationError("governed evidence does not meet the release policy")
    cases = _json(output_dir / "case-results.json")
    expected_case_ids = {str(record["inputs"]["case_id"]) for record in load_evaluation_records()}
    for variant in ("baseline", "governed"):
        observed = {str(item["case_id"]) for item in cases["variants"][variant]}
        if observed != expected_case_ids:
            raise EvidenceValidationError(f"case coverage mismatch for {variant}")
    control_status = _json(output_dir / "control-status.json")
    reconstructed = dict(summary)
    reconstructed_variants = {
        variant: {
            **variants[variant],
            "cases": cast(dict[str, Any], cases["variants"])[variant],
        }
        for variant in ("baseline", "governed")
    }
    reconstructed["variants"] = reconstructed_variants
    try:
        validate_control_status(control_status, reconstructed)
        validate_evidence_references(control_status, output_dir)
    except ControlTraceabilityError as exc:
        raise EvidenceValidationError(str(exc)) from exc
    if output_dir.resolve() == SAMPLE_EVIDENCE_DIR.resolve():
        expected_matrix = render_control_matrix(control_status)
        if CONTROL_MATRIX_PATH.read_text(encoding="utf-8") != expected_matrix:
            raise EvidenceValidationError(
                "human control matrix is stale relative to measured machine evidence"
            )


def manifest_digest(output_dir: Path = DEFAULT_EVIDENCE_DIR) -> str:
    return hashlib.sha256((output_dir / "manifest.json").read_bytes()).hexdigest()
