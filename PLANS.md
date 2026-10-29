# Project plan

This roadmap records planned work and observed verification evidence. Allowed statuses are `Not started`, `In progress`, `Blocked`, and `Complete`.

## Phase 0 — Repository foundation and source validation

**Status:** Complete

**Objective:** Establish durable repository contracts, a minimal reproducible Python scaffold, primary-source decisions, contribution and security controls, and foundation-only automated checks.

**Required outputs:**

- Repository contracts: `AGENTS.md`, `GOALS.md`, and this plan.
- Foundation README, contribution and pre-release security policies, license, environment example, ignore rules, Python project metadata, dependency lockfile, package/test directories, and a real `make verify` entry point.
- Primary-source register and an initial architecture decision record, with all future lab behavior labeled `Planned`.
- GitHub pull request and issue templates, Dependabot configuration, and least-privilege CI covering only implemented foundation checks.
- Structural smoke tests that do not simulate future assurance capabilities.

**Acceptance criteria:**

- A reasonably clean environment installs dependencies from the lockfile without API keys, SaaS calls, paid services, or model downloads.
- All documented Phase 0 checks pass, including YAML and link validation, repository consistency checks, and `make verify`.
- CI, templates, paths, labels, and commands agree with repository content.
- No credentials, personal paths, caches, generated artifacts, or unsupported assurance/compliance claims are committed.
- `git diff --check` passes when Git is available.
- No Phase 1 behavior is implemented or simulated.

**Verification evidence:**

- `git init` — initialized an empty local repository on branch `main`; no remote or commit was created.
- Official-source review on 2026-10-29 — confirmed Python 3.12 support status, uv lock/sync behavior, MLflow 3.17.2 release metadata and planned APIs, the SQL-backend requirement for evaluation datasets, local SQLite tracking, NIST AI RMF 1.0 and AI 600-1, the public ISO/IEC 42001 overview, OWASP GenAI LLM Top 10 2026, current EU AI Act materials, and GitHub CI/Dependabot configuration. Sources and limits are recorded in `docs/source-register.md`.
- `/private/tmp/mlflow-ai-assurance-uv/bin/uv lock` — resolved 102 packages with Python 3.12.16 and generated `uv.lock`.
- `/private/tmp/mlflow-ai-assurance-uv/bin/uv sync --locked --dev` — created `.venv` and installed the locked project plus 98 packages, including MLflow 3.17.2.
- Planned MLflow import smoke check — observed MLflow `3.17.2`; `mlflow.start_span`, `mlflow.genai.evaluate`, `mlflow.genai.datasets.create_dataset`, and `mlflow.genai.scorers.scorer` were importable and callable. No capability was executed.
- `make UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv verify` — after the MIT license update, lock check resolved 102 packages; Ruff lint passed; Ruff reported 3 files formatted; mypy reported no issues in 3 source files; pytest reported 7 passed; foundation validation passed.
- Installed package metadata check — observed `License-Expression: MIT` and `License :: OSI Approved :: MIT License`; a repository-wide case-insensitive search found no references to the former license outside ignored local prompts.
- External-link check across README, contributing guidance, and the source register — checked 16 unique HTTPS links: 15 returned successful HTTP statuses; ISO returned HTTP 403 to the scripted client, while its official page was separately accessible during primary-source review.
- `git diff --check` and `git diff --cached --check` — exited successfully with no output. Because this is a new repository with untracked files, a separate repository-wide trailing-whitespace scan was also run and found no matches.
- Repository-wide credential-pattern and personal-path scans — found no matches outside ignored local prompts and the lockfile exclusions. The claim review found only bounded/non-claim language plus standard license text.
- Final scope inspection — the package contains only `__init__.py` and `py.typed`; no retrieval, generation, controls, traces, datasets, scorers, gates, providers, evidence generation, MLflow state, or generated evidence directories exist.

## Phase 1 — Functional offline assurance MVP

**Status:** Not started

**Objective:** Implement a deterministic vertical slice comparing synthetic-policy RAG baseline and governed variants through MLflow-backed assurance.

**Required outputs:** Planned baseline/governed implementations, distinguishable MLflow traces, a versioned synthetic evaluation dataset, deterministic offline scorers, a configurable PASS/FAIL release gate, and initial generated evidence.

**Acceptance criteria:** Planned checks must demonstrate intentional baseline control gaps, justified governed thresholds, non-zero exits for regressions, and fully offline reproducibility.

**Verification evidence:** Not run.

## Phase 2 — Assurance and evidence hardening

**Status:** Not started

**Objective:** Harden bidirectional traceability, evidence integrity, negative paths, security controls, and defensible governance documentation.

**Required outputs:** Planned risk/control/test/evidence crosswalks, validated evidence schemas, redaction and leakage defenses, negative-path tests, standards mapping limits, residual-risk records, and regeneration controls.

**Acceptance criteria:** Planned validation must connect every material risk to controls, tests, evidence, decisions, and residual risk while rejecting invalid or stale evidence.

**Verification evidence:** Not run.

## Phase 3 — Independent portfolio and release review

**Status:** Not started

**Objective:** Perform an independent public-portfolio and release-readiness review without overstating the lab's assurance claim.

**Required outputs:** Planned independent review findings, corrected public narrative, reproducibility review, release checklist, and documented limitations and manual publication actions.

**Acceptance criteria:** Planned review must confirm a clean offline checkout, coherent claims and evidence, safe public artifacts, and explicit release decisions and open risks.

**Verification evidence:** Not run.

## Decision log

- 2026-10-29: Phase 0 started under the strict foundation-only scope in `mlflow-ai-assurance-lab-prompts/01-repository-foundation.md`.
- 2026-10-29: Selected Python 3.12.16 and uv 0.13.6 with a committed universal lockfile. Python 3.12 remains supported, and the narrower runtime avoids adopting a prerelease branch while keeping the MLflow environment reproducible.
- 2026-10-29: Pinned MLflow 3.17.2, the current stable patch release observed on PyPI. Only its planned import surface was smoke-tested; behavioral verification is deferred to Phase 1.
- 2026-10-29: Planned SQLite-backed local MLflow tracking because evaluation datasets require SQL and the mandatory path cannot depend on hosted infrastructure.
- 2026-10-29: Selected the MIT License at the user's explicit direction and applied it across the license text, package metadata, public README, tests, and structural validation. The `src` package layout uses Ruff, mypy, pytest, and a repository-specific structural validator.
- 2026-10-29: Kept the initial standards/regulatory mapping educational and bounded to public primary sources; no ISO clauses, legal conclusions, compliance claims, or certification claims are included.
- 2026-10-29: Kept security reporting as an explicit pre-publication blocker because no real private contact exists. Hosted security settings require manual maintainer action.

## Surprises and discoveries

- 2026-10-29: The starting directory contains the four implementation prompts and a macOS `.DS_Store`; it is not yet a Git repository.
- 2026-10-29: The host provides Python 3.13.5; primary-source review led to a separate pinned Python 3.12.16 environment managed by uv.
- 2026-10-29: uv provisioned Python 3.12.16 independently of the host Python, so the selected runtime installed cleanly without changing the system interpreter.
- 2026-10-29: MLflow evaluation datasets require a SQL backend; the future local architecture therefore cannot rely on FileStore.
- 2026-10-29: Automated HTTP validation received a 403 from the official ISO page, although the same official page was accessible through the research browser. This is recorded as bot filtering, not evidence of a broken link.

## Outcomes and retrospective

Phase 0 is complete. The repository now has durable contracts, a locked and verified Python foundation, source-backed architecture decisions, pre-release collaboration and security controls, and checks limited to capabilities that actually exist. The security reporting contact and hosted GitHub security settings remain manual pre-publication actions. Phase 1 has not started and requires the separate Phase 1 prompt.
