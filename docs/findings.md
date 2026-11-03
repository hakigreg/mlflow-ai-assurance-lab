# Final portfolio and release-review findings

This document separates observed results, known gaps, and recommendations. The detailed claim and
evidence boundaries are in the [`claim ledger`](claim-ledger.md); the overall interpretation is in
the [`bounded assurance statement`](assurance-statement.md).

## Review conclusion

The local portfolio package is coherent and reproducible for its bounded claim. The quickstart,
baseline/governed demo, MLflow evaluation, fail-closed gate, negative paths, trace redaction checks,
and generated/committed evidence validation were observed during the Phase 3 review. No critical
implementation defect or false successful fallback was found.

The review corrected five material presentation/readiness gaps: the README still described Phase 2
instead of leading with portfolio value; the initial setup network boundary and `uv`-on-`PATH`
prerequisite were not explicit; the Phase 3 demo, interview, architecture summary, and release
checklist were absent; unverified hosted labels were assigned by issue forms; and hosted controls
were not clearly separated from local verification. Blank issues are now disabled so public reports
use the sanitized quality/governance forms; private security reporting remains a publication
blocker.

Read-only GitHub inspection later confirmed that the current commit is synchronized and its hosted
CI passed. The owner designated `contacto@vektoria.io` as the private security contact. Dependabot
alerts and security updates remain deferred, and repository rules plus optional GitHub Private
Vulnerability Reporting can be configured after the repository becomes public. No hosted setting
was changed during the review.

## Observed technical results

The committed sample evaluated eight versioned synthetic cases per variant through MLflow 3.17.2.
Baseline scored `0.25` citation-source match, `0.875` scope-action match, `0.875` configured
synthetic-marker absence, `0.375` expected-action match, and `0.25` lexical-response match, resulting
in `FAIL`. Governed scored `1.0` on all five required metrics and produced `PASS` at the unchanged
versioned thresholds.

The schema `2.0` evidence pack validates current input and application-source digests, complete
case/trace coverage, recorded and recomputed decisions, measured control status, prohibited-content
absence at the configured persistence boundary, material digest, and generated artifact hashes.
Negative tests reject controlled regression, missing or invalid metrics, stale policy/input binding,
tampered or contradictory evidence, unsafe configured content, and unknown schemas.

| Risk | Lifecycle stage | Implemented control | Produced evidence | Observed gap | Enterprise fit assessment |
|---|---|---|---|---|---|
| RISK-TRACE-001 | Evaluation, evidence generation, review | CTRL-TRACE-001, CTRL-EVID-001 | MLflow case/trace anchors; schema-bound [`manifest.json`](../evidence/sample/manifest.json); generated [`control matrix`](control-matrix.md) | Local evidence is not signed, independently timestamped, append-only, or custody-controlled. A `dirty` Git marker requires review. | Useful as an inspectable provenance pattern; insufficient as an enterprise evidence store or audit record. |
| RISK-CITE-001 | Retrieval, output, evaluation | CTRL-CITE-001 | `CASE-CIT-001`, citation metric, run/trace anchor, and control status in [`control-status.json`](../evidence/sample/control-status.json) | Citation IDs show expected/retrieved provenance only; they do not establish truth or entailment. | Useful as a deterministic regression check; insufficient for domain or factual validation. |
| RISK-SCOPE-001 | Input, decision, output | CTRL-SCOPE-001, CTRL-REFUSE-001 | `CASE-SCOPE-001`, named-case and aggregate action scores | Coverage is vocabulary-based and may miss paraphrases, new domains, or context-dependent scope. | Useful as a policy-rule fixture; insufficient for real traffic or evolving business scope. |
| RISK-LEAK-001 | Input, output, persistence, evidence | CTRL-REDACT-001, CTRL-REFUSE-001, CTRL-TRACE-001 | `CASE-SENS-001`, raw-output score, `persistence_safe=true`, and stored-trace/runtime inspection tests | Configured patterns are not general PII, secret, authorization, or exfiltration detection. | Useful to demonstrate a pre-persistence boundary; unsuitable for real sensitive data without broader controls. |
| RISK-INJECT-001 | Input, retrieval, decision | CTRL-INJECT-001, CTRL-REFUSE-001 | Direct and indirect cases, expected-action scores, and trace anchors | No obfuscation, multilingual, multimodal, adaptive, ingestion, or poisoning attack lifecycle is exercised. | Useful as a minimal defensive test pattern; not an enterprise prompt-injection assessment or red team. |
| RISK-GROUND-001 | Retrieval, output, evaluation | CTRL-SUPPORT-001, CTRL-CITE-001, CTRL-REFUSE-001, CTRL-GROUND-001 | Support case, citation-source match, expected-action match, and lexical-response match | Lexical overlap and citation IDs do not establish semantic support, factual accuracy, or misinformation absence. | Useful for stable offline regression; insufficient for a real model, representative corpus, or high-impact use. |
| RISK-RELEASE-001 | Evaluation, gate, release review | CTRL-GATE-001, CTRL-EVID-001 | Expected `baseline=FAIL`/`governed=PASS`, strict exit semantics, material digest, and negative-path tests | The gate covers only the versioned dataset and metrics; no independent review, exception workflow, or production monitoring exists. | Useful as a fail-closed technical quality gate; not an enterprise release authorization. |

## Known gaps and bounded interpretation

The observed result does not demonstrate production safety, real-model behavior, semantic
groundedness, general sensitive-data detection, broad prompt-injection resistance, policy
correctness, legal compliance or applicability, NIST alignment, ISO conformity or certification,
or complete audit readiness. The deterministic provider and lexical retriever are test instruments.

Threat mappings are similarly bounded. OWASP `LLM09:2026` is not applicable to the implemented
lexical retriever; the committed untrusted bulletin is not an executed RAG-poisoning lifecycle;
MITRE ATLAS prompt-injection and leakage references describe fixture intent, not demonstrated
effectiveness against an LLM. Details are in the [`threat model`](threat-model.md).

## Recommendations for enterprise extension

These are recommendations, not implemented controls or observed results.

| Related risk | Recommendation | Why it remains future work |
|---|---|---|
| RISK-TRACE-001, RISK-RELEASE-001 | Add signed, independently timestamped, access-controlled, append-only evidence storage; generate from a clean reviewed commit; add independent enterprise release review and a governed exception process. | The current pack is local and hash-linked only; Phase 3 reviewed portfolio readiness, not enterprise release authorization. |
| RISK-CITE-001, RISK-GROUND-001 | Perform domain-owner source validation and representative semantic/factual evaluation with uncertainty and human adjudication. | Current scorers intentionally measure only IDs, actions, configured markers, and lexical terms. |
| RISK-SCOPE-001 | Build a versioned, domain-owned scope taxonomy and test paraphrases, ambiguity, multilingual inputs, and production-like traffic. | The current vocabulary and eight cases are deliberately small. |
| RISK-LEAK-001 | Complete privacy/security review; add data classification, authorization, general secret/PII controls, retention, access logging, and incident response before handling real data. | Real sensitive data and production identity/access architecture are out of scope. |
| RISK-INJECT-001 | Run independent red-team and human testing across obfuscated, multilingual, multimodal, adaptive, ingestion, and poisoning paths for the actual provider and retrieval architecture. | The required path has no real model, vector store, dynamic ingestion, tools, or autonomous actions. |
| All risks | Add real-provider/data-boundary review, representative evaluation, production monitoring, change management, incident management, and accountable business ownership before any enterprise use. | Those capabilities would materially expand the lab and require new evidence, risks, controls, and release criteria. |
