# Educational standards and regulatory crosswalk

This architecture crosswalk is educational and deliberately bounded. It does not establish legal
applicability or compliance, ISO/IEC 42001 conformity or certification, NIST alignment, or complete
coverage. Only public sources and themes in [`source-register.md`](source-register.md) are used; no
protected ISO clauses are reproduced.

| Public theme | Lab evidence | Limits |
|---|---|---|
| NIST AI RMF 1.0 GOVERN/MAP | System card, risk owners, scope, risk assessment, control matrix | A small lab is not an organizational risk-management program. |
| NIST AI RMF 1.0 MEASURE/MANAGE and NIST AI 600-1 GenAI profile | Versioned cases, deterministic scorers, thresholds, gate, residual risks, human escalation | Scorers cover selected technical behaviors only and do not measure societal or deployment impacts. |
| ISO/IEC 42001:2023 public themes: risk management, transparency, traceability, and continual improvement | Risk/control links, MLflow traces, evidence manifest, versioned plan | No clause-level mapping, management-system assessment, conformity, or certification claim. |
| OWASP LLM01:2026 Prompt Injection | Direct/indirect cases and CTRL-INJECT-001 | Defensive pattern tests are not comprehensive penetration testing. |
| OWASP LLM02:2026 Sensitive Information Disclosure | Leakage scorer, refusal, trace redaction | Only synthetic configured markers are covered. |
| OWASP LLM07:2026 Misinformation | Citation validity and limited groundedness proxy | The proxy cannot establish semantic truth. |
| OWASP LLM09:2026 Vector and Embedding Weaknesses | Retrieval provenance and support threshold | The lab uses lexical retrieval, not production embeddings or a vector database. |
| EU AI Act public themes: documentation, logging/traceability, transparency, human oversight, robustness, cybersecurity, and accuracy | System card, MLflow traces, evidence, oversight flow, adversarial cases, gate | No legal classification or applicability analysis; technical artifacts alone cannot demonstrate compliance. |

Mappings are architecture aids. A qualified legal, standards, security, and domain review would be
required before using them for an enterprise system.
