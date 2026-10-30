# Risk assessment

This qualitative assessment covers the Phase 1 synthetic lab. Likelihood and impact are reasoned
for the lab context; they are not enterprise ratings.

| Risk | Scenario and rationale | Inherent L/I | Owner role | Controls | Residual risk and treatment |
|---|---|---|---|---|---|
| RISK-TRACE-001 | Missing, stale, or altered evidence obscures how a decision was reached. Likelihood medium because generated artifacts drift; impact medium for portfolio credibility. | M/M | Lab maintainer | CTRL-TRACE-001, CTRL-EVID-001 | Low/medium after hashes and validation; Phase 2 should add stronger provenance and clean-checkout review. |
| RISK-CITE-001 | An answer cites an absent or unretrieved source. Likelihood high in the uncontrolled baseline; impact medium because reviewers may trust unsupported provenance. | H/M | Lab maintainer | CTRL-CITE-001 | Low in current cases; lexical retrieval and small corpus remain limiting. |
| RISK-SCOPE-001 | The assistant answers outside the synthetic policy purpose. Likelihood medium and impact low/medium in the non-production lab. | M/L-M | Lab maintainer | CTRL-SCOPE-001, CTRL-REFUSE-001 | Low for configured terms; novel out-of-scope language may bypass the heuristic. |
| RISK-LEAK-001 | Sensitive markers appear in output, traces, or evidence. Likelihood high in the intentional baseline case; impact high because persistence can amplify disclosure. | H/H | Lab maintainer | CTRL-REDACT-001, CTRL-REFUSE-001, CTRL-TRACE-001 | Medium: configured patterns are narrow and are not a general PII detector. Do not use real sensitive data. |
| RISK-INJECT-001 | Direct or retrieved instructions alter intended behavior. Likelihood medium; impact medium in this no-tools lab. | M/M | Lab maintainer | CTRL-INJECT-001, CTRL-REFUSE-001 | Medium: pattern matching does not cover obfuscation, multilingual, or multimodal injection. |
| RISK-GROUND-001 | The system answers without enough policy support or appears grounded when it is not. Likelihood high in the baseline; impact medium. | H/M | Lab maintainer | CTRL-SUPPORT-001, CTRL-CITE-001, CTRL-GROUND-001 | Medium: lexical-response and citation-ID matching are not semantic or factual proof. |
| RISK-RELEASE-001 | A regression is accepted because thresholds, results, or failure semantics are wrong. Likelihood medium; impact high for assurance claims. | M/H | Lab maintainer | CTRL-GATE-001, CTRL-EVID-001 | Low/medium after strict thresholds and negative tests; independent review remains Phase 3 work. |

Each risk links forward through [`control-matrix.md`](control-matrix.md); that matrix links controls
back to these risks, code, tests, evidence, decisions, and residual risk.
