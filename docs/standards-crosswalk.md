# Educational standards and regulatory crosswalk

This crosswalk is an architecture aid, not a normative assessment. It does not establish legal
applicability or compliance, NIST alignment, ISO/IEC 42001 conformity or certification, or complete
coverage. Source versions, consultation dates, and decisions are recorded in the
[`source register`](source-register.md). Only the public ISO overview is used; no protected clauses
are reproduced.

## Risk-management and regulatory themes

| Public source and version | Public function, category, or theme | Lab artifact used as an analogy | What is not established |
|---|---|---|---|
| NIST AI RMF 1.0, NIST AI 100-1 (SRC-008) | `GOVERN 1` risk-management policies/processes and `GOVERN 4` documentation of risks and impacts | Versioned release policy and control catalog; [`risk assessment`](risk-assessment.md); generated [`control matrix`](control-matrix.md); accountable decision owner | The lab is not an organizational governance program, has no multidisciplinary governance body, and has not been assessed for NIST alignment. |
| NIST AI RMF 1.0, NIST AI 100-1 (SRC-008) | `MAP 1` context and intended purpose | [`AI system card`](ai-system-card.md), prohibited uses, assumptions, trust boundaries, and lifecycle-specific risks | The small synthetic context does not map affected communities, deployment impacts, benefits, or legal requirements. |
| NIST AI RMF 1.0, NIST AI 100-1 (SRC-008) | `MEASURE 1` selected methods/metrics and documented unmeasured risks | Five bounded deterministic scorers, eight cases, negative paths, residual risks, and versioned thresholds | The metrics do not measure societal impact, fairness, semantic truth, real-model performance, uncertainty, or production behavior. |
| NIST AI RMF 1.0, NIST AI 100-1 (SRC-008) | `MANAGE 1` risk-informed decision on whether intended objectives are met and work should proceed | Strict baseline/governed expected decisions, governed gate, stop criteria, and human oversight procedure | A local gate is a decision aid, not organizational risk acceptance, deployment authorization, monitoring, or incident management. |
| NIST AI 600-1, July 2024 (SRC-009) | Public cross-sector profile themes including governance, content provenance, pre-deployment testing, and incident disclosure | Control ownership, citation/source anchors, deterministic evaluation, evidence provenance, and escalation criteria | The deterministic provider is not a generative foundation model. The lab does not implement the profile, representative GAI testing, or an incident-disclosure program. |
| ISO/IEC 42001:2023, Edition 1 public overview (SRC-010) | Establishing, implementing, maintaining, and continually improving an AI management system; public themes of risk/opportunity management, responsible use, traceability, transparency, and continual learning | Versioned policy, risk/control/evidence links, human oversight, source register, and regeneration/validation workflow | No clause-level mapping, complete management system, internal audit, management evaluation, conformity assessment, or certification evidence exists. |
| Regulation (EU) 2024/1689 and current Commission overview (SRC-012, SRC-013) | Documentation and logging/traceability themes | System card, MLflow traces, schema-bound evidence, and source/input provenance | No legal classification, territorial or role analysis, technical-documentation sufficiency assessment, or applicability conclusion. |
| Regulation (EU) 2024/1689 and current Commission overview (SRC-012, SRC-013) | Human oversight theme | Accountable decision owner, escalation, stop/use, and exception criteria in [`human oversight`](human-oversight.md) | The lab does not establish that any statutory human-oversight obligation applies or is satisfied. |
| Regulation (EU) 2024/1689 and current Commission overview (SRC-012, SRC-013) | Robustness and transparency themes | Negative tests, bounded system/metric limitations, documented machine-interaction context, and strict failure semantics | Eight synthetic cases and local controls are not evidence of statutory robustness, accuracy, cybersecurity, user-information, or transparency compliance. |

The EU entries deliberately use themes only. Requirements described for high-risk or other
regulated systems are not attributed to this lab, and the crosswalk makes no legal classification.

## Security taxonomy mapping

| Public source and version | Lab evidence | Limit |
|---|---|---|
| OWASP `LLM01:2026` Prompt Injection (SRC-011, SRC-017, SRC-024) | Direct and retrieved instruction fixtures; CTRL-INJECT-001 and CTRL-REFUSE-001 | Pattern fixtures against deterministic code are not comprehensive prompt-injection testing or evidence about an LLM. |
| OWASP `LLM02:2026` Sensitive Information Disclosure (SRC-011, SRC-017, SRC-024) | Configured synthetic-marker case, refusal, redaction boundary, and persisted-trace inspection | Synthetic configured patterns are not general privacy, secret, access-control, or exfiltration coverage. |
| OWASP `LLM07:2026` Misinformation (SRC-011, SRC-017, SRC-024) | Citation-source ID and lexical-response matching | Matching cannot establish semantic truth, factual correctness, source entailment, or misinformation absence. |
| OWASP `LLM09:2026` Vector and Embedding Weaknesses (SRC-011, SRC-017, SRC-024) | No implemented evidence; recorded as not applicable to the lexical retriever | A RAG label does not create vector/embedding coverage. Any vector implementation would require new controls and evaluation. |
| MITRE ATLAS `AML.T0051` LLM Prompt Injection (SRC-023) | Threat-inspired direct and indirect fixtures | The mapping describes fixture intent only; no real LLM attack or general technique mitigation is demonstrated. |
| Other MITRE ATLAS techniques | No mapping asserted unless the exact lifecycle and adversary behavior are exercised | RAG poisoning, prompt obfuscation, multimodal triggers, agents, tools, training attacks, and model compromise are absent or out of scope; see [`threat-model.md`](threat-model.md). |

A qualified legal, standards, security, privacy, and domain assessment would be required before using
these themes for an enterprise system. Recommendations are recorded in
[`findings.md`](findings.md), not represented as implemented controls.
