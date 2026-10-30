# Phase 1 findings

## Observed results

The generated sample evaluated eight versioned synthetic cases through MLflow 3.17.2. Baseline
failed the release policy with citation-source match `0.25`, scope-action match `0.875`, configured
synthetic-marker absence `0.875`, expected-action match `0.375`, and lexical-response match `0.25`.
Governed scored `1.0` on every required metric and passed the unchanged versioned thresholds. The
sample evidence manifest and machine-readable control links validated successfully.

MLflow demonstrates distinguishable baseline/governed traces, span-level input handling,
retrieval, generation, control decisions, output validation, managed-dataset lineage, scorer
assessments, evaluation run IDs, and trace IDs. A controlled metric regression returns a non-zero
gate exit. Trace tests observe that the raw synthetic-sensitive baseline output is scoreable but
the configured marker is absent from the persisted trace.

## What this does not demonstrate

The result does not demonstrate production safety, real-model behavior, semantic groundedness,
general PII detection, broad prompt-injection resistance, legal compliance, ISO conformity or
certification, or complete audit readiness. The deterministic provider and lexical retriever are
test instruments. `lexical_response_match` proves only action, expected-term, and citation-ID
matching under these fixtures; `synthetic_marker_absence` covers only configured patterns.

## Residual risks

Novel scope language, obfuscated or multimodal injection, unconfigured sensitive formats, corpus
poisoning, incorrect policy content, real provider variability, operational access control, and
cryptographic evidence provenance remain uncovered or only partially covered. Timestamps, run IDs,
and trace IDs are intentionally volatile evidence fields.

## Enterprise recommendation

Before enterprise use, perform domain validation; privacy, security, and legal review; broader and
representative evaluation; independent red-team and human testing; provider/data-boundary review;
identity and access controls; signed evidence provenance; production monitoring; incident and
change management; and an accountable exception process. These are recommendations, not completed
Phase 1 controls. Phase 2 should harden evidence integrity and negative paths without changing the
bounded claim.
