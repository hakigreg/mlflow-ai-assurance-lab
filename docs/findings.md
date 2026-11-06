# Technical findings and limitations

This document separates measured results, known gaps, and recommendations. The detailed claim and
evidence boundaries are in the [`claim ledger`](claim-ledger.md); the overall interpretation is in
the [`bounded assurance statement`](assurance-statement.md).

## Observed technical results

The committed sample evaluates eight versioned synthetic cases per variant through MLflow 3.17.2.
Baseline scores `0.25` citation-source match, `0.875` scope-action match, `0.875` configured
synthetic-marker absence, `0.375` expected-action match, and `0.25` lexical-response match,
resulting in `FAIL`. Governed scores `1.0` on all five required metrics and produces `PASS` at the
versioned thresholds.

The schema `2.0` evidence pack validates current input and application-source digests, complete
case/trace coverage, recorded and recomputed decisions, measured control observations,
configured-content absence at the persistence boundary, material digest, and generated artifact
hashes. Negative tests reject controlled regression, missing or invalid metrics, stale policy/input
binding, tampered or contradictory evidence, unsafe configured content, and unknown schemas.

| Risk | Lifecycle stage | Implemented control | Produced evidence | Observed gap | Enterprise fit |
|---|---|---|---|---|---|
| RISK-TRACE-001 | Evaluation and evidence generation | CTRL-TRACE-001, CTRL-EVID-001 | MLflow case/trace anchors; schema-bound [`manifest.json`](../evidence/sample/manifest.json); generated [`control matrix`](control-matrix.md) | Local evidence is not signed, independently timestamped, append-only, or custody-controlled. A `dirty` Git marker requires separate source inspection. | Inspectable provenance pattern; insufficient as an enterprise evidence store or audit record. |
| RISK-CITE-001 | Retrieval, output, evaluation | CTRL-CITE-001 | `CASE-CIT-001`, citation metric, run/trace anchor, and observation in [`control-status.json`](../evidence/sample/control-status.json) | Citation IDs show expected/retrieved provenance only; they do not establish truth or entailment. | Deterministic regression check; insufficient for domain or factual validation. |
| RISK-SCOPE-001 | Input and control decision | CTRL-SCOPE-001, CTRL-REFUSE-001 | `CASE-SCOPE-001`, scope and action metrics, trace action | The vocabulary is narrow and English-only. | Useful contract example; insufficient for production intent classification. |
| RISK-LEAK-001 | Input, output, persistence | CTRL-REDACT-001, CTRL-REFUSE-001, CTRL-TRACE-001 | Synthetic leakage case, pre-persistence redaction test, persisted-trace inspection | Configured regex coverage is not general PII, secret, authorization, or exfiltration detection. | Demonstrates a persistence boundary, not a complete data-protection program. |
| RISK-INJECT-001 | Input, retrieval, inference | CTRL-INJECT-001, CTRL-REFUSE-001 | Direct and retrieved instruction cases with expected refusal actions | Exact patterns do not cover obfuscation, multilingual or multimodal attacks, adaptive attackers, tools, or agents. | Threat-inspired fixture, not broad prompt-injection assurance. |
| RISK-GROUND-001 | Retrieval, output, evaluation | CTRL-SUPPORT-001, CTRL-GROUND-001, CTRL-CITE-001, CTRL-REFUSE-001 | Unsupported-query refusal, lexical-response and citation-ID metrics | Lexical overlap and IDs are not semantic support, source entailment, truth, or misinformation detection. | Deterministic proxy only. |
| RISK-RELEASE-001 | Evaluation and gate | CTRL-GATE-001, CTRL-EVID-001 | Expected `baseline=FAIL`/`governed=PASS`, strict exit semantics, material digest, and negative-path tests | The gate covers only the versioned dataset and metrics; no production monitoring or governed exception mechanism exists. | Fail-closed technical quality gate; not enterprise release authorization. |

## Known gaps and bounded interpretation

The deterministic provider and lexical retriever are test instruments. The results do not establish
real-model behavior, semantic or factual correctness, general privacy/security effectiveness,
legal compliance, NIST alignment, ISO/IEC 42001 conformity or certification, production safety, or
complete audit readiness.

The local evidence pack detects drift and inconsistency relative to trusted versioned inputs. It
does not establish author identity, chain of custody, independent time, immutability, access
control, retention enforcement, or organizational risk acceptance.

## Recommendations for enterprise extension

| Scope | Recommendation | Reason |
|---|---|---|
| RISK-TRACE-001, RISK-RELEASE-001 | Add signed, independently timestamped, access-controlled, append-only evidence storage and a governed exception process. | The current pack is local and hash-linked only. |
| RISK-CITE-001, RISK-GROUND-001 | Add domain-owned representative data, semantic/factual evaluation, source-quality criteria, uncertainty handling, and expert adjudication. | Current metrics intentionally measure lexical and ID contracts only. |
| RISK-LEAK-001 | Add data classification, authorization, general secret/PII controls, retention, access logging, and incident response before handling real data. | Real sensitive data and production identity/access architecture are out of scope. |
| RISK-INJECT-001, RISK-SCOPE-001 | Add obfuscated, multilingual, multimodal, adaptive, tool-use, authorization, and ingestion attack cases tied to the intended architecture. | Current fixtures exercise exact deterministic patterns only. |
| All risks | Add representative evaluation, production monitoring, change management, incident management, and accountable business ownership before enterprise use. | Those capabilities would require new evidence, risks, controls, and release criteria. |
