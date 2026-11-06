# Contributing

## Setup and checks

Requirements are Git, `make`, and
[uv](https://docs.astral.sh/uv/getting-started/installation/). The repository pins Python 3.12.16
and installs exactly from `uv.lock`:

```bash
make setup
```

Focused checks are `make lint`, `make format-check`, `make types`, `make test`,
`make repository`, `make evaluate`, `make gate`, and `make evidence-validate`. Before submitting a
change, run:

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
   machine-readable control observations are generated from that catalog and measured results.
3. Regenerate sample evidence explicitly with
   `uv run python -m mlflow_ai_assurance_lab evidence --output-dir evidence/sample` when behavior,
   data, configuration, schemas, or thresholds change.
   Compare two validated packs with
   `uv run python -m mlflow_ai_assurance_lab compare-evidence LEFT_DIR RIGHT_DIR`; material drift
   exits `1`, while documented timestamp and MLflow-ID volatility is normalized.
4. Record only commands actually run and results actually observed.
5. Document limitations, residual-risk impact, and a reversible rollback path.

Use only synthetic, publishable content. Do not commit secrets, personal data, client data,
proprietary policies, local MLflow databases, or unsanitized traces. Public quality and governance
gaps may use issue forms; security-sensitive reports must follow `SECURITY.md`.
