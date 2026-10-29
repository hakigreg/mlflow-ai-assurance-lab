# ADR 0001: Local assurance architecture

- **Status:** Accepted and implemented in Phase 1
- **Date:** 2026-10-29
- **Scope:** Phase 0 decision, implemented and behaviorally verified in Phase 1

## Context

The future lab needs one mandatory path that is deterministic, inspectable, secret-free, and runnable locally and in CI. It must compare an intentionally limited baseline with a governed variant while preserving traceability through MLflow. Phase 0 must not implement or simulate that behavior.

MLflow evaluation datasets require a SQL backend. Built-in LLM judges may make provider calls, so they are unsuitable for the mandatory offline path. The public repository must also keep synthetic inputs, policy logic, thresholds, and generated evidence reviewable.

## Decision

The following architecture is implemented for Phase 1:

1. Use Python 3.12, uv, and the committed lockfile for the required runtime.
2. Use one deterministic offline provider implemented as explicit local code with no model download or network fallback. An optional real provider may be added later but must remain disabled by default and outside required verification.
3. Keep shared synthetic corpus and typed contracts separate from baseline and governed orchestration. Baseline and governed variants must have distinct entry points and trace attributes so their evidence cannot be confused.
4. Use MLflow 3.17.2 as the sole evaluation and assurance platform. Capture planned traces and evaluation results in a local MLflow tracking server backed by SQLite, with local artifacts in ignored generated directories.
5. Use versioned synthetic evaluation cases and deterministic code-based MLflow scorers. Any groundedness heuristic must be labeled as a proxy, not a semantic correctness proof.
6. Apply a versioned release policy after evaluation and emit a machine-validated evidence pack that links risks, controls, tests, run/trace identifiers, results, decisions, and residual risks.
7. Fail explicitly when the tracking backend, required data, evaluation, gate, or evidence validation fails. No online or permissive success fallback is allowed.

The implemented package boundaries are `domain`, `config`, `application`, `redaction`, `tracking`,
`scorers`, `evaluation`, `gate`, and `evidence`. The deterministic provider, lexical retrieval, and
controls remain cohesive inside `application` at this scale.

## Consequences

- SQLite satisfies the SQL-backend requirement for local evaluation datasets without external infrastructure, but it is not a production scalability claim.
- Deterministic scorers provide reproducible technical signals but cannot replace expert review or prove broad safety, groundedness, or compliance.
- Separate variants improve comparison and trace clarity but require shared contracts to prevent accidental metric drift.
- Generated evidence must be reproducible and safe to publish; local databases, artifacts, and evidence outputs remain ignored until explicit validated examples are selected.

## Rejected alternatives

- **FileStore as the required backend:** rejected because MLflow evaluation datasets require SQL.
- **A hosted tracking service:** rejected because the mandatory path must not require SaaS, credentials, or external writes.
- **LLM-as-a-judge for the required gate:** rejected because it would make the mandatory path non-deterministic or provider-dependent.
- **Another evaluation or GRC platform:** rejected because MLflow is the repository's primary assurance tool and cross-platform comparison is out of scope.

## Verification status

Official documentation and the pinned package were reviewed. Phase 1 executed the managed dataset,
manual tracing, `mlflow.genai.evaluate()`, five code-based scorers, release gate, and evidence
validation against local SQLite. The observed sample produces the intentionally expected baseline
`FAIL` and governed `PASS`. The implementation uses manual spans so raw scorer-visible output can
be redacted before trace persistence. Local run/trace identifiers and timestamps remain volatile.
