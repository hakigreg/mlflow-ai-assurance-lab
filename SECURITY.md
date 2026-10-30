# Security policy

## Pre-release status

This repository is not yet published or released. No private reporting channel exists yet. **Publication is blocked until the maintainer configures a real private contact or enables GitHub Private Vulnerability Reporting and replaces this placeholder.** Do not put vulnerability details, secrets, personal data, exploitable payloads, or unsanitized evidence in a public issue.

There is no response-time or remediation SLA. Reports will be handled on a best-effort basis after a private channel exists.

## Security scope

Security reports include, but are not limited to:

- committed or exposed credentials and secret-like values;
- sensitive information leakage through outputs, logs, fixtures, traces, runs, or evidence;
- unsafe persistence or insufficient redaction of trace content;
- vulnerable dependencies or build and CI supply-chain weaknesses;
- control bypasses that create a concrete confidentiality, integrity, or availability risk.

Public quality or governance issues include incorrect documentation, missing traceability, weak but non-exploitable evaluation coverage, and proposed control improvements that reveal no sensitive details. Use the public issue forms only for those sanitized cases.

## Safe evidence handling

Security evidence must be minimal, synthetic or sanitized, and shared only through the future private channel. Do not publish real credentials, personal or client data, proprietary prompts or policies, weaponized payloads, complete exploit instructions, raw sensitive traces, local environment dumps, or internal infrastructure details.

The persistence boundary applies `persistence-redaction-v2` before MLflow trace persistence. It
redacts the configured synthetic markers, selected credential/API-key shapes, and configured
instruction-override phrases from span inputs, outputs, attributes, tags, and metadata. Known
synthetic sensitive markers are still presented to the application and deterministic leakage
scorer, but only redacted values may enter traces, generated evidence, or logs. This narrow policy
is not general PII, secret, or prompt-injection detection. Treat a failed redaction assertion as a
security defect; do not bypass it or publish the affected local database.

## Maintainer actions required before publication

- Configure and document a real private security contact or enable GitHub Private Vulnerability Reporting.
- Enable Dependabot alerts and Dependabot security updates in hosted repository settings.
- Confirm that the final public reporting path is reachable and remove this placeholder language.

Local files do not enable hosted security settings.
