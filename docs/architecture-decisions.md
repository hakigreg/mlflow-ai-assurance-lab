# Architecture decisions

This page is the short public index of the lab's implemented decisions. The detailed original
record is [ADR 0001](adr/0001-planned-assurance-architecture.md).

## Implemented decisions

| Decision | Rationale | Consequence |
|---|---|---|
| MLflow is the only assurance platform. | Keep tracing, evaluation, run/trace anchors, and evidence inspection in one reviewable system. | The lab does not compare evaluation or GRC products. |
| The required provider is deterministic local code. | The mandatory path must work without keys, SaaS, paid calls, or model downloads. | It tests assurance mechanics, not real-model quality or variability. |
| SQLite backs local MLflow tracking. | MLflow managed evaluation datasets require a SQL backend. | The setup is inspectable and portable but is not a production tracking architecture. |
| Baseline and governed variants share inputs but have distinct behavior and trace tags. | Missing controls must be visible as a comparison, not hidden by a single happy path. | The baseline is expected to fail; an unexpected baseline pass is an evaluation error. |
| Manual spans enforce a pre-persistence redaction boundary. | Raw output must remain scoreable while configured prohibited content must not reach traces or evidence. | The redactor covers configured patterns only and is not general privacy or secret detection. |
| Five deterministic code-based scorers feed a strict versioned gate. | Stable signals and explicit failure semantics are more reviewable than an online judge for this lab. | Lexical, ID, marker, and action matches do not establish semantic or factual correctness. |
| Every governed metric threshold is `1.0`. | Each of the eight synthetic cases is a release requirement, not a statistical sample. | One measured regression fails the gate; broader representativeness remains out of scope. |
| Evidence is generated, schema-validated, hash-linked, and source/input-bound. | A decision should be reproducible and challengeable from code and versioned inputs. | Local evidence is not signed, independently timestamped, append-only, or custody-controlled. |
| Standards mappings are educational crosswalks. | Public governance themes help explain the architecture without asserting an assessment. | No compliance, alignment, conformity, certification, or legal conclusion is permitted. |

## Rejected for the required path

- Hosted tracking or evaluation, because it would add credentials and an external dependency.
- LLM-as-a-judge, because it would add provider cost, nondeterminism, and data-boundary review.
- A second evaluation or GRC platform, because it would weaken the lab's focused evidence chain.
- Real or proprietary data, because all public fixtures and evidence must remain synthetic.

## Change rule

A change to behavior, data, thresholds, schemas, or control metadata requires corresponding tests,
documentation, traceability updates, regenerated sample evidence, and `make verify`. An optional
real-provider experiment may be added only outside the mandatory offline gate with explicit cost,
privacy, secret-handling, and reproducibility boundaries.
