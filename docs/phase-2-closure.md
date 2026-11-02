# Phase 2 closure record

This record maps every requirement family from the Phase 2 master prompt to implemented,
executable evidence. It records the P2-07 rehearsal performed on 2026-11-02 from a clean Git
working tree before the closure edits. Phase 3 was not started.

## Final requirement matrix

| Requirement family | Implementation | Test or executable check | Evidence | Result |
|---|---|---|---|---|
| Repository, governance, CI, guidance, templates, and Dependabot audit | Repository contracts, least-privilege CI, issue/PR templates, and `uv`/Actions Dependabot configuration | `scripts/check_foundation.py`; `tests/test_foundation.py`; `make verify` | [source register](source-register.md), [plan](../PLANS.md), and CI workflow | Satisfied |
| Pinned MLflow API verification | MLflow `3.17.2` tracing, managed-dataset, evaluation, and scorer call shapes | `test_pinned_mlflow_api_surface_is_importable`; full offline evaluation | SRC-003 through SRC-007 and SRC-016 through SRC-022 in the [source register](source-register.md) | Satisfied |
| Unsupported claims, circular tests, proxy naming, mapping limits, and reproducibility review | Bounded scorer names, claim ledger, independent recomputation, source/input digests, and limited standards/threat mappings | Scorer, gate, evidence, foundation, and traceability tests | [scorer contracts](scorer-contracts.md), [claim ledger](claim-ledger.md), and [standards crosswalk](standards-crosswalk.md) | Satisfied |
| Versioned dataset with stable IDs, expected behavior, rationale, and valid scorers | Dataset schema `1.1`, eight stable cases, exact validation, five deterministic matching scorers | `tests/test_config.py`, `tests/test_scorers.py`, and `tests/test_application.py` | `data/evaluation/policy-assurance-v1.json`, case results, and [scorer contracts](scorer-contracts.md) | Satisfied |
| Negative release-gate, trace-redaction, and evidence-validation paths | Fail-closed gate validation, `persistence-redaction-v2`, and strict evidence validation | `tests/test_gate.py`, `tests/test_tracing.py`, and `tests/test_evidence.py` | Baseline gate exits `1`; invalid input tests require exit `2`; validated persistence and evidence fields | Satisfied |
| Manifest provenance and checksums | Evidence schemas `2.0` bind UTC, Git context, app/tool/input versions and digests, policy thresholds, MLflow IDs, and artifact hashes | Evidence generation plus current-input, schema, relation, safety, and checksum validation | [`manifest.json`](../evidence/sample/manifest.json) and [evidence provenance contract](evidence-provenance.md) | Satisfied |
| Volatile-field normalization | `material-assurance-v1` excludes only documented UTC, MLflow-ID, and Git-context volatility | Evidence comparison tests distinguish volatile-only changes from material drift | Manifest material digest and [comparison contract](evidence-provenance.md) | Satisfied |
| Per-control status, threshold, evidence, decision, and residual risk | Versioned control catalog and measured control derivation render machine and human views | `tests/test_controls.py`; repository reverse-link and rendered-matrix validation | [`control-status.json`](../evidence/sample/control-status.json) and generated [control matrix](control-matrix.md) | Satisfied |
| No unsafe configured content in persisted traces, logs, or artifacts | Uniform pre-persistence redaction and post-evaluation trace/runtime inspection | `tests/test_tracing.py`; evidence safety validation | `persistence_safe=true` in the sample and CTRL-TRACE-001/CTRL-REDACT-001 evidence | Satisfied within the configured-pattern boundary |
| Bounded OWASP/MITRE threat model | Demonstrated fixtures, partial analogues, non-applicable entries, and uncovered lifecycles are separated | Governance contract checks and repository link validation | [threat model](threat-model.md) and versioned primary sources | Satisfied |
| Bounded NIST/ISO/EU crosswalk | Public functions/categories/themes only; no legal, compliance, conformity, certification, or alignment conclusion | Governance contract checks and repository link validation | [standards crosswalk](standards-crosswalk.md) and [source register](source-register.md) | Satisfied |
| Assurance claim, evidence, assumptions, and limitations | Bounded assurance statement and eight-claim ledger | `test_governance_claim_contracts_are_explicit` | [assurance statement](assurance-statement.md) and [claim ledger](claim-ledger.md) | Satisfied |
| Findings with risk, lifecycle, control, evidence, gaps, enterprise fit, and recommendation | Observed results are separated from future recommendations | Governance contract checks and repository link validation | [Phase 2 findings](findings.md) | Satisfied |
| Final CI-equivalent gate, evidence regeneration, and observed plan record | Locked install followed by the exact `make verify` sequence; explicit failing baseline gate; code-generated final sample | P2-07 rehearsal and final rerun recorded in [PLANS.md](../PLANS.md) | Final run IDs, manifest hash, material digest, and command outcomes below | Satisfied |

## Observed closure rehearsal

- `make UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv setup` resolved 102 locked packages and
  installed the local project with Python 3.12.16 and uv 0.13.6.
- `make UV=/private/tmp/mlflow-ai-assurance-uv/bin/uv verify` passed Ruff lint and formatting,
  mypy over 23 source files, 61 pytest tests (with one upstream MLflow/SQLAlchemy deprecation
  warning), repository/documentation/link/traceability validation, offline evaluation, the
  governed gate, generated evidence validation, and committed sample validation.
- The final rehearsal evaluation produced baseline run `9f2d644661f14092bb9d24ca474cf602`
  with `FAIL` and governed run `448208ca8dda4db9818a1d0c4a1d23c3` with `PASS`.
- The explicit baseline gate returned exit `1` and listed all five failed metrics. Negative tests
  also observed exit `2` for invalid gate inputs without a success fallback.
- The code-generated committed sample has manifest SHA-256
  `1ca8a73689e0c3b1eb56482a63d22448fe2b51970adbb358829170651d0966ef`, material digest
  `94866a8b968fda33013a75971ed7caab24f929d83e8ee738b2fbf299129f1c1a`, and application-source
  digest `834aba66333986d955f9fce23658f9fb1a0de208ebbda92f479c8396e0f10348`.
- Comparing the independently generated rehearsal pack with the final sample returned
  `material_match=true` and `classification=identical`.
- `git diff --check` passed. Explicit scans found no credential-shaped values or personal absolute
  paths in the publishable tree and no configured raw marker or prohibited prompt phrase in the
  committed evidence.

## Residual risk and manual actions

The bounded residual risks in the [risk assessment](risk-assessment.md) remain accepted for this
portfolio-scale synthetic lab. The evidence is local, unsigned, independently untimestamped, and
not append-only; the cases and configured redaction patterns are narrow; lexical and citation-ID
matching are not semantic or factual validation; and no independent enterprise release review or
production monitoring exists.

Before publication, the maintainer must configure a private security contact or GitHub Private
Vulnerability Reporting, enable hosted Dependabot alerts and security updates, confirm the public
reporting path, and observe the hosted CI run after an authorized push. These hosted actions were
not performed during P2-07.

## Decision

`CLOSE PHASE 2`. All Phase 2 acceptance criteria have executable or generated evidence, no
unresolved Phase 2 implementation gap was found, and the remaining limitations are explicit and
compatible with the bounded claim. Phase 3 remains `Not started`.
