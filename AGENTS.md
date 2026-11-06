# Repository instructions

## Purpose and invariants

This repository is a small, inspectable AI assurance lab project. Its intended evidence chain is:

`AI risk -> control -> automated evaluation -> decision gate -> auditable evidence`

MLflow is the primary assurance tool. Do not add another evaluation or GRC platform. The required path must run locally and in CI without API keys, SaaS, paid calls, or model downloads. Use only publishable synthetic identities, policies, prompts, and data. Redact secrets and sensitive markers before persisting traces, logs, fixtures, or evidence.

Maintain bidirectional traceability across risk, control, implementation, test, MLflow run or trace, evidence, decision, and residual risk. Version thresholds, release policy, datasets, and schemas. Never fabricate results or turn failures into successful fallbacks. Treat standards mappings as educational architecture crosswalks, document their limits, and make no claims of compliance, certification, legal assessment, production safety, or complete audit readiness.

## Engineering expectations

- Prefer cohesive, typed Python modules, explicit errors, minimal dependencies, and a deterministic offline path.
- Keep dependencies reproducible through the committed lockfile.
- Generate evidence with code; do not hand-author measured results.
- Update behavior, tests, documentation, traceability, and evidence together.
- Keep GitHub templates and CI aligned with checks that actually exist.
- Verify APIs and standards against official primary sources and record versions and decisions in `docs/source-register.md`.
- Separate observed results from recommendations and report only commands actually run and outcomes actually observed.

## Context routing

- Read `GOALS.md` for scope, constraints, and success conditions.
- Read `CONTRIBUTING.md` for the available setup, checks, and contribution workflow.
- Read `SECURITY.md` before handling a security report or potentially sensitive evidence.
- Read `docs/source-register.md` before relying on an external API, standard, or regulatory mapping.
- Read `docs/control-matrix.md` when it exists for risk, control, test, evidence, decision, and residual-risk links.

## Verification

Run focused checks while changing a component, then run `make verify`. The current required workflow covers linting, formatting, types, tests, repository validation, the deterministic offline evaluation and gate, generated evidence validation, and sample evidence validation, including the implemented negative-path tests. Do not claim a check passed unless it was executed and observed.

## External boundaries

Reversible local development is allowed. Pushes, deployment, cloud resources, paid calls, external writes, and changes to hosted repository settings require explicit authorization. Never commit secrets or real sensitive data.
