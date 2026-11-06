from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_readme_leads_with_the_assurance_lab() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert readme.startswith("# MLflow AI Assurance Lab\n")
    assert "Status:" not in readme


def test_project_explanation_materials_exist() -> None:
    for relative_path in (
        "docs/architecture-decisions.md",
        "docs/demo-script.md",
        "docs/interview-notes.md",
    ):
        assert (ROOT / relative_path).is_file(), relative_path


def test_durable_contracts_exist() -> None:
    for relative_path in ("AGENTS.md", "GOALS.md"):
        assert (ROOT / relative_path).is_file(), relative_path


def test_governance_claim_contracts_are_explicit() -> None:
    assurance = (ROOT / "docs/assurance-statement.md").read_text(encoding="utf-8")
    ledger = (ROOT / "docs/claim-ledger.md").read_text(encoding="utf-8")
    findings = (ROOT / "docs/findings.md").read_text(encoding="utf-8")
    crosswalk = (ROOT / "docs/standards-crosswalk.md").read_text(encoding="utf-8")
    threat_model = (ROOT / "docs/threat-model.md").read_text(encoding="utf-8")

    for heading in (
        "## Claim",
        "## Evidence",
        "## Assumptions",
        "## Limitations and permitted use",
    ):
        assert heading in assurance
    for claim_number in range(1, 9):
        assert f"CLAIM-{claim_number:03d}" in ledger
    for heading in (
        "## Observed technical results",
        "## Known gaps and bounded interpretation",
        "## Recommendations for enterprise extension",
    ):
        assert heading in findings
    assert "does not establish legal" in crosswalk
    assert "Not applicable to the implemented retriever" in threat_model
    assert "Out of scope" in threat_model


def test_project_metadata_pins_runtime() -> None:
    with (ROOT / "pyproject.toml").open("rb") as file_handle:
        metadata = tomllib.load(file_handle)

    project = metadata["project"]
    assert project["requires-python"] == ">=3.12.16,<3.13"
    assert project["dependencies"] == ["mlflow==3.17.2"]
    assert project["license"] == "MIT"
    assert "License :: OSI Approved :: MIT License" in project["classifiers"]


def test_license_file_is_mit() -> None:
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert license_text.startswith("MIT License\n")
    assert "Permission is hereby granted, free of charge" in license_text


def test_pinned_mlflow_api_surface_is_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MLFLOW_DISABLE_AGENT_HINT", "1")

    import mlflow
    from mlflow.genai import evaluate
    from mlflow.genai.datasets import create_dataset
    from mlflow.genai.scorers import scorer

    assert mlflow.__version__ == "3.17.2"
    assert all(callable(item) for item in (mlflow.start_span, evaluate, create_dataset, scorer))


def test_phase_one_modules_exist() -> None:
    package = ROOT / "src" / "mlflow_ai_assurance_lab"
    required = {
        "application.py",
        "scorers.py",
        "gate.py",
        "evidence.py",
        "evaluation.py",
        "tracking.py",
    }
    assert required <= {path.name for path in package.rglob("*.py")}


def test_security_policy_defines_private_channel_without_fictitious_sla() -> None:
    policy = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "contacto@vektoria.io" in policy
    assert "There is no response-time or remediation SLA" in policy
