# ADR 0001: Local assurance architecture

- **Date:** 2026-10-29
- **Scope:** Mandatory deterministic offline assurance path

## Context

The lab needs one mandatory path that is deterministic, inspectable, secret-free, and runnable
locally and in CI. It compares an intentionally limited baseline with a governed variant while
preserving traceability through MLflow.

MLflow evaluation datasets require a SQL backend. Built-in LLM judges may make provider calls, so
they are unsuitable for the mandatory offline path. The public repository must also keep synthetic
inputs, policy logic, thresholds, and generated evidence inspectable.

## Decision

1. Use Python 3.12, uv, and the committed lockfile for the required runtime.
2. Use one deterministic offline provider implemented as explicit local code with no model download
   or network fallback. Any optional real provider must remain disabled by default and outside
   required verification.
3. Keep shared synthetic corpus and typed contracts separate from baseline and governed
   orchestration. The variants have distinct entry points and trace attributes.
4. Use MLflow 3.17.2 as the sole evaluation and assurance platform. Store traces, datasets, and
   evaluation results in local MLflow tracking backed by SQLite, with runtime artifacts in ignored
   generated directories.
5. Use versioned synthetic evaluation cases and deterministic code-based MLflow scorers. Label any
   groundedness heuristic as a proxy, not semantic correctness proof.
6. Apply a versioned release policy after evaluation and emit a machine-validated evidence pack
   linking risks, controls, tests, run/trace identifiers, results, decisions, and residual risks.
7. Fail explicitly when tracking, required data, evaluation, gate, or evidence validation fails. No
   online or permissive success fallback is allowed.

The package boundaries are `domain`, `config`, `application`, `redaction`, `tracking`, `scorers`,
`evaluation`, `gate`, and `evidence`. The deterministic provider, lexical retrieval, and controls
remain cohesive inside `application` at this scale.

## Consequences

- SQLite satisfies the SQL-backend requirement without external infrastructure, but it is not a
  production scalability claim.
- Deterministic scorers provide reproducible technical signals but cannot replace expert assurance
  or prove broad safety, groundedness, or compliance.
- Separate variants improve comparison and trace clarity but require shared contracts to prevent
  accidental metric drift.
- Generated evidence must be reproducible and safe to share. Local databases and runtime outputs
  remain ignored; only the selected machine-validated sample under `evidence/sample/` is committed.

## Rejected alternatives

- **FileStore as the required backend:** MLflow evaluation datasets require SQL.
- **A hosted tracking service:** the mandatory path must not require SaaS, credentials, or external
  writes.
- **LLM-as-a-judge:** it would add provider cost, nondeterminism, and data-boundary requirements.
- **A second evaluation or GRC platform:** it would weaken the lab's focused evidence chain.
