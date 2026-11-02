# Risk assessment

This qualitative assessment covers the synthetic lab through P2-06. Likelihood and impact are
reasoned for the lab context; they are not enterprise ratings. Lifecycle stages describe where the
scenario is represented in this lab, not a complete enterprise lifecycle assessment.

| Risk | Scenario and rationale | Inherent L/I | Owner role | Controls | Residual risk and treatment | Lifecycle stage |
|---|---|---|---|---|---|---|
| RISK-TRACE-001 | Missing, stale, or altered evidence obscures how a decision was reached. Likelihood medium because generated artifacts drift; impact medium for portfolio credibility. | M/M | Lab maintainer | CTRL-TRACE-001, CTRL-EVID-001 | Low/medium after schema `2.0`, current-input/source digests, recomputation, hashes, and validation. The pack remains locally generated, unsigned, independently untimestamped, and subject to reviewer judgment when Git is `dirty`. | Evaluation, evidence generation, review |
| RISK-CITE-001 | An answer cites an absent or unretrieved source. Likelihood high in the uncontrolled baseline; impact medium because reviewers may trust unsupported provenance. | H/M | Lab maintainer | CTRL-CITE-001 | Low in the current fixture; citation-ID provenance does not establish source truth, entailment, or policy correctness, and the corpus is small. | Retrieval, output, evaluation |
| RISK-SCOPE-001 | The assistant answers outside the synthetic policy purpose. Likelihood medium and impact low/medium in the non-production lab. | M/L-M | Lab maintainer | CTRL-SCOPE-001, CTRL-REFUSE-001 | Low for configured terms; novel or paraphrased out-of-scope language may bypass the vocabulary heuristic. | Input, decision, output |
| RISK-LEAK-001 | Sensitive markers appear in output, traces, or evidence. Likelihood high in the intentional baseline case; impact high because persistence can amplify disclosure. | H/H | Lab maintainer | CTRL-REDACT-001, CTRL-REFUSE-001, CTRL-TRACE-001 | Medium: configured patterns are narrow and are not general PII, secret, access-control, or exfiltration detection. Real sensitive data remains prohibited. | Input, output, persistence, evidence |
| RISK-INJECT-001 | Direct or retrieved instructions alter intended behavior. Likelihood medium; impact medium in this no-tools lab. | M/M | Lab maintainer | CTRL-INJECT-001, CTRL-REFUSE-001 | Medium: exact pattern matching does not cover obfuscation, multilingual, multimodal, adaptive, ingestion, or poisoning attacks. | Input, retrieval, decision |
| RISK-GROUND-001 | The system answers without enough policy support or appears grounded when it is not. Likelihood high in the baseline; impact medium. | H/M | Lab maintainer | CTRL-SUPPORT-001, CTRL-CITE-001, CTRL-REFUSE-001, CTRL-GROUND-001 | Medium: lexical-response and citation-ID matching are not semantic grounding, factual correctness, misinformation assessment, or representative real-model evaluation. | Retrieval, output, evaluation |
| RISK-RELEASE-001 | A regression is accepted because thresholds, results, or failure semantics are wrong. Likelihood medium; impact high for assurance claims. | M/H | Lab maintainer | CTRL-GATE-001, CTRL-EVID-001 | Low/medium after strict thresholds, fail-closed validation, negative tests, and measured control derivation. The narrow dataset and lack of independent review prevent enterprise release reliance. | Evaluation, gate, release review |

Each risk ID is registered in `config/control-catalog-v1.json`. The generated
[`control-matrix.md`](control-matrix.md) links controls back to these risks, code/configuration,
tests, MLflow run/trace or case anchors, evidence, decisions, and residual risk. Repository
validation rejects missing, unknown, or orphaned references in either direction.
