# Project goals

## Purpose and bounded assurance claim

This exploratory lab demonstrates a technical assurance chain from AI risk through controls and automated evaluation to a decision gate and inspectable evidence, with MLflow as the primary assurance tool.

Within documented assumptions and synthetic data, the governed variant should provide stronger and verifiable control coverage than the baseline. This bounded comparison does not demonstrate production safety, legal compliance, ISO conformity, certification, or complete audit readiness.

## Desired outcomes

- A synthetic-policy RAG application with intentionally distinct baseline and governed variants.
- MLflow traces that make the variants and relevant control behavior distinguishable.
- A versioned evaluation dataset using only publishable synthetic content.
- Deterministic offline scorers that require no model download, API key, SaaS service, or paid call.
- A configurable PASS/FAIL release gate with explicit non-zero failure behavior.
- A reproducible, machine-validated evidence pack.
- Governance documentation with bidirectional traceability and clearly bounded standards mappings.
- Secret-free CI exercising the required offline path.

## Success conditions

- A clean checkout can install and run the required workflow offline after dependencies are available from the lockfile.
- MLflow traces clearly distinguish baseline and governed behavior.
- The baseline fails controls that are intentionally absent and documented as such.
- The governed variant meets justified, versioned thresholds.
- Regressions and invalid, missing, or stale evidence produce a non-zero exit code.
- `make verify` passes.
- Every material risk links to a control, implementation, test, evidence, decision, and residual risk.

## Scope

- MLflow tracing, evaluation, datasets, scorers, and local tracking.
- Defensive tests for scope handling, refusal behavior, citations, leakage, and a clearly labeled groundedness proxy.
- Educational architecture crosswalks to NIST AI RMF 1.0, NIST AI 600-1, public ISO/IEC 42001 themes, selected current OWASP LLM risks, and relevant EU AI Act themes.
- An optional real-provider path that remains disabled by default and is never required for local verification or CI.

## Non-goals

- A production service or enterprise governance platform.
- Legal advice, a compliance determination, certification, or a complete GRC workflow.
- A complete model-registry or production-monitoring implementation.
- A custom web UI.
- Any evaluation or GRC platform other than MLflow.

## Constraints and evidence standard

- Use synthetic, public, publishable data and English public artifacts only.
- Lock compatible dependency versions and keep policies, thresholds, datasets, and schemas under version control.
- Use inspectable policy logic and persist no secrets or sensitive markers without redaction.
- Prefer measured, code-generated evidence over prose assertions.
- Label heuristics and proxies precisely; do not present them as semantic or legal proof.
- Separate observed results from recommendations and planned work.
- Regenerate and revalidate evidence after behavior, configuration, threshold, dataset, or schema changes.
- Do not fabricate results or conceal failure with a successful fallback.

Change this file only when the user explicitly changes project scope or success criteria.
