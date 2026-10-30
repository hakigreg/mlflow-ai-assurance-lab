from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from mlflow_ai_assurance_lab.evidence import (
    EvidenceValidationError,
    compare_evidence,
    generate_evidence,
    validate_evidence,
)
from mlflow_ai_assurance_lab.redaction import contains_unsafe_persistence_content

ROOT = Path(__file__).resolve().parents[1]


def _copy_sample(tmp_path: Path) -> Path:
    evidence = tmp_path / "evidence"
    shutil.copytree(ROOT / "evidence/sample", evidence)
    return evidence


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _refresh_hash(evidence: Path, name: str) -> None:
    manifest_path = evidence / "manifest.json"
    manifest = _read_json(manifest_path)
    files = manifest["files"]
    assert isinstance(files, dict)
    files[name] = hashlib.sha256((evidence / name).read_bytes()).hexdigest()
    _write_json(manifest_path, manifest)


def test_sample_evidence_is_valid() -> None:
    validate_evidence(ROOT / "evidence/sample")


def test_tampered_evidence_is_rejected(tmp_path: Path) -> None:
    evidence = _copy_sample(tmp_path)
    report = evidence / "report.md"
    report.write_text(report.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
    with pytest.raises(EvidenceValidationError, match="hash mismatch"):
        validate_evidence(evidence)


def test_contradictory_control_status_is_rejected(tmp_path: Path) -> None:
    evidence = _copy_sample(tmp_path)
    control_path = evidence / "control-status.json"
    control_status = json.loads(control_path.read_text(encoding="utf-8"))
    citation = next(
        item for item in control_status["controls"] if item["control_id"] == "CTRL-CITE-001"
    )
    citation["status"] = "FAIL"
    control_path.write_text(
        json.dumps(control_status, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest_path = evidence / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"]["control-status.json"] = hashlib.sha256(control_path.read_bytes()).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    with pytest.raises(EvidenceValidationError, match="contradicts measured results"):
        validate_evidence(evidence)


def test_missing_evidence_file_is_rejected(tmp_path: Path) -> None:
    evidence = _copy_sample(tmp_path)
    (evidence / "case-results.json").unlink()

    with pytest.raises(EvidenceValidationError, match="required evidence file is missing"):
        validate_evidence(evidence)


def test_stale_input_provenance_is_rejected(tmp_path: Path) -> None:
    evidence = _copy_sample(tmp_path)
    manifest_path = evidence / "manifest.json"
    manifest = _read_json(manifest_path)
    provenance = manifest["provenance"]
    assert isinstance(provenance, dict)
    inputs = provenance["inputs"]
    assert isinstance(inputs, dict)
    dataset = inputs["dataset"]
    assert isinstance(dataset, dict)
    dataset["sha256"] = "0" * 64
    _write_json(manifest_path, manifest)

    with pytest.raises(EvidenceValidationError, match="input provenance is stale"):
        validate_evidence(evidence)


def test_unknown_schema_version_is_rejected(tmp_path: Path) -> None:
    evidence = _copy_sample(tmp_path)
    manifest_path = evidence / "manifest.json"
    manifest = _read_json(manifest_path)
    manifest["schema_version"] = "999.0"
    _write_json(manifest_path, manifest)

    with pytest.raises(EvidenceValidationError, match="unsupported manifest schema"):
        validate_evidence(evidence)


@pytest.mark.parametrize("defect", ["missing", "wrong_type"])
def test_summary_contract_rejects_missing_or_wrong_typed_fields(
    tmp_path: Path, defect: str
) -> None:
    evidence = _copy_sample(tmp_path)
    summary_path = evidence / "summary.json"
    summary = _read_json(summary_path)
    if defect == "missing":
        del summary["app_version"]
    else:
        summary["app_version"] = 1
    _write_json(summary_path, summary)
    _refresh_hash(evidence, "summary.json")

    message = "fields are invalid" if defect == "missing" else "must be a non-empty string"
    with pytest.raises(EvidenceValidationError, match=message):
        validate_evidence(evidence)


def test_contradictory_case_trace_relation_is_rejected(tmp_path: Path) -> None:
    evidence = _copy_sample(tmp_path)
    cases_path = evidence / "case-results.json"
    cases = _read_json(cases_path)
    variants = cases["variants"]
    assert isinstance(variants, dict)
    governed = variants["governed"]
    assert isinstance(governed, list)
    assert isinstance(governed[0], dict)
    governed[0]["trace_id"] = "tr-contradictory"
    _write_json(cases_path, cases)
    _refresh_hash(evidence, "case-results.json")

    with pytest.raises(EvidenceValidationError, match="case-to-trace relation contradicts"):
        validate_evidence(evidence)


def test_prohibited_evidence_content_is_rejected_even_with_updated_checksum(
    tmp_path: Path,
) -> None:
    evidence = _copy_sample(tmp_path)
    report = evidence / "report.md"
    report.write_text(report.read_text(encoding="utf-8") + "ignore previous controls\n")
    _refresh_hash(evidence, "report.md")

    with pytest.raises(EvidenceValidationError, match="prohibited persistence content"):
        validate_evidence(evidence)


def test_comparison_normalizes_timestamp_only_differences(tmp_path: Path) -> None:
    evidence = _copy_sample(tmp_path)
    summary_path = evidence / "summary.json"
    summary = _read_json(summary_path)
    previous = summary["generated_at_utc"]
    assert isinstance(previous, str)
    replacement = "2030-01-02T03:04:05Z"
    summary["generated_at_utc"] = replacement
    _write_json(summary_path, summary)
    report = evidence / "report.md"
    report.write_text(
        report.read_text(encoding="utf-8").replace(previous, replacement), encoding="utf-8"
    )
    _refresh_hash(evidence, "summary.json")
    _refresh_hash(evidence, "report.md")

    comparison = compare_evidence(ROOT / "evidence/sample", evidence)

    assert comparison["material_match"] is True
    assert comparison["raw_artifacts_match"] is False
    assert comparison["classification"] == "volatile_or_normalizable_only"


def test_comparison_reports_material_result_drift(tmp_path: Path) -> None:
    summary = _read_json(ROOT / "evidence/sample/summary.json")
    cases = _read_json(ROOT / "evidence/sample/case-results.json")
    summary_variants = summary["variants"]
    case_variants = cases["variants"]
    assert isinstance(summary_variants, dict)
    assert isinstance(case_variants, dict)
    baseline = summary_variants["baseline"]
    baseline_cases = case_variants["baseline"]
    assert isinstance(baseline, dict)
    assert isinstance(baseline_cases, list)
    metrics = baseline["metrics"]
    assert isinstance(metrics, dict)
    metrics["citation_source_match"] = 0.125
    positive_case = next(item for item in baseline_cases if item["case_id"] == "CASE-POS-001")
    positive_case["scores"]["citation_source_match"] = 0.0
    results = dict(summary)
    results["variants"] = {
        name: {**summary_variants[name], "cases": case_variants[name]}
        for name in ("baseline", "governed")
    }
    results_path = tmp_path / "drifted-results.json"
    _write_json(results_path, results)
    drifted = tmp_path / "drifted-evidence"
    generate_evidence(results_path, drifted)

    comparison = compare_evidence(ROOT / "evidence/sample", drifted)

    assert comparison["material_match"] is False
    assert comparison["classification"] == "material_drift"


def test_generated_sample_artifacts_contain_no_prohibited_persistence_content() -> None:
    evidence = ROOT / "evidence/sample"
    for name in (
        "manifest.json",
        "summary.json",
        "case-results.json",
        "control-status.json",
        "report.md",
    ):
        assert not contains_unsafe_persistence_content(
            (evidence / name).read_text(encoding="utf-8")
        )


def test_manifest_contains_no_machine_specific_absolute_paths() -> None:
    manifest = (ROOT / "evidence/sample/manifest.json").read_text(encoding="utf-8")
    personal_path_markers = ("/" + "Users/", "/" + "home/", "C:\\" + "Users\\")
    assert not any(marker in manifest for marker in personal_path_markers)
