# Bounded assurance statement

## Claim

For the versioned local configuration and eight synthetic cases recorded in the committed sample,
the governed variant provides stronger, inspectable control coverage than the deliberately limited
baseline. The measured baseline decision is `FAIL`; the measured governed decision is `PASS` at
the five versioned `1.0` thresholds. The evidence pack binds those results to cases, controls,
MLflow run/trace anchors, input and source digests, schemas, and generated-file hashes.

This is a bounded comparative technical claim. It does not establish production safety, real-model
behavior, policy correctness, legal compliance or applicability, NIST alignment, ISO/IEC 42001
conformity or certification, general security effectiveness, or complete audit readiness.

## Evidence

- [`summary.json`](../evidence/sample/summary.json) records the aggregate metrics, decisions,
  failed metrics, persistence assertion, and MLflow identifiers for both variants.
- [`case-results.json`](../evidence/sample/case-results.json) records all eight case outcomes and
  trace anchors per variant.
- [`control-status.json`](../evidence/sample/control-status.json) and the generated
  [`control matrix`](control-matrix.md) connect measured observations to risks, controls, tests,
  evidence, the release decision, and residual risk.
- [`manifest.json`](../evidence/sample/manifest.json) records schema versions, current-input and
  application-source digests, tool versions, artifact hashes, and the material comparison digest.
- [`Makefile`](../Makefile) and [`tests/`](../tests/) define the executable verification path.

## Assumptions

- The committed sample is interpreted only with its recorded dataset, corpus, release policy,
  control catalog, application-source digest, and tool versions.
- The deterministic provider and lexical retriever are test instruments, not substitutes for a
  trained model, production retrieval system, or representative deployment data.
- Local MLflow identifiers are evidence anchors; the source and input digests provide the portable
  binding. A `dirty` Git marker requires separate source inspection.
- All inputs are synthetic and publishable. Real sensitive data is prohibited.

## Limitations and permitted use

The fixtures cover configured citation IDs, scope terms, prompt patterns, synthetic markers,
expected actions, and lexical response terms. They do not cover novel or obfuscated attacks,
semantic truth, factual accuracy, general sensitive-data discovery, vector retrieval, model or
data poisoning, access control, real-provider variability, or production operations. The evidence
is local and hash-linked but is not signed, independently timestamped, or append-only.

The statement may be used to explain this lab project's evidence chain. It must not be used as
an enterprise release authorization or as a normative, legal, certification, or audit conclusion.
Material claims and their individual evidence boundaries are listed in the
[`claim ledger`](claim-ledger.md).
