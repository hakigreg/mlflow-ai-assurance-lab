# Phase 1 assurance evidence report

This report is generated from deterministic synthetic cases. It demonstrates a bounded
technical comparison; it does not prove production safety, legal compliance, ISO
conformity, certification, or complete audit readiness.

- Dataset digest: `52e8233512ee90631a64b1728a591a1cd6962f270ea76cb4e47e736bf5ce4069`
- Release policy: `release-policy-v1`
- Generated at (volatile): `2026-10-30T13:42:09.659254+00:00`

## Observed decisions

| Variant | Decision | MLflow run (volatile) | Failed metrics |
|---|---|---|---|
| baseline | FAIL | `bfc89f2e3b25491ca126a89c0c07e22a` | citation_source_match, scope_action_match, synthetic_marker_absence, expected_action_match, lexical_response_match |
| governed | PASS | `fa151ff889314e4793495a74852a4d7f` | None |

## Aggregate metrics

| Scorer | Baseline | Governed |
|---|---:|---:|
| citation_source_match | 0.250 | 1.000 |
| expected_action_match | 0.375 | 1.000 |
| lexical_response_match | 0.250 | 1.000 |
| scope_action_match | 0.875 | 1.000 |
| synthetic_marker_absence | 0.875 | 1.000 |

## Interpretation limits

`lexical_response_match` checks the expected action, lexical terms, and citation IDs
only. It is not a semantic or factual correctness judgment. All scorers use a small
synthetic dataset, and `synthetic_marker_absence` recognizes only configured marker
patterns. The observed PASS applies only to these versioned cases and thresholds.
