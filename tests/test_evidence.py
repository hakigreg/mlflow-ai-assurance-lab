from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from mlflow_ai_assurance_lab.evidence import EvidenceValidationError, validate_evidence
from mlflow_ai_assurance_lab.redaction import contains_unsafe_persistence_content

ROOT = Path(__file__).resolve().parents[1]


def test_sample_evidence_is_valid() -> None:
    validate_evidence(ROOT / "evidence/sample")


def test_tampered_evidence_is_rejected(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    shutil.copytree(ROOT / "evidence/sample", evidence)
    report = evidence / "report.md"
    report.write_text(report.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
    with pytest.raises(EvidenceValidationError, match="hash mismatch"):
        validate_evidence(evidence)


def test_contradictory_control_status_is_rejected(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    shutil.copytree(ROOT / "evidence/sample", evidence)
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


def test_generated_sample_artifacts_contain_no_prohibited_persistence_content() -> None:
    evidence = ROOT / "evidence/sample"
    for name in ("summary.json", "case-results.json", "control-status.json", "report.md"):
        assert not contains_unsafe_persistence_content(
            (evidence / name).read_text(encoding="utf-8")
        )
