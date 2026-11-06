"""Generate, compare, and validate the measured assurance evidence pack."""

from __future__ import annotations

import copy
import hashlib
import importlib.metadata
import json
import math
import platform
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from mlflow_ai_assurance_lab.config import (
    DEFAULT_CORPUS_PATH,
    DEFAULT_DATASET_PATH,
    DEFAULT_POLICY_PATH,
    SCORER_NAMES,
    load_evaluation_records,
    load_json,
    load_release_policy,
)
from mlflow_ai_assurance_lab.control_catalog import DEFAULT_CONTROL_CATALOG_PATH, ROOT
from mlflow_ai_assurance_lab.controls import (
    CONTROL_STATUS_SCHEMA_VERSION,
    ControlTraceabilityError,
    derive_control_status,
    render_control_matrix,
    validate_control_status,
    validate_evidence_references,
)
from mlflow_ai_assurance_lab.evaluation import DEFAULT_RESULTS_PATH, sha256_file
from mlflow_ai_assurance_lab.redaction import contains_unsafe_persistence_content
from mlflow_ai_assurance_lab.tracking import EXPERIMENT_NAME

DEFAULT_EVIDENCE_DIR = Path("artifacts/evidence/latest")
SAMPLE_EVIDENCE_DIR = ROOT / "evidence/sample"
CONTROL_MATRIX_PATH = ROOT / "docs/control-matrix.md"
MACHINE_FILES = ("summary.json", "case-results.json", "control-status.json")
PACK_FILES = (*MACHINE_FILES, "report.md")
SUMMARY_SCHEMA_VERSION = "2.0"
CASE_RESULTS_SCHEMA_VERSION = "2.0"
MANIFEST_SCHEMA_VERSION = "2.0"
EVIDENCE_VERSION = "phase2-evidence-provenance-v2"
COMPARISON_PROFILE_VERSION = "material-assurance-v1"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
GIT_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
APP_SOURCE_PATHS = (
    Path("Makefile"),
    Path("pyproject.toml"),
    Path("uv.lock"),
)
VOLATILE_FIELDS = (
    "summary.generated_at_utc",
    "summary.variants.*.experiment_id",
    "summary.variants.*.run_id",
    "summary.variants.*.trace_ids",
    "case-results.variants.*.*.trace_id",
    "control-status.controls.*.mlflow_anchors.*.run_id",
    "control-status.controls.*.mlflow_anchors.*.cases.*.trace_id",
    "manifest.mlflow",
    "report generated timestamp and MLflow identifiers",
)
NORMALIZABLE_FIELDS = (
    "manifest.provenance.git.commit",
    "manifest.provenance.git.working_tree",
)
DETERMINISTIC_FIELDS = (
    "input versions and SHA-256 digests",
    "application source SHA-256 digest",
    "tool versions",
    "decisions, metrics, failed metrics, cases, actions, citations, and scores",
    "derived control status excluding MLflow identifiers",
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


def _exact_keys(value: dict[str, Any], expected: set[str], location: str) -> None:
    observed = set(value)
    if observed != expected:
        raise EvidenceValidationError(
            f"{location} fields are invalid: "
            f"missing={sorted(expected - observed)}, extra={sorted(observed - expected)}"
        )


def _object(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvidenceValidationError(f"{location} must be an object")
    return cast(dict[str, Any], value)


def _list(value: Any, location: str) -> list[Any]:
    if not isinstance(value, list):
        raise EvidenceValidationError(f"{location} must be a list")
    return value


def _string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value:
        raise EvidenceValidationError(f"{location} must be a non-empty string")
    return value


def _strings(value: Any, location: str, *, unique: bool = False) -> list[str]:
    values = [_string(item, f"{location} item") for item in _list(value, location)]
    if unique and len(values) != len(set(values)):
        raise EvidenceValidationError(f"{location} values must be unique")
    return values


def _sha256(value: Any, location: str) -> str:
    digest = _string(value, location)
    if SHA256_PATTERN.fullmatch(digest) is None:
        raise EvidenceValidationError(f"{location} must be a lowercase SHA-256 digest")
    return digest


def _number(value: Any, location: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EvidenceValidationError(f"{location} must be numeric")
    number = float(value)
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        raise EvidenceValidationError(f"{location} must be finite and in [0, 1]")
    return number


def _normalized_utc(value: Any, location: str) -> str:
    timestamp = _string(value, location)
    if UTC_PATTERN.fullmatch(timestamp) is None:
        raise EvidenceValidationError(f"{location} must be normalized UTC ending in Z")
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceValidationError(f"{location} is not a valid timestamp") from exc
    if parsed.tzinfo != UTC:
        raise EvidenceValidationError(f"{location} must use UTC")
    return timestamp


def _package_version(distribution: str) -> str:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError as exc:
        raise EvidenceValidationError(
            f"required package metadata is missing: {distribution}"
        ) from exc


def _source_digest() -> str:
    paths = [ROOT / path for path in APP_SOURCE_PATHS]
    paths.extend(sorted((ROOT / "src/mlflow_ai_assurance_lab").glob("*.py")))
    digest = hashlib.sha256()
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _git_provenance() -> dict[str, str]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {"commit": "unavailable", "working_tree": "unavailable"}
    if GIT_COMMIT_PATTERN.fullmatch(commit) is None:
        return {"commit": "unavailable", "working_tree": "unavailable"}
    return {"commit": commit, "working_tree": "dirty" if status else "clean"}


def _input_provenance() -> dict[str, dict[str, Any]]:
    dataset = load_json(DEFAULT_DATASET_PATH)
    corpus = load_json(DEFAULT_CORPUS_PATH)
    policy = load_json(DEFAULT_POLICY_PATH)
    catalog = load_json(DEFAULT_CONTROL_CATALOG_PATH)
    return {
        "dataset": {
            "schema_version": dataset["schema_version"],
            "version": dataset["dataset_version"],
            "sha256": sha256_file(DEFAULT_DATASET_PATH),
        },
        "corpus": {
            "schema_version": corpus["schema_version"],
            "version": corpus["corpus_version"],
            "sha256": sha256_file(DEFAULT_CORPUS_PATH),
        },
        "release_policy": {
            "schema_version": policy["schema_version"],
            "version": policy["policy_version"],
            "sha256": sha256_file(DEFAULT_POLICY_PATH),
            "thresholds": policy["thresholds"],
        },
        "control_catalog": {
            "schema_version": catalog["schema_version"],
            "version": catalog["catalog_version"],
            "sha256": sha256_file(DEFAULT_CONTROL_CATALOG_PATH),
        },
    }


def _provenance() -> dict[str, Any]:
    return {
        "application": {
            "name": "mlflow-ai-assurance-lab",
            "version": _package_version("mlflow-ai-assurance-lab"),
            "source_sha256": _source_digest(),
        },
        "git": _git_provenance(),
        "inputs": _input_provenance(),
        "tools": {
            "python": platform.python_version(),
            "mlflow": _package_version("mlflow"),
        },
    }


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
            "## Measured control observations",
            "",
            "| Control | Governed result | Metric or method | Observed | Threshold | "
            "Baseline result |",
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


def _normalized_control_status(status: dict[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(status)
    for control in cast(list[dict[str, Any]], normalized["controls"]):
        anchors = cast(dict[str, dict[str, Any]], control["mlflow_anchors"])
        for variant in ("baseline", "governed"):
            anchors[variant].pop("run_id", None)
            for case in cast(list[dict[str, Any]], anchors[variant]["cases"]):
                case.pop("trace_id", None)
    return normalized


def _material_payload(
    summary: dict[str, Any],
    cases: dict[str, Any],
    control_status: dict[str, Any],
    provenance: dict[str, Any],
) -> dict[str, Any]:
    normalized_summary = copy.deepcopy(summary)
    normalized_summary.pop("generated_at_utc", None)
    for variant in cast(dict[str, dict[str, Any]], normalized_summary["variants"]).values():
        variant.pop("experiment_id", None)
        variant.pop("run_id", None)
        variant.pop("trace_ids", None)
    normalized_cases = copy.deepcopy(cases)
    for variant_cases in cast(
        dict[str, list[dict[str, Any]]], normalized_cases["variants"]
    ).values():
        for case in variant_cases:
            case.pop("trace_id", None)
    material_provenance = copy.deepcopy(provenance)
    material_provenance.pop("git", None)
    return {
        "summary": normalized_summary,
        "case_results": normalized_cases,
        "control_status": _normalized_control_status(control_status),
        "provenance": material_provenance,
    }


def _digest_json(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_summary(summary: dict[str, Any]) -> None:
    _exact_keys(
        summary,
        {
            "schema_version",
            "generated_at_utc",
            "app_version",
            "dataset_version",
            "dataset_sha256",
            "corpus_version",
            "corpus_sha256",
            "release_policy_sha256",
            "control_catalog_sha256",
            "control_catalog_version",
            "policy_version",
            "variants",
        },
        "summary",
    )
    if summary["schema_version"] != SUMMARY_SCHEMA_VERSION:
        raise EvidenceValidationError("unsupported summary schema version")
    _normalized_utc(summary["generated_at_utc"], "summary.generated_at_utc")
    for field in ("app_version", "dataset_version", "corpus_version", "policy_version"):
        _string(summary[field], f"summary.{field}")
    for field in (
        "dataset_sha256",
        "corpus_sha256",
        "release_policy_sha256",
        "control_catalog_sha256",
    ):
        _sha256(summary[field], f"summary.{field}")
    _string(summary["control_catalog_version"], "summary.control_catalog_version")
    variants = _object(summary["variants"], "summary.variants")
    _exact_keys(variants, {"baseline", "governed"}, "summary.variants")
    policy = load_release_policy()
    for name in ("baseline", "governed"):
        variant = _object(variants[name], f"summary.variants.{name}")
        _exact_keys(
            variant,
            {
                "variant",
                "experiment_id",
                "run_id",
                "trace_ids",
                "metrics",
                "decision",
                "failed_metrics",
                "persistence_safe",
            },
            f"summary.variants.{name}",
        )
        if variant["variant"] != name:
            raise EvidenceValidationError(f"summary variant label is inconsistent for {name}")
        _string(variant["experiment_id"], f"summary.variants.{name}.experiment_id")
        _string(variant["run_id"], f"summary.variants.{name}.run_id")
        _strings(variant["trace_ids"], f"summary.variants.{name}.trace_ids", unique=True)
        metrics = _object(variant["metrics"], f"summary.variants.{name}.metrics")
        _exact_keys(metrics, set(SCORER_NAMES), f"summary.variants.{name}.metrics")
        for scorer, score in metrics.items():
            _number(score, f"summary.variants.{name}.metrics.{scorer}")
        if variant["decision"] not in {"PASS", "FAIL"}:
            raise EvidenceValidationError(f"summary.variants.{name}.decision is invalid")
        failed = _strings(
            variant["failed_metrics"], f"summary.variants.{name}.failed_metrics", unique=True
        )
        if not set(failed) <= set(SCORER_NAMES):
            raise EvidenceValidationError(f"summary.variants.{name}.failed_metrics is invalid")
        if not isinstance(variant["persistence_safe"], bool):
            raise EvidenceValidationError(
                f"summary.variants.{name}.persistence_safe must be a boolean"
            )
        expected_decision = policy.expected_decisions[cast(Any, name)]
        if variant["decision"] != expected_decision:
            raise EvidenceValidationError(f"summary decision is unexpected for {name}")


def _validate_case_results(cases: dict[str, Any], summary: dict[str, Any]) -> None:
    _exact_keys(cases, {"schema_version", "dataset_sha256", "variants"}, "case-results")
    if cases["schema_version"] != CASE_RESULTS_SCHEMA_VERSION:
        raise EvidenceValidationError("unsupported case-results schema version")
    digest = _sha256(cases["dataset_sha256"], "case-results.dataset_sha256")
    if digest != summary["dataset_sha256"]:
        raise EvidenceValidationError("case-results dataset digest contradicts summary")
    variants = _object(cases["variants"], "case-results.variants")
    _exact_keys(variants, {"baseline", "governed"}, "case-results.variants")
    summary_variants = cast(dict[str, dict[str, Any]], summary["variants"])
    expected_case_ids = {str(record["inputs"]["case_id"]) for record in load_evaluation_records()}
    for name in ("baseline", "governed"):
        observed_ids: list[str] = []
        observed_trace_ids: list[str] = []
        raw_cases = _list(variants[name], f"case-results.variants.{name}")
        for index, raw_case in enumerate(raw_cases):
            location = f"case-results.variants.{name}.{index}"
            case = _object(raw_case, location)
            _exact_keys(
                case,
                {"case_id", "trace_id", "action", "citations", "scores"},
                location,
            )
            case_id = _string(case["case_id"], f"{location}.case_id")
            observed_ids.append(case_id)
            observed_trace_ids.append(_string(case["trace_id"], f"{location}.trace_id"))
            _string(case["action"], f"{location}.action")
            _strings(case["citations"], f"{location}.citations", unique=True)
            scores = _object(case["scores"], f"{location}.scores")
            _exact_keys(scores, set(SCORER_NAMES), f"{location}.scores")
            for scorer, score in scores.items():
                _number(score, f"{location}.scores.{scorer}")
        if len(observed_ids) != len(set(observed_ids)) or set(observed_ids) != expected_case_ids:
            raise EvidenceValidationError(f"case coverage mismatch for {name}")
        if observed_trace_ids != summary_variants[name]["trace_ids"]:
            raise EvidenceValidationError(f"case-to-trace relation contradicts summary for {name}")


def _validate_provenance(provenance: dict[str, Any]) -> None:
    _exact_keys(provenance, {"application", "git", "inputs", "tools"}, "manifest.provenance")
    application = _object(provenance["application"], "manifest.provenance.application")
    _exact_keys(
        application, {"name", "version", "source_sha256"}, "manifest.provenance.application"
    )
    if application["name"] != "mlflow-ai-assurance-lab":
        raise EvidenceValidationError("manifest application name is invalid")
    if application["version"] != _package_version("mlflow-ai-assurance-lab"):
        raise EvidenceValidationError("manifest application version is stale")
    source_digest = _sha256(application["source_sha256"], "manifest application source digest")
    if source_digest != _source_digest():
        raise EvidenceValidationError("manifest application source digest is stale")
    git = _object(provenance["git"], "manifest.provenance.git")
    _exact_keys(git, {"commit", "working_tree"}, "manifest.provenance.git")
    commit = _string(git["commit"], "manifest.provenance.git.commit")
    if commit != "unavailable" and GIT_COMMIT_PATTERN.fullmatch(commit) is None:
        raise EvidenceValidationError("manifest Git commit is invalid")
    if git["working_tree"] not in {"clean", "dirty", "unavailable"}:
        raise EvidenceValidationError("manifest working-tree marker is invalid")
    inputs = _object(provenance["inputs"], "manifest.provenance.inputs")
    if inputs != _input_provenance():
        raise EvidenceValidationError("evidence input provenance is stale")
    tools = _object(provenance["tools"], "manifest.provenance.tools")
    _exact_keys(tools, {"python", "mlflow"}, "manifest.provenance.tools")
    _string(tools["python"], "manifest.provenance.tools.python")
    if tools["mlflow"] != _package_version("mlflow"):
        raise EvidenceValidationError("manifest MLflow version is stale")


def _validate_manifest(manifest: dict[str, Any]) -> None:
    _exact_keys(
        manifest,
        {
            "schema_version",
            "evidence_version",
            "provenance",
            "mlflow",
            "files",
            "artifact_schema_versions",
            "comparison",
        },
        "manifest",
    )
    if manifest["schema_version"] != MANIFEST_SCHEMA_VERSION:
        raise EvidenceValidationError("unsupported manifest schema version")
    if manifest["evidence_version"] != EVIDENCE_VERSION:
        raise EvidenceValidationError("unsupported evidence version")
    _validate_provenance(_object(manifest["provenance"], "manifest.provenance"))
    mlflow = _object(manifest["mlflow"], "manifest.mlflow")
    _exact_keys(mlflow, {"experiment_name", "variants"}, "manifest.mlflow")
    if mlflow["experiment_name"] != EXPERIMENT_NAME:
        raise EvidenceValidationError("manifest MLflow experiment name is invalid")
    mlflow_variants = _object(mlflow["variants"], "manifest.mlflow.variants")
    _exact_keys(mlflow_variants, {"baseline", "governed"}, "manifest.mlflow.variants")
    for name in ("baseline", "governed"):
        item = _object(mlflow_variants[name], f"manifest.mlflow.variants.{name}")
        _exact_keys(item, {"experiment_id", "run_id"}, f"manifest.mlflow.variants.{name}")
        _string(item["experiment_id"], f"manifest.mlflow.variants.{name}.experiment_id")
        _string(item["run_id"], f"manifest.mlflow.variants.{name}.run_id")
    files = _object(manifest["files"], "manifest.files")
    _exact_keys(files, set(PACK_FILES), "manifest.files")
    for name, digest in files.items():
        _sha256(digest, f"manifest.files.{name}")
    artifact_schemas = _object(
        manifest["artifact_schema_versions"], "manifest.artifact_schema_versions"
    )
    _exact_keys(artifact_schemas, set(MACHINE_FILES), "manifest.artifact_schema_versions")
    expected_schemas = {
        "summary.json": SUMMARY_SCHEMA_VERSION,
        "case-results.json": CASE_RESULTS_SCHEMA_VERSION,
        "control-status.json": CONTROL_STATUS_SCHEMA_VERSION,
    }
    if artifact_schemas != expected_schemas:
        raise EvidenceValidationError("manifest artifact schema versions are invalid")
    comparison = _object(manifest["comparison"], "manifest.comparison")
    _exact_keys(
        comparison,
        {
            "profile_version",
            "material_digest",
            "deterministic_fields",
            "normalizable_fields",
            "volatile_fields",
        },
        "manifest.comparison",
    )
    if comparison["profile_version"] != COMPARISON_PROFILE_VERSION:
        raise EvidenceValidationError("unsupported evidence comparison profile")
    _sha256(comparison["material_digest"], "manifest.comparison.material_digest")
    deterministic = tuple(_strings(comparison["deterministic_fields"], "deterministic fields"))
    normalizable = tuple(_strings(comparison["normalizable_fields"], "normalizable fields"))
    volatile = tuple(_strings(comparison["volatile_fields"], "volatile fields"))
    if deterministic != DETERMINISTIC_FIELDS:
        raise EvidenceValidationError("manifest deterministic-field classification is invalid")
    if normalizable != NORMALIZABLE_FIELDS:
        raise EvidenceValidationError("manifest normalizable-field classification is invalid")
    if volatile != VOLATILE_FIELDS:
        raise EvidenceValidationError("manifest volatile-field classification is invalid")


def generate_evidence(
    results_path: Path = DEFAULT_RESULTS_PATH,
    output_dir: Path = DEFAULT_EVIDENCE_DIR,
) -> Path:
    results = _json(results_path)
    provenance = _provenance()
    output_dir.mkdir(parents=True, exist_ok=True)
    variants = cast(dict[str, dict[str, Any]], results["variants"])
    control_status = derive_control_status(results)
    summary = {key: value for key, value in results.items() if key != "variants"}
    summary["variants"] = {
        name: {key: value for key, value in variant.items() if key != "cases"}
        for name, variant in variants.items()
    }
    case_results = {
        "schema_version": CASE_RESULTS_SCHEMA_VERSION,
        "dataset_sha256": results["dataset_sha256"],
        "variants": {name: variant["cases"] for name, variant in variants.items()},
    }
    _validate_summary(summary)
    _validate_case_results(case_results, summary)
    _write_json(output_dir / "summary.json", summary)
    _write_json(output_dir / "case-results.json", case_results)
    _write_json(output_dir / "control-status.json", control_status)
    (output_dir / "report.md").write_text(_render_report(results, control_status), encoding="utf-8")
    if output_dir.resolve() == SAMPLE_EVIDENCE_DIR.resolve():
        CONTROL_MATRIX_PATH.write_text(render_control_matrix(control_status), encoding="utf-8")
    material_digest = _digest_json(
        _material_payload(summary, case_results, control_status, provenance)
    )
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "evidence_version": EVIDENCE_VERSION,
        "provenance": provenance,
        "mlflow": {
            "experiment_name": EXPERIMENT_NAME,
            "variants": {
                name: {
                    "experiment_id": variant["experiment_id"],
                    "run_id": variant["run_id"],
                }
                for name, variant in variants.items()
            },
        },
        "files": {name: sha256_file(output_dir / name) for name in PACK_FILES},
        "artifact_schema_versions": {
            "summary.json": SUMMARY_SCHEMA_VERSION,
            "case-results.json": CASE_RESULTS_SCHEMA_VERSION,
            "control-status.json": CONTROL_STATUS_SCHEMA_VERSION,
        },
        "comparison": {
            "profile_version": COMPARISON_PROFILE_VERSION,
            "material_digest": material_digest,
            "deterministic_fields": list(DETERMINISTIC_FIELDS),
            "normalizable_fields": list(NORMALIZABLE_FIELDS),
            "volatile_fields": list(VOLATILE_FIELDS),
        },
    }
    _write_json(output_dir / "manifest.json", manifest)
    validate_evidence(output_dir)
    return output_dir


def validate_evidence(output_dir: Path = DEFAULT_EVIDENCE_DIR) -> None:
    manifest_path = output_dir / "manifest.json"
    manifest = _json(manifest_path)
    _validate_manifest(manifest)
    for name in PACK_FILES:
        path = output_dir / name
        if not path.is_file():
            raise EvidenceValidationError(f"required evidence file is missing: {name}")
        if cast(dict[str, str], manifest["files"])[name] != sha256_file(path):
            raise EvidenceValidationError(f"evidence file hash mismatch: {name}")
        if contains_unsafe_persistence_content(path.read_text(encoding="utf-8")):
            raise EvidenceValidationError(
                f"prohibited persistence content found in evidence: {name}"
            )
    if contains_unsafe_persistence_content(manifest_path.read_text(encoding="utf-8")):
        raise EvidenceValidationError(
            "prohibited persistence content found in evidence: manifest.json"
        )

    summary = _json(output_dir / "summary.json")
    _validate_summary(summary)
    cases = _json(output_dir / "case-results.json")
    _validate_case_results(cases, summary)
    control_status = _json(output_dir / "control-status.json")
    if control_status.get("schema_version") != CONTROL_STATUS_SCHEMA_VERSION:
        raise EvidenceValidationError("unsupported control-status schema version")

    variants = cast(dict[str, dict[str, Any]], summary["variants"])
    provenance = cast(dict[str, Any], manifest["provenance"])
    provenance_application = cast(dict[str, Any], provenance["application"])
    provenance_inputs = cast(dict[str, dict[str, Any]], provenance["inputs"])
    summary_bindings = {
        "app_version": provenance_application["version"],
        "dataset_version": provenance_inputs["dataset"]["version"],
        "dataset_sha256": provenance_inputs["dataset"]["sha256"],
        "corpus_version": provenance_inputs["corpus"]["version"],
        "corpus_sha256": provenance_inputs["corpus"]["sha256"],
        "policy_version": provenance_inputs["release_policy"]["version"],
        "release_policy_sha256": provenance_inputs["release_policy"]["sha256"],
        "control_catalog_version": provenance_inputs["control_catalog"]["version"],
        "control_catalog_sha256": provenance_inputs["control_catalog"]["sha256"],
    }
    for field, expected in summary_bindings.items():
        if summary[field] != expected:
            raise EvidenceValidationError(f"summary {field} contradicts provenance")
    manifest_mlflow = cast(dict[str, Any], manifest["mlflow"])["variants"]
    for name in ("baseline", "governed"):
        expected_anchor = {
            "experiment_id": variants[name]["experiment_id"],
            "run_id": variants[name]["run_id"],
        }
        if manifest_mlflow[name] != expected_anchor:
            raise EvidenceValidationError(
                f"manifest MLflow provenance contradicts summary for {name}"
            )

    reconstructed = dict(summary)
    reconstructed["variants"] = {
        variant: {
            **variants[variant],
            "cases": cast(dict[str, Any], cases["variants"])[variant],
        }
        for variant in ("baseline", "governed")
    }
    try:
        validate_control_status(control_status, reconstructed)
        validate_evidence_references(control_status, output_dir)
    except ControlTraceabilityError as exc:
        raise EvidenceValidationError(str(exc)) from exc
    if (output_dir / "report.md").read_text(encoding="utf-8") != _render_report(
        reconstructed, control_status
    ):
        raise EvidenceValidationError("human report contradicts machine evidence")
    expected_material_digest = _digest_json(
        _material_payload(
            summary,
            cases,
            control_status,
            cast(dict[str, Any], manifest["provenance"]),
        )
    )
    comparison = cast(dict[str, Any], manifest["comparison"])
    if comparison["material_digest"] != expected_material_digest:
        raise EvidenceValidationError("evidence material digest mismatch")
    if output_dir.resolve() == SAMPLE_EVIDENCE_DIR.resolve():
        expected_matrix = render_control_matrix(control_status)
        if CONTROL_MATRIX_PATH.read_text(encoding="utf-8") != expected_matrix:
            raise EvidenceValidationError(
                "human control matrix is stale relative to measured machine evidence"
            )


def compare_evidence(left: Path, right: Path) -> dict[str, Any]:
    """Compare validated packs while separating material drift from known volatility."""

    validate_evidence(left)
    validate_evidence(right)
    left_manifest = _json(left / "manifest.json")
    right_manifest = _json(right / "manifest.json")
    left_comparison = cast(dict[str, Any], left_manifest["comparison"])
    right_comparison = cast(dict[str, Any], right_manifest["comparison"])
    left_digest = str(left_comparison["material_digest"])
    right_digest = str(right_comparison["material_digest"])
    left_files = cast(dict[str, str], left_manifest["files"])
    right_files = cast(dict[str, str], right_manifest["files"])
    if left_files == right_files:
        classification = "identical"
    elif left_digest == right_digest:
        classification = "volatile_or_normalizable_only"
    else:
        classification = "material_drift"
    return {
        "comparison_profile": COMPARISON_PROFILE_VERSION,
        "material_match": left_digest == right_digest,
        "left_material_digest": left_digest,
        "right_material_digest": right_digest,
        "raw_artifacts_match": left_files == right_files,
        "classification": classification,
    }


def manifest_digest(output_dir: Path = DEFAULT_EVIDENCE_DIR) -> str:
    return hashlib.sha256((output_dir / "manifest.json").read_bytes()).hexdigest()
