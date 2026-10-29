"""Validate repository structure and functional-MVP consistency."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import yaml

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
    "SECURITY.md",
    "config/release-policy-v1.json",
    "data/evaluation/policy-assurance-v1.json",
    "data/policies/policies-v1.json",
    "docs/ai-system-card.md",
    "docs/adr/0001-planned-assurance-architecture.md",
    "docs/control-matrix.md",
    "docs/findings.md",
    "docs/human-oversight.md",
    "docs/risk-assessment.md",
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
        errors.append("Phase 0 CI must not reference GitHub Actions secrets")


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


def validate_scope(errors: list[str]) -> None:
    package = ROOT / "src/mlflow_ai_assurance_lab"
    required_package_files = {
        "__init__.py",
        "__main__.py",
        "application.py",
        "config.py",
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
    if "Functional offline assurance MVP" not in readme:
        errors.append("README does not expose the required Phase 1 status")

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
    matrix_risks = set(RISK_ID.findall(matrix_text))
    if risks != matrix_risks:
        errors.append(
            "risk/control matrix coverage mismatch: "
            f"missing={sorted(risks - matrix_risks)}, extra={sorted(matrix_risks - risks)}"
        )

    control_status = json.loads(
        (ROOT / "evidence/sample/control-status.json").read_text(encoding="utf-8")
    )
    machine_controls = {item["control_id"] for item in control_status["controls"]}
    matrix_controls = set(CONTROL_ID.findall(matrix_text))
    if machine_controls != matrix_controls:
        errors.append(
            "human/machine control coverage mismatch: "
            f"missing={sorted(machine_controls - matrix_controls)}, "
            f"extra={sorted(matrix_controls - machine_controls)}"
        )
    for item in control_status["controls"]:
        test_path, separator, test_name = item["test"].partition("::")
        if not separator or not (ROOT / test_path).is_file():
            errors.append(f"invalid control test link: {item['test']}")
        elif f"def {test_name}(" not in (ROOT / test_path).read_text(encoding="utf-8"):
            errors.append(f"missing linked test function: {item['test']}")
        evidence_path = item["evidence"].split("#", 1)[0]
        if not (ROOT / "evidence/sample" / evidence_path).is_file():
            errors.append(f"missing linked evidence file: {item['evidence']}")


def main() -> int:
    errors: list[str] = []
    validate_required_files(errors)
    validate_yaml(errors)
    validate_markdown_links(errors)
    validate_public_files(errors)
    validate_scope(errors)
    validate_traceability(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository and functional-MVP validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
