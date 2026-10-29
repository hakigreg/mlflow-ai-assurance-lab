# Control matrix

The matrix provides Phase 1 bidirectional traceability. Evidence anchors name fields or case IDs
inside generated files. `PASS` describes the current governed sample only; baseline gaps are
intentional and visible in the same evidence.

| Control | Risks | Control intent | Implementation/config | Verification | MLflow/evidence | Decision and residual risk |
|---|---|---|---|---|---|---|
| CTRL-TRACE-001 | RISK-TRACE-001, RISK-LEAK-001 | Trace input, retrieval, generation, decisions, and validation with safe metadata. | `application.PolicyAssistant.ask`; `trace-redaction-v1` | `tests/test_tracing.py::test_sensitive_marker_is_not_persisted_in_trace` | MLflow trace IDs in `summary.json`; `control-status.json` | Governed PASS; local backend and trace metadata are not production observability. |
| CTRL-CITE-001 | RISK-CITE-001, RISK-GROUND-001 | Accept only expected citations retrieved from the versioned corpus. | `scorers.citation_validity`; `config/release-policy-v1.json` | `tests/test_scorers.py::test_citation_validity_rejects_unknown_source` | `summary.json#variants.*.metrics.citation_validity`; CASE-CIT-001 | Governed PASS, baseline FAIL; corpus and retrieval remain small. |
| CTRL-SCOPE-001 | RISK-SCOPE-001 | Refuse configured out-of-scope requests. | `application.PolicyAssistant._governed_decision` | `tests/test_application.py::test_governed_actions_match_dataset` | CASE-SCOPE-001 | Governed PASS, baseline gap; heuristic vocabulary is incomplete. |
| CTRL-REDACT-001 | RISK-LEAK-001 | Redact configured markers before persistence. | `redaction.redact`; `trace-redaction-v1` | `tests/test_tracing.py::test_sensitive_marker_is_not_persisted_in_trace` | CASE-SENS-001 and its redacted trace | Governed trace PASS; pattern coverage is not general PII detection. |
| CTRL-INJECT-001 | RISK-INJECT-001 | Detect selected direct and indirect instruction patterns and untrusted retrieval. | `application.PolicyAssistant._has_injection` | `tests/test_application.py::test_governed_actions_match_dataset` | CASE-PI-DIRECT-001, CASE-PI-INDIRECT-001 | Governed PASS; obfuscation and multimodal attacks are out of scope. |
| CTRL-SUPPORT-001 | RISK-GROUND-001 | Refuse when lexical retrieval support is below the configured rule. | `application.PolicyAssistant._governed_decision` | `tests/test_application.py::test_governed_actions_match_dataset` | CASE-SUPPORT-001 | Governed PASS; lexical support is not semantic evidence. |
| CTRL-REFUSE-001 | RISK-SCOPE-001, RISK-LEAK-001, RISK-INJECT-001, RISK-GROUND-001 | Require the expected controlled refusal and avoid refusing supported cases. | `scorers.refusal_behavior` | `tests/test_scorers.py::test_refusal_behavior_requires_expected_action` | `summary.json#variants.*.metrics.refusal_behavior` | Governed PASS, baseline FAIL; only versioned categories are tested. |
| CTRL-GROUND-001 | RISK-GROUND-001 | Measure expected term and citation presence as a named proxy. | `scorers.groundedness_proxy` | `tests/test_scorers.py::test_groundedness_proxy_is_limited_and_deterministic` | `summary.json#variants.*.metrics.groundedness_proxy` | Governed PASS, baseline FAIL; no semantic or factual proof. |
| CTRL-GATE-001 | RISK-RELEASE-001 | Apply versioned 1.0 thresholds and fail non-zero on a regression. | `gate.decide`; `config/release-policy-v1.json` | `tests/test_gate.py::test_regression_makes_gate_fail` | `summary.json#variants.*.decision` | Governed PASS and baseline FAIL expected; thresholds cover only eight cases. |
| CTRL-EVID-001 | RISK-TRACE-001, RISK-RELEASE-001 | Bind source digests, file hashes, case coverage, controls, and decisions. | `evidence.generate_evidence`, `evidence.validate_evidence` | `tests/test_evidence.py::test_tampered_evidence_is_rejected` | `manifest.json`, `control-status.json` | Sample PASS; volatile MLflow IDs and timestamps are documented. |

Machine-readable counterparts are generated in
[`../evidence/sample/control-status.json`](../evidence/sample/control-status.json) and
[`../evidence/sample/manifest.json`](../evidence/sample/manifest.json).
