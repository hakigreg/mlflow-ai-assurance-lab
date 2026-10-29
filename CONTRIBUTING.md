# Contributing

## Project state

The repository is in **Foundation — implementation not started**. Phase 0 accepts repository-engineering and documentation work only. Application behavior and generated assurance evidence begin in Phase 1.

The repository currently uses a single-maintainer pull request workflow. Opening a pull request does not imply a response time or acceptance.

## Setup

Requirements:

- Git
- `make`
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

The project pins Python 3.12.16 in `.python-version`; uv can provision it when needed. Install exactly from the committed lockfile:

```bash
uv sync --locked --dev
```

No API keys, SaaS accounts, paid calls, or model downloads are required for the current checks.

## Available checks

Run focused checks during development:

```bash
make lint
make format-check
make types
make test
make foundation
```

Before requesting review, run the complete implemented check set:

```bash
make verify
git diff --check
```

Phase 1 is planned to add the deterministic offline gate and evidence validation. Do not report those planned checks as available until their commands and negative-path tests exist.

## Pull request workflow

1. Keep the change within the current phase recorded in `PLANS.md`.
2. Update behavior, tests, documentation, and architecture decisions together when applicable.
3. Identify affected risk and control IDs. If the control matrix does not yet exist, state `Not yet assigned` rather than inventing traceability.
4. Update risk/control documentation when behavior or risk treatment changes.
5. Record commands actually run and their observed results in the pull request template.
6. Regenerate and validate evidence after behavior, dataset, threshold, configuration, or schema changes once evidence generation exists.
7. Document limitations and a reversible rollback path.

Use only synthetic, publishable content. Do not commit secrets, personal data, client data, proprietary policies, or unsanitized traces and logs. Public quality and governance gaps can use the issue forms. Potential vulnerabilities, secret exposure, unsafe trace persistence, or sensitive leakage must follow `SECURITY.md` and must not be disclosed in a public issue.
