# Interview notes

## Two-minute explanation

This lab demonstrates an end-to-end assurance pattern rather than another chatbot. A versioned
synthetic-policy assistant has an intentionally weak baseline and a governed variant. MLflow records
the traces and evaluation; deterministic scorers measure five narrow contracts; a versioned gate
requires every governed case to pass; generated evidence links risks, controls, code, tests,
run/trace anchors, decisions, and residual risk. The baseline must fail, so the comparison proves
that the controls make an observable difference within the fixture.

## What differentiates the work

- Governance requirements are executable: risks and controls connect to tests, metrics, gate
  semantics, evidence, and residual-risk statements.
- Failure paths are first-class: regressions, invalid metrics, stale policy bindings, tampered
  evidence, contradictory status, and configured persistence leakage fail explicitly.
- Claims are narrower than the implementation's marketing potential: scorer names state exactly
  what is measured, and standards mappings are non-compliance educational crosswalks.
- Evidence is generated and machine-validated rather than hand-authored as a success narrative.

## Design trade-offs

| Choice | Benefit | Cost or limit |
|---|---|---|
| Deterministic local provider | Reproducible, secret-free, no paid calls | Does not represent real LLM behavior |
| Lexical and ID-based scorers | Stable and inspectable | No semantic truth, entailment, or broad safety judgment |
| Strict `1.0` thresholds | Any fixture regression blocks the gate | Small dataset is not representative statistics |
| Manual MLflow tracing | Explicit spans and redaction boundary | More application code than automatic tracing |
| SQLite and local artifacts | Easy local/CI reproduction | Not scalable, shared, access-controlled, or immutable |
| Hash-linked evidence | Detects drift and tampering inside the pack | No signature, trusted timestamp, or chain of custody |

## Questions to invite

- Which risks should be material for the intended use case, and who owns acceptance?
- How would the dataset become representative and domain-owned?
- Which failures should block release versus require a documented exception?
- How would real-provider privacy, cost, nondeterminism, and prompt/data retention be governed?
- What evidence store, signing, access control, and retention model would an enterprise require?

## Honest limitations

The provider is deterministic code, not a trained model. The corpus and eight cases are synthetic.
The controls do not cover obfuscated, multilingual, multimodal, adaptive, authorization, tool-use,
or production ingestion threats. Configured redaction is not general PII or secret detection.
Citation IDs and lexical overlap do not establish factual correctness. The evidence pack is local
and unsigned. The gate is a technical regression decision aid, not legal review, certification,
enterprise release authorization, or production monitoring.

## Sensible extension path

For a real system, add accountable business and domain owners, representative data, human
adjudication, privacy/security review, provider and retention controls, broader adversarial tests,
monitoring, incident and exception workflows, and signed evidence storage. Keep those as new
versioned risks, controls, tests, and evidence rather than silently broadening this lab's claim.

Future separate portfolio labs may use `deepeval-governance-tests` for additional CI-oriented
evaluation and `verifywise-governance-lab` for inventory, governance workflows, and compliance
management. They are intentionally not dependencies of this MLflow-focused lab.
