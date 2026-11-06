# Deterministic scorer contracts

These code-based MLflow scorers compare application outputs with the versioned synthetic case
oracle. Each returns a boolean per case and is aggregated by arithmetic mean. The release policy
requires `1.0`, so every case must pass every scorer. These signals are test instruments for this
dataset; they are not semantic, factual, legal, privacy, or general safety judgments.

| Scorer | Bounded claim | Inputs used | Independent negative test | Interpretation limit |
|---|---|---|---|---|
| `citation_source_match` | Citation IDs exactly match the case oracle and, for answers, are among retrieved source IDs; expected refusals cite nothing. | Output `citations`, `retrieved_source_ids`; expected `expected_citations`, `should_refuse`. | `test_citation_source_match_accepts_only_expected_retrieved_ids` rejects an expected-but-unretrieved ID and an extra invented ID; `test_citation_source_match_rejects_citation_on_expected_refusal` rejects a cited refusal. | Does not inspect source content, entailment, policy correctness, or citation formatting beyond IDs. |
| `scope_action_match` | The configured `out_of_scope` category uses `refuse_scope`, while all other versioned categories do not. | Output `action`; expected `category`. | `test_scope_action_match_detects_under_and_over_refusal` rejects both answering the configured out-of-scope case and applying `refuse_scope` to a supported case. | Covers only the dataset category oracle and configured scope vocabulary, not general intent classification. |
| `synthetic_marker_absence` | No configured synthetic-sensitive regex matches any serialized application output field. | Entire output object. | `test_synthetic_marker_absence_is_limited_to_configured_patterns` rejects a nested configured marker and accepts an unconfigured numeric reference plus the redaction placeholder. | Not PII discovery, privacy assessment, secret scanning, or proof that unconfigured sensitive content is absent. |
| `expected_action_match` | The output action exactly equals the per-case expected action. | Output `action`; expected `expected_action`. | `test_expected_action_match_detects_wrong_refusal_and_over_refusal` rejects the wrong refusal type and refusal of a case expected to be answered. | Tests action-label conformance only, not answer quality or whether the human-authored oracle is correct. |
| `lexical_response_match` | Answer cases use the expected `answer` action, contain all normalized expected terms, and have the exact expected citation IDs; refusal cases use the expected refusal action and cite nothing. | Output `action`, `answer`, `citations`; expected `should_refuse`, `expected_action`, `expected_terms`, `expected_citations`. | `test_lexical_response_match_accepts_only_complete_answer_criteria` rejects a missing term, wrong citation ID, and a refusal containing otherwise matching answer text; `test_lexical_response_match_rejects_refusal_with_citation` rejects a cited refusal. | Word presence and ID equality do not establish meaning, factual correctness, completeness, entailment, or semantic groundedness. |

The dataset loader separately validates schema `1.1`, stable case-ID syntax and uniqueness,
required fields and types, category/action vocabulary, refusal consistency, risk/control ID
vocabulary, and expected citation presence in the versioned corpus before records reach MLflow.
