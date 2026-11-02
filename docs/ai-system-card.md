# AI system card

## System and purpose

`mlflow-ai-assurance-lab` is a portfolio-scale synthetic-policy question-answering system used to
demonstrate a bounded assurance chain. It compares a deliberately limited baseline with a governed
variant. Intended users are engineers, assurance reviewers, and governance architects examining
the controls, traces, evaluation results, and evidence—not end users seeking real policy advice.
The governing interpretation is the [`bounded assurance statement`](assurance-statement.md), with
individual evidence boundaries in the [`claim ledger`](claim-ledger.md).

## Boundaries and data

- Inputs, policies, identities, expectations, and adversarial cases are synthetic and publishable.
- The system answers only from the versioned corpus in `data/policies/policies-v1.json`.
- The required provider is deterministic local code. It is not a trained language model and makes
  no network call or model download.
- SQLite stores local MLflow runs, traces, and the managed evaluation dataset under `artifacts/`.
- The generated evidence schemas are version `2.0`; the manifest binds application/source and input
  digests, tool versions, MLflow anchors, artifact hashes, and a material comparison digest.
- Known sensitive test markers are scored in raw application output but configured synthetic
  markers, credential shapes, and prohibited prompt phrases are redacted before trace or evidence
  persistence under `persistence-redaction-v2`. This is not general PII or secret detection.

## Variants and dependencies

Both variants share retrieval and generation contracts. `baseline` intentionally lacks explicit
scope, sensitive-data, prompt-injection, support, and citation controls. `governed` applies these
controls before generation and validates output. MLflow 3.17.2 is the sole assurance platform;
Python 3.12.16 and the committed `uv.lock` define the runtime.

## Limitations

The corpus and eight-case dataset are small. Retrieval uses lexical overlap. The deterministic
provider cannot represent the variability or emergent behavior of a real model. The
`lexical_response_match` checks action labels, lexical terms, and citation IDs only. The application
has no vector store, external provider, tools, autonomous actions, dynamic ingestion, or production
identity/access boundary. Passing the gate is evidence for this versioned lab configuration, not
production safety, policy correctness, legal applicability or compliance, NIST alignment, ISO/IEC
42001 conformity or certification, general security effectiveness, or complete audit readiness.

## Human oversight

The gate is a decision aid. A lab reviewer owns release decisions, exceptions, stop/use decisions,
and review of failed cases and residual risks. See [`human-oversight.md`](human-oversight.md).
