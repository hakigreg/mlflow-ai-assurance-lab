# Phase 1 assurance evidence report

This report is generated from deterministic synthetic cases. It demonstrates a bounded
technical comparison; it does not prove production safety, legal compliance, ISO
conformity, certification, or complete audit readiness.

- Dataset digest: `8bfa021682b0a5fa01aeaa0797dccd528f7248ff49e0baff7eb9e6fbcd43d364`
- Release policy: `release-policy-v1`
- Generated at (volatile): `2026-10-29T21:07:02.265224+00:00`

## Observed decisions

| Variant | Decision | MLflow run (volatile) | Failed metrics |
|---|---|---|---|
| baseline | FAIL | `ce8f1878982047bf8f4ea898d242ed92` | citation_validity, scope_adherence, sensitive_data_leakage, refusal_behavior, groundedness_proxy |
| governed | PASS | `4752cfac64374f96955b84d83f444c9c` | None |

## Aggregate metrics

| Scorer | Baseline | Governed |
|---|---:|---:|
| citation_validity | 0.250 | 1.000 |
| groundedness_proxy | 0.250 | 1.000 |
| refusal_behavior | 0.375 | 1.000 |
| scope_adherence | 0.875 | 1.000 |
| sensitive_data_leakage | 0.875 | 1.000 |

## Interpretation limits

`groundedness_proxy` checks expected lexical terms and citation IDs only. It is not
a semantic correctness judgment. All scorers use a small synthetic dataset, so the
observed PASS applies only to these versioned cases and thresholds.
