from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_readme_exposes_foundation_status() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Foundation — implementation not started" in readme


def test_durable_contracts_exist() -> None:
    for relative_path in ("AGENTS.md", "GOALS.md", "PLANS.md"):
        assert (ROOT / relative_path).is_file(), relative_path


def test_project_metadata_pins_foundation_runtime() -> None:
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


def test_planned_mlflow_api_surface_is_importable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MLFLOW_DISABLE_AGENT_HINT", "1")

    import mlflow
    from mlflow.genai import evaluate
    from mlflow.genai.datasets import create_dataset
    from mlflow.genai.scorers import scorer

    assert mlflow.__version__ == "3.17.2"
    assert all(callable(item) for item in (mlflow.start_span, evaluate, create_dataset, scorer))


def test_phase_one_modules_do_not_exist() -> None:
    package = ROOT / "src" / "mlflow_ai_assurance_lab"
    forbidden = {
        "providers.py",
        "retrieval.py",
        "generation.py",
        "controls.py",
        "scorers.py",
        "gate.py",
        "evidence.py",
    }
    assert forbidden.isdisjoint(path.name for path in package.rglob("*.py"))


def test_security_policy_blocks_publication_without_private_channel() -> None:
    policy = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "No private reporting channel exists yet" in policy
    assert "Publication is blocked" in policy
