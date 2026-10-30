"""Generate and validate the reviewable Phase 1 evidence pack."""

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
from mlflow_ai_assurance_lab.evaluation import DEFAULT_RESULTS_PATH, sha256_file
from mlflow_ai_assurance_lab.redaction import contains_sensitive_marker

DEFAULT_EVIDENCE_DIR = Path("artifacts/evidence/latest")
MACHINE_FILES = ("summary.json", "case-results.json", "control-status.json")

CONTROL_STATUS = (
    {
        "control_id": "CTRL-TRACE-001",
        "risk_ids": ["RISK-TRACE-001", "RISK-LEAK-001"],
        "implementation": "application.PolicyAssistant.ask",
        "test": "tests/test_tracing.py::test_sensitive_marker_is_not_persisted_in_trace",
        "evidence": "summary.json#variants",
        "status": "PASS",
    },
    {
        "control_id": "CTRL-CITE-001",
        "risk_ids": ["RISK-CITE-001", "RISK-GROUND-001"],
        "implementation": "scorers.citation_source_match",
        "test": (
            "tests/test_scorers.py::test_citation_source_match_accepts_only_expected_retrieved_ids"
        ),
        "evidence": "summary.json#variants.governed.metrics.citation_source_match",
        "status": "PASS",
    },
    {
        "control_id": "CTRL-SCOPE-001",
        "risk_ids": ["RISK-SCOPE-001"],
        "implementation": "application.PolicyAssistant._governed_decision",
        "test": "tests/test_application.py::test_governed_actions_match_dataset",
        "evidence": "case-results.json#CASE-SCOPE-001",
        "status": "PASS",
    },
    {
        "control_id": "CTRL-REDACT-001",
        "risk_ids": ["RISK-LEAK-001"],
        "implementation": "redaction.redact",
        "test": "tests/test_tracing.py::test_sensitive_marker_is_not_persisted_in_trace",
        "evidence": "case-results.json#CASE-SENS-001",
        "status": "PASS",
    },
    {
        "control_id": "CTRL-INJECT-001",
        "risk_ids": ["RISK-INJECT-001"],
        "implementation": "application.PolicyAssistant._has_injection",
        "test": "tests/test_application.py::test_governed_actions_match_dataset",
        "evidence": "case-results.json#CASE-PI-DIRECT-001",
        "status": "PASS",
    },
    {
        "control_id": "CTRL-SUPPORT-001",
        "risk_ids": ["RISK-GROUND-001"],
        "implementation": "application.PolicyAssistant._governed_decision",
        "test": "tests/test_application.py::test_governed_actions_match_dataset",
        "evidence": "case-results.json#CASE-SUPPORT-001",
        "status": "PASS",
    },
    {
        "control_id": "CTRL-REFUSE-001",
        "risk_ids": ["RISK-INJECT-001", "RISK-LEAK-001", "RISK-GROUND-001"],
        "implementation": "scorers.expected_action_match",
        "test": (
            "tests/test_scorers.py::"
            "test_expected_action_match_detects_wrong_refusal_and_over_refusal"
        ),
        "evidence": "summary.json#variants.governed.metrics.expected_action_match",
        "status": "PASS",
    },
    {
        "control_id": "CTRL-GROUND-001",
        "risk_ids": ["RISK-GROUND-001"],
        "implementation": "scorers.lexical_response_match",
        "test": (
            "tests/test_scorers.py::"
            "test_lexical_response_match_accepts_only_complete_answer_criteria"
        ),
        "evidence": "summary.json#variants.governed.metrics.lexical_response_match",
        "status": "PASS",
    },
    {
        "control_id": "CTRL-GATE-001",
        "risk_ids": ["RISK-RELEASE-001"],
        "implementation": "gate.decide",
        "test": "tests/test_gate.py::test_regression_makes_gate_fail",
        "evidence": "summary.json#variants.governed.decision",
        "status": "PASS",
    },
    {
        "control_id": "CTRL-EVID-001",
        "risk_ids": ["RISK-TRACE-001", "RISK-RELEASE-001"],
        "implementation": "evidence.validate_evidence",
        "test": "tests/test_evidence.py::test_tampered_evidence_is_rejected",
        "evidence": "manifest.json#files",
        "status": "PASS",
    },
)


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


def _render_report(results: dict[str, Any]) -> str:
    variants = cast(dict[str, dict[str, Any]], results["variants"])
    lines = [
        "# Phase 1 assurance evidence report",
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
    control_status = {
        "schema_version": "1.0",
        "decision": variants["governed"]["decision"],
        "controls": CONTROL_STATUS,
    }
    _write_json(output_dir / "summary.json", summary)
    _write_json(output_dir / "case-results.json", case_results)
    _write_json(output_dir / "control-status.json", control_status)
    (output_dir / "report.md").write_text(_render_report(results), encoding="utf-8")
    files = (*MACHINE_FILES, "report.md")
    manifest = {
        "schema_version": "1.0",
        "evidence_version": "phase1-evidence-v1",
        "input_digests": {
            "dataset": sha256_file(DEFAULT_DATASET_PATH),
            "corpus": sha256_file(DEFAULT_CORPUS_PATH),
            "release_policy": sha256_file(DEFAULT_POLICY_PATH),
        },
        "files": {name: sha256_file(output_dir / name) for name in files},
        "volatile_fields": [
            "summary.generated_at_utc",
            "summary.variants.*.run_id",
            "summary.variants.*.trace_ids",
            "case-results.variants.*.*.trace_id",
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
    }
    if manifest.get("input_digests") != expected_inputs:
        raise EvidenceValidationError("evidence input digests are stale")
    files = cast(dict[str, str], manifest.get("files"))
    for name in (*MACHINE_FILES, "report.md"):
        path = output_dir / name
        if files.get(name) != sha256_file(path):
            raise EvidenceValidationError(f"evidence file hash mismatch: {name}")
        if contains_sensitive_marker(path.read_text(encoding="utf-8")):
            raise EvidenceValidationError(f"sensitive marker found in evidence: {name}")
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
    controls = _json(output_dir / "control-status.json")["controls"]
    if not controls or any(
        not all(item.get(key) for key in ("control_id", "risk_ids", "test", "evidence", "status"))
        for item in controls
    ):
        raise EvidenceValidationError("control status contains an incomplete traceability link")


def manifest_digest(output_dir: Path = DEFAULT_EVIDENCE_DIR) -> str:
    return hashlib.sha256((output_dir / "manifest.json").read_bytes()).hexdigest()
