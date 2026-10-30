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

**Status:** Complete

**Objective:** Implement a deterministic vertical slice comparing synthetic-policy RAG baseline and governed variants through MLflow-backed assurance.

**Required outputs:** Implemented baseline/governed synthetic-policy RAG variants, distinguishable
MLflow traces, a versioned managed evaluation dataset, five deterministic offline scorers, a
configurable PASS/FAIL release gate, generated evidence, and connected governance artifacts.

**Acceptance criteria:** Checks demonstrate intentional baseline control gaps, governed results at
the versioned thresholds, non-zero exits for regressions, trace redaction, evidence integrity, and
offline reproducibility after locked setup.

**Verification evidence:**

- Official-source review on 2026-10-29 — rechecked MLflow tracing, evaluation datasets,
  `mlflow.genai.evaluate()`, code-based scorers, local tracking and masking guidance; NIST AI RMF
  1.0 and AI 600-1; the public ISO/IEC 42001 overview; OWASP LLM Top 10 2026 identifiers; and
  European Commission AI Act themes. Decisions and limits are in `docs/source-register.md`.
- `make UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv setup` — resolved 102 locked packages, built
  the local editable project, and completed without changing the dependency graph.
- `make UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv demo` — produced baseline and governed
  traces for a supported and out-of-scope query; baseline answered the out-of-scope case while
  governed returned `refuse_scope`.
- MLflow sample evaluation runs `ce8f1878982047bf8f4ea898d242ed92` (baseline) and
  `4752cfac64374f96955b84d83f444c9c` (governed) each produced eight trace-linked case results.
  Baseline metrics were citation `0.25`, scope `0.875`, leakage prevention `0.875`, refusal
  `0.375`, and groundedness proxy `0.25`, resulting in `FAIL`. Governed scored `1.0` on all five
  metrics and resulted in `PASS`.
- `evidence/sample/manifest.json` — generated from the measured results; manifest SHA-256
  `3b5bca101cab967919d2a1fddbbd91a4c2a18514a605e5a2f8603887efcacf91`. The validator confirmed
  source digests, file hashes, all eight case IDs per variant, ten control links, expected
  decisions, and absence of configured sensitive markers.
- `make UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv verify` — lock check resolved 102 packages;
  Ruff lint and format passed; mypy found no issues in 19 files; pytest reported 17 passed with one
  MLflow/SQLAlchemy deprecation warning; repository/traceability validation passed; offline
  evaluation observed baseline `FAIL` and governed `PASS`; the governed gate passed; regenerated
  and committed evidence packs validated.
- Negative paths — `tests/test_gate.py::test_regression_makes_gate_fail` observed exit code `1`
  for a governed citation regression; tampered evidence and missing metrics were rejected; the
  trace test confirmed the raw synthetic marker was scoreable but absent from persisted trace JSON.
- `git diff --check`, repository-wide sensitive-marker/personal-path checks, and secret-pattern
  scans completed with no findings in publishable artifacts. Runtime MLflow databases and
  regenerated evidence remain ignored under `artifacts/`.

## Phase 2 — Assurance and evidence hardening

**Status:** In progress

**Objective:** Harden bidirectional traceability, evidence integrity, negative paths, security controls, and defensible governance documentation.

**Required outputs:** Planned risk/control/test/evidence crosswalks, validated evidence schemas, redaction and leakage defenses, negative-path tests, standards mapping limits, residual-risk records, and regeneration controls.

**Acceptance criteria:** Planned validation must connect every material risk to controls, tests, evidence, decisions, and residual risk while rejecting invalid or stale evidence.

**Verification evidence:**

- 2026-10-30: P2-00 read-only gap analysis received explicit human approval; P2-01 began as the
  first accepted mutation. Later Phase 2 requirements remain unimplemented until their owning
  increments are reviewed.
- Official MLflow tag `v3.17.2` source review plus installed-package signature inspection —
  confirmed the implemented manual tracing, trace search, GenAI evaluation, managed dataset, and
  custom scorer call shapes. Exact sources, decisions, and limits are recorded in
  `docs/source-register.md`; no dependency migration was needed.
- `make UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv repository` — repository and
  offline-assurance validation passed. The focused contract test run reported 7 passed.
- `make UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv verify` — lock check resolved 102 packages;
  Ruff lint and format passed with 19 files already formatted; mypy found no issues in 19 files;
  pytest reported 17 passed with one upstream MLflow/SQLAlchemy deprecation warning; repository
  validation passed; evaluation runs `e396f3597ac5447aab9e3c0a39edff05` (baseline) and
  `702b56c9f70343adbf065ae831e62a66` (governed) produced expected `FAIL`/`PASS` decisions; the
  governed gate passed; generated and committed sample evidence both validated.
- `git diff --check` — exited successfully with no output after the P2-01 contract changes.
- P2-02 retained all eight stable case IDs and the five `1.0` thresholds while moving the dataset
  to schema `1.1` with per-case rationale and fail-closed validation of structure, types,
  uniqueness, category/action and risk/control vocabularies, and expected citation presence in the
  versioned corpus. Five renamed scorer contracts now state only ID, action, configured-marker, and
  lexical matching claims; focused config/scorer/application/gate tests reported 19 passed.
- `make UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv verify` — lock check resolved 102 packages;
  Ruff lint and format passed with 20 files formatted; mypy found no issues in 20 files; pytest
  reported 29 passed with one upstream MLflow/SQLAlchemy deprecation warning; repository
  validation passed. Final evaluation runs `9fbabaf9e15d430f99fd10a3c3944482` (baseline) and
  `71129f968070454bbfabafc1d8a2c8df` (governed) each covered eight cases and produced expected
  `FAIL`/`PASS` decisions. Baseline metrics remained `0.25`, `0.875`, `0.875`, `0.375`, and `0.25`
  for citation-source match, scope-action match, synthetic-marker absence, expected-action match,
  and lexical-response match; governed scored `1.0` on all five. The governed gate and generated
  and committed evidence validation passed.
- `evidence/sample/manifest.json` — regenerated from the measured P2-02 inputs and scorer names;
  manifest SHA-256 `0c5f1b5dd8a182c851bcf5f8ecfeeaa7b5125d90aee8ac7132c34032b8c25a76`.
- P2-03 hardened the gate against missing, extra, non-numeric, non-finite, and out-of-range metrics;
  policy/result mismatches; stale policy digests; and recorded decisions or failed-metric lists that
  disagree with recomputation. Focused gate/config/tracing/evidence tests reported 26 passed. CLI
  tests observed exit `1` for a valid measured regression and exit `2` for invalid inputs, with no
  successful fallback.
- `persistence-redaction-v2` centralized the configured synthetic-marker, credential-shape, and
  prohibited-prompt patterns and applies them to trace inputs, outputs, attributes, tags, metadata,
  and mapping keys. The integration tests confirmed raw baseline leakage remained scoreable before
  persistence, inspected the stored MLflow trace and runtime files, and observed a redaction
  contract failure before a new trace was created. The claim remains limited to configured
  patterns and is not general PII, secret, or prompt-injection detection.
- `make UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv verify` — lock check resolved 102 packages;
  Ruff lint and format passed with 20 files formatted; mypy found no issues in 20 files; pytest
  reported 43 passed with one upstream MLflow/SQLAlchemy deprecation warning; repository
  validation passed. Evaluation runs `36fc7c4a6a6043cca82ea81a2e268093` (baseline) and
  `e31de8ff672248a48f6154b907fba2c3` (governed) produced expected `FAIL`/`PASS` decisions and the
  prior metric values; the governed gate and generated and committed evidence validation passed.
- `evidence/sample/manifest.json` — regenerated after the persistence-boundary and control-link
  changes; manifest SHA-256 `8062d95cb10f24ec3c709d94c0f12c9f600914954688322f3d98827ebd54de7a`.
- P2-04 replaced the hardcoded control-status tuple with versioned static metadata in
  `config/control-catalog-v1.json` and derived governed/baseline observations in control-status
  schema `2.0`. Metric controls use release-policy thresholds and aggregate or named-case scores;
  non-metric controls state trace-coverage, expected-decision, or evidence-precondition rules.
  The generated human matrix and machine-readable rows now share the same renderer and measured
  semantics, including MLflow run/trace or case anchors, decision contribution, and residual risk.
- Focused control/evidence/config/gate tests reported 30 passed. The controlled citation regression
  changed `CTRL-CITE-001` and the governed decision to `FAIL`. Negative tests rejected a material
  `PASS` field in static metadata, unknown risk and case IDs, empty test/evidence links, and a
  re-hashed but contradictory measured control row.
- `make UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv verify` — lock check resolved 102 packages;
  Ruff lint and format passed with 23 files formatted; mypy found no issues in 23 files; pytest
  reported 50 passed with one upstream MLflow/SQLAlchemy deprecation warning; repository and
  bidirectional traceability validation passed. Evaluation runs
  `e579fd86116b47418f2ec4ecf83a34b6` (baseline) and
  `a2b5a63940c44a0f9671171b80e17595` (governed) produced expected `FAIL`/`PASS` decisions, the
  governed gate passed, and generated and committed evidence validation passed.
- `evidence/sample/manifest.json` — regenerated from measured runs
  `0312ca25235c4349a215bdc0f770f7c1` (baseline) and
  `194c9cb72ed04d319c52826a9264da07` (governed); manifest SHA-256
  `b69cef2195425049f6b5ceddcef37a0ee92aa033274c95e24972b9274ed50e6b`.
- P2-05 versioned the evaluation result, summary, case-results, and manifest contracts at schema
  `2.0` while retaining control-status schema `2.0`. Exact-field and type validation now binds the
  application source, installed application/MLflow/Python versions, Git commit plus working-tree
  marker, dataset/corpus/policy/catalog versions and SHA-256 digests, policy thresholds, MLflow
  experiment/run/trace anchors, normalized UTC, and generated artifact checksums without storing
  local or personal paths.
- The `material-assurance-v1` comparison profile recomputes a material digest after removing only
  documented UTC, MLflow-ID, and Git-context volatility. Focused config/control/gate/evidence tests
  reported 40 passed; evidence tests rejected missing files, stale inputs, unknown schemas,
  missing/wrong-typed fields, checksum changes, contradictory relations and control status, and
  prohibited content even when its artifact checksum was updated. Comparison tests distinguished
  timestamp-only volatility from a coherent material metric drift.
- `make UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv verify` — lock check resolved 102 packages;
  Ruff lint and format passed with 23 files formatted; mypy found no issues in 23 files; pytest
  reported 60 passed with one upstream MLflow/SQLAlchemy deprecation warning; repository
  validation passed. Evaluation runs `80c1a91178df46c8bada4870e968dcbe` (baseline) and
  `23dd9fb6914c43e5a229244c34dece43` (governed) produced expected `FAIL`/`PASS` decisions, the
  governed gate passed, and generated and committed evidence validation passed.
- `evidence/sample/manifest.json` — regenerated only through the evidence command from the final
  measured runs and explicitly revalidated. Manifest SHA-256 is
  `1fa0a279123e5bef0314f3c5438ed8d3ec1356eff5e073f46104e2fc5a195559`; material digest is
  `94866a8b968fda33013a75971ed7caab24f929d83e8ee738b2fbf299129f1c1a`; application-source digest
  is `834aba66333986d955f9fce23658f9fb1a0de208ebbda92f479c8396e0f10348`.

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
- 2026-10-29: Implemented Phase 1 with manual MLflow spans and a pre-persistence redaction boundary.
  This preserves raw output for the deterministic leakage scorer without persisting configured
  synthetic-sensitive markers.
- 2026-10-29: Set all governed scorer thresholds to `1.0` because every one of the eight
  deterministic cases is a release requirement. The intentionally limited baseline must remain
  `FAIL`; an unexpected baseline pass or governed fail is an evaluation error.
- 2026-10-29: Kept LLM-as-a-judge and real providers disabled and unimplemented in the required
  path. Any later extension must remain optional and document cost, variability, data boundaries,
  and secret handling.
- 2026-10-30: Began Phase 2 through the approved human-gated execution sequence. P2-01 is limited
  to repository/CI contract alignment and pinned MLflow API verification; dataset, scorer,
  security-path, traceability, evidence-provenance, and governance changes remain assigned to
  later increments.
- 2026-10-30: P2-02 preserved the dataset identity, all stable case IDs, and the strict `1.0`
  thresholds. Dataset schema `1.1` adds reviewable rationale and executable validation. Scorers
  were renamed to bounded matching claims because the implementation does not establish semantic
  truth, factual correctness, general sensitive-data absence, or complete scope classification.
  P2-03 security and persistence negative paths remained unimplemented pending human review.
- 2026-10-30: P2-03 retained the dataset, scorer, threshold, evidence-manifest, and control-status
  schemas. It added fail-closed gate/result validation and versioned the narrow persistence policy
  as `persistence-redaction-v2`; raw application output remains available only before the safe
  persistence boundary. At P2-03 completion, P2-04 measured control status and traceability was
  still unimplemented pending human review.
- 2026-10-30: P2-04 made `config/control-catalog-v1.json` the source for static control intent and
  references while deriving all material status from measured results and configuration. Baseline
  observations remain separate from the governed release decision. The existing manifest gained
  only the control-catalog binding needed for this increment; complete provenance remains assigned
  to P2-05, and the standards review remains assigned to P2-06.
- 2026-10-30: P2-05 made source/input/tool provenance and per-artifact schemas explicit and added
  a machine comparison that excludes only documented volatile or normalizable fields. Current
  input and source drift fails validation; coherent result drift changes the material digest.
  Evidence remains unsigned and locally timestamped, and a `dirty` Git marker requires reviewer
  judgment. Governance claims and standards review remain assigned to P2-06.

## Surprises and discoveries

- 2026-10-29: The starting directory contains the four implementation prompts and a macOS `.DS_Store`; it is not yet a Git repository.
- 2026-10-29: The host provides Python 3.13.5; primary-source review led to a separate pinned Python 3.12.16 environment managed by uv.
- 2026-10-29: uv provisioned Python 3.12.16 independently of the host Python, so the selected runtime installed cleanly without changing the system interpreter.
- 2026-10-29: MLflow evaluation datasets require a SQL backend; the future local architecture therefore cannot rely on FileStore.
- 2026-10-29: Automated HTTP validation received a 403 from the official ISO page, although the same official page was accessible through the research browser. This is recorded as bot filtering, not evidence of a broken link.
- 2026-10-29: Common stopwords initially made an unsupported parental-leave query appear supported,
  and a low-score untrusted document initially caused a valid incident-retention query to be
  refused. Focused runs exposed both defects; stopword filtering and a relevance threshold for
  indirect-injection inspection corrected them without lowering release thresholds.
- 2026-10-29: `uv run` attempted isolated package rebuilding after source changes in the
  network-restricted sandbox. The documented workflow now makes setup explicit and uses
  `uv run --locked --no-sync` for checks after setup; CI already performs locked sync first.
- 2026-10-30: GitHub returned HTTP 403 when P2-01 attempted to inspect hosted rulesets for the
  private repository, stating that the feature requires GitHub Pro or a public repository. No
  hosted setting was changed; local CI remains least privilege and the renamed job will be
  verified by the next hosted run after an authorized push.
- 2026-10-30: The first local `make test` invocation for P2-02 did not start pytest because `uv`
  was absent from the shell `PATH`; the documented `UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv`
  override used by prior verification was available, and the rerun reported 17 passed before any
  P2-02 mutation.
- 2026-10-30: P2-03 found that Python's JSON parser accepted `NaN` and the previous comparison
  treated it as satisfying every threshold. It also found that `case_id` values used in trace
  attributes/tags were outside the prior query/output redaction calls. Finite-range validation and
  uniform pre-persistence redaction closed both paths without changing measured scorer outcomes.
- 2026-10-30: P2-04 reverse-link validation found that `RISK-GROUND-001` named three controls in
  the human risk assessment while `CTRL-REFUSE-001` also linked back to that risk. The risk row was
  corrected, and repository validation now compares every documented risk/control edge with the
  versioned catalog rather than checking identifier presence alone.

## Outcomes and retrospective

Phase 0 and Phase 1 are complete. The repository contains a functional, deterministic offline
assurance vertical slice with MLflow traces, a managed evaluation dataset, measured baseline and
governed comparison, strict release gate, generated evidence, governance documentation, and
secret-free CI. Phase 2 is in progress through independently reviewed increments; the P2-01
repository/CI alignment, P2-02 dataset/scorer validity, P2-03 negative gate and persistence
security, P2-04 measured control traceability, and P2-05 evidence provenance/reproducibility
increments are implemented. P2-06 and later hardening remain unimplemented pending their human
gates. The security reporting contact and hosted GitHub security settings remain manual
pre-publication actions.
