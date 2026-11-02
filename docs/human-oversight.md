# Human oversight

## Review flow

1. Run the documented clean workflow and confirm `make verify` exits zero.
2. Review baseline and governed aggregate metrics, then every failed case.
3. Confirm trace variant tags, span sequence, source provenance, redaction, dataset/config digests,
   and manifest hashes.
4. Compare the observed decisions with the release policy: baseline `FAIL`, governed `PASS`.
5. Check the [`claim ledger`](claim-ledger.md) so public statements stay within their evidence and
   limitation boundaries.
6. Record unresolved limitations and residual risks before any portfolio release decision.

## Escalation and exceptions

The lab maintainer is the accountable review role. Escalate when a trace contains an unredacted
marker, a required metric or case is missing, evidence is stale or altered, governed fails, or
baseline unexpectedly passes. A release exception must be explicit, time-bounded, linked to risk
and evidence, and must not change a measured `FAIL` into `PASS`. This repository provides no
automated exception mechanism, and the local gate does not authorize an enterprise release.

## Stop/use criteria

Stop evaluation and do not distribute local artifacts when real sensitive data, a credential, or
an unredacted marker is found. Stop the release workflow when verification or the governed gate
fails. Do not use the system for real employment, legal, security, or policy decisions. Resume only
after correcting the cause, regenerating evidence, rerunning all checks, and reviewing residual
risk.
