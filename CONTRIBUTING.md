# Contributing

## Project state

Phase 1 provides a functional offline assurance MVP. Phase 2 hardening is in progress through
human-gated increments; Phase 3 independent release review has not started. Keep changes within
the current increment and record observed status in `PLANS.md`.

## Setup and checks

Requirements are Git, `make`, and
[uv](https://docs.astral.sh/uv/getting-started/installation/). The repository pins Python 3.12.16
and installs exactly from `uv.lock`:

```bash
make setup
```

Focused checks are `make lint`, `make format-check`, `make types`, `make test`,
`make repository`, `make evaluate`, `make gate`, and `make evidence-validate`. Before review, run:

```bash
make verify
git diff --check
```

`make verify` runs linting, formatting, types, tests (including negative paths), repository
validation, the offline baseline/governed comparison, the governed gate, regenerated evidence
validation, and committed sample evidence validation. No API key, SaaS account, paid call, or model
download is required.

## Change workflow

1. Update behavior, tests, documentation, traceability, and evidence together.
2. Identify affected risk and control IDs from `docs/control-matrix.md`.
   Change static control metadata only in `config/control-catalog-v1.json`; the human matrix and
   machine-readable control status are generated from that catalog and measured results.
3. Regenerate sample evidence explicitly with
   `uv run python -m mlflow_ai_assurance_lab evidence --output-dir evidence/sample` when behavior,
   data, configuration, schemas, or thresholds change.
4. Record only commands actually run and results actually observed.
5. Document limitations, residual-risk impact, and a reversible rollback path.

Use only synthetic, publishable content. Do not commit secrets, personal data, client data,
proprietary policies, local MLflow databases, or unsanitized traces. Public quality and governance
gaps may use issue forms; security-sensitive reports must follow `SECURITY.md`.
