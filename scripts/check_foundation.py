"""Validate repository structure and implemented offline-assurance consistency."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import yaml

from mlflow_ai_assurance_lab.control_catalog import (
    ControlCatalogError,
    load_control_catalog,
)
from mlflow_ai_assurance_lab.controls import (
    ControlTraceabilityError,
    render_control_matrix,
    validate_static_traceability,
)

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "__pycache__"}
REQUIRED_FILES = {
    ".env.example",
    ".github/ISSUE_TEMPLATE/assurance_gap.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/dependabot.yml",
    ".github/pull_request_template.md",
    ".github/workflows/ci.yml",
    ".python-version",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "GOALS.md",
    "LICENSE",
    "Makefile",
    "PLANS.md",
    "README.md",
    "RELEASE_READINESS.md",
    "SECURITY.md",
    "config/control-catalog-v1.json",
    "config/release-policy-v1.json",
    "data/evaluation/policy-assurance-v1.json",
    "data/policies/policies-v1.json",
    "docs/ai-system-card.md",
    "docs/architecture-decisions.md",
    "docs/adr/0001-planned-assurance-architecture.md",
    "docs/assurance-statement.md",
    "docs/claim-ledger.md",
    "docs/control-matrix.md",
    "docs/demo-script.md",
    "docs/evidence-provenance.md",
    "docs/findings.md",
    "docs/human-oversight.md",
    "docs/interview-notes.md",
    "docs/phase-2-closure.md",
    "docs/risk-assessment.md",
    "docs/scorer-contracts.md",
    "docs/source-register.md",
    "docs/standards-crosswalk.md",
    "docs/threat-model.md",
    "evidence/sample/manifest.json",
    "evidence/sample/report.md",
    "pyproject.toml",
    "uv.lock",
}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^]]+]\(([^)]+)\)")
SECRET_PATTERNS = {
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
}
RISK_ID = re.compile(r"\bRISK-[A-Z]+-\d{3}\b")
CONTROL_ID = re.compile(r"\bCTRL-[A-Z]+-\d{3}\b")


def repository_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and not EXCLUDED_PARTS.intersection(path.parts)
        and "mlflow-ai-assurance-lab-prompts" not in path.parts
    ]


def validate_required_files(errors: list[str]) -> None:
    for relative_path in sorted(REQUIRED_FILES):
        if not (ROOT / relative_path).is_file():
            errors.append(f"missing required file: {relative_path}")


def validate_yaml(errors: list[str]) -> None:
    yaml_paths = sorted((ROOT / ".github").rglob("*.yml"))
    for path in yaml_paths:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"invalid YAML in {path.relative_to(ROOT)}: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"YAML root must be a mapping: {path.relative_to(ROOT)}")

    dependabot = yaml.safe_load((ROOT / ".github/dependabot.yml").read_text(encoding="utf-8"))
    ecosystems = {update["package-ecosystem"] for update in dependabot["updates"]}
    if ecosystems != {"github-actions", "uv"}:
        errors.append(f"unexpected Dependabot ecosystems: {sorted(ecosystems)}")

    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for required_text in ("contents: read", "uv sync --locked --dev", "make verify"):
        if required_text not in workflow:
            errors.append(f"CI is missing required text: {required_text}")
    if "secrets." in workflow:
        errors.append("Required offline CI must not reference GitHub Actions secrets")


def validate_markdown_links(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.md")):
        excluded = EXCLUDED_PARTS.intersection(path.parts)
        if excluded or "mlflow-ai-assurance-lab-prompts" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            parsed = urlparse(target)
            if parsed.scheme in {"https", "mailto"}:
                continue
            if parsed.scheme or target.startswith("#"):
                if parsed.scheme and parsed.scheme not in {"http", "https", "mailto"}:
                    errors.append(f"unsupported link scheme in {path.relative_to(ROOT)}: {target}")
                continue
            local_target = unquote(target.split("#", 1)[0])
            if local_target and not (path.parent / local_target).resolve().exists():
                errors.append(f"broken local link in {path.relative_to(ROOT)}: {target}")


def validate_public_files(errors: list[str]) -> None:
    for path in repository_files():
        if path.suffix not in {
            ".json",
            ".md",
            ".py",
            ".toml",
            ".yml",
            ".yaml",
            ".example",
            "",
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        personal_path_markers = ("/" + "Users/", "/" + "home/", "C:\\" + "Users\\")
        if any(marker in text for marker in personal_path_markers):
            errors.append(f"personal absolute path in {path.relative_to(ROOT)}")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"possible {label} in {path.relative_to(ROOT)}")


def validate_implemented_scope(errors: list[str]) -> None:
    package = ROOT / "src/mlflow_ai_assurance_lab"
    required_package_files = {
        "__init__.py",
        "__main__.py",
        "application.py",
        "config.py",
        "control_catalog.py",
        "controls.py",
        "domain.py",
        "evaluation.py",
        "evidence.py",
        "gate.py",
        "py.typed",
        "redaction.py",
        "scorers.py",
        "tracking.py",
    }
    observed = {path.name for path in package.iterdir() if path.is_file()}
    if not required_package_files <= observed:
        errors.append(
            f"functional MVP package files are missing: {sorted(required_package_files - observed)}"
        )

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "local portfolio review complete; publication controls pending" not in readme:
        errors.append("README does not expose the current Phase 3 release-review status")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if not license_text.startswith("MIT License\n"):
        errors.append("LICENSE is not the MIT License")

    project_metadata = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    if 'license = "MIT"' not in project_metadata:
        errors.append("project metadata does not declare the MIT License")


def validate_traceability(errors: list[str]) -> None:
    risk_text = (ROOT / "docs/risk-assessment.md").read_text(encoding="utf-8")
    matrix_text = (ROOT / "docs/control-matrix.md").read_text(encoding="utf-8")
    risks = set(RISK_ID.findall(risk_text))
    try:
        catalog = load_control_catalog()
        validate_static_traceability(catalog=catalog)
    except (ControlCatalogError, ControlTraceabilityError) as exc:
        errors.append(f"invalid measured control traceability: {exc}")
        return
    catalog_risks = set(catalog["risk_ids"])
    if risks != catalog_risks:
        errors.append(
            "risk/control catalog coverage mismatch: "
            f"missing={sorted(risks - catalog_risks)}, extra={sorted(catalog_risks - risks)}"
        )
    documented_risk_controls: dict[str, set[str]] = {}
    for line in risk_text.splitlines():
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) >= 7 and RISK_ID.fullmatch(cells[1]):
            documented_risk_controls[cells[1]] = set(CONTROL_ID.findall(cells[5]))
    expected_risk_controls = {
        risk_id: {item["control_id"] for item in catalog["controls"] if risk_id in item["risk_ids"]}
        for risk_id in catalog_risks
    }
    if documented_risk_controls != expected_risk_controls:
        errors.append("risk assessment control links are stale relative to the control catalog")

    control_status = json.loads(
        (ROOT / "evidence/sample/control-status.json").read_text(encoding="utf-8")
    )
    machine_controls = {item["control_id"] for item in control_status["controls"]}
    catalog_controls = {item["control_id"] for item in catalog["controls"]}
    if machine_controls != catalog_controls:
        errors.append(
            "catalog/machine control coverage mismatch: "
            f"missing={sorted(catalog_controls - machine_controls)}, "
            f"extra={sorted(machine_controls - catalog_controls)}"
        )
    matrix_controls = set(CONTROL_ID.findall(matrix_text))
    if matrix_controls != catalog_controls:
        errors.append(
            "human/catalog control coverage mismatch: "
            f"missing={sorted(catalog_controls - matrix_controls)}, "
            f"extra={sorted(matrix_controls - catalog_controls)}"
        )
    if matrix_text != render_control_matrix(control_status):
        errors.append("human control matrix is stale relative to measured machine evidence")


def main() -> int:
    errors: list[str] = []
    validate_required_files(errors)
    validate_yaml(errors)
    validate_markdown_links(errors)
    validate_public_files(errors)
    validate_implemented_scope(errors)
    validate_traceability(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository and offline-assurance validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
