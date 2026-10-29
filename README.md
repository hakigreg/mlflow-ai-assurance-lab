# MLflow AI Assurance Lab

> **Status: Foundation — implementation not started**

This repository is the foundation for a small, reproducible portfolio lab that will explore how MLflow can support a technical AI assurance chain:

`AI risk -> control -> automated evaluation -> decision gate -> auditable evidence`

The planned lab will compare synthetic-policy RAG baseline and governed variants under a deterministic offline evaluation path. Its bounded claim is comparative: within documented assumptions and synthetic data, the governed variant should provide stronger, verifiable control coverage than the baseline. It will not establish production safety, legal compliance, certification, ISO conformity, or complete audit readiness.

## Current contents

Phase 0 provides only repository contracts, dependency and Python decisions, collaboration controls, primary-source references, an initial architecture decision, and structural checks. Retrieval, generation, policy controls, MLflow traces, evaluation datasets, scorers, release gates, providers, and evidence generation are all **Planned** for later phases and are not implemented or simulated here.

Read these files before contributing:

- [`GOALS.md`](GOALS.md) — stable scope and success conditions.
- [`PLANS.md`](PLANS.md) — phase status and observed evidence.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — setup and checks.
- [`SECURITY.md`](SECURITY.md) — pre-release reporting limitations.
- [`docs/source-register.md`](docs/source-register.md) — official sources and supported decisions.
- [`docs/adr/0001-planned-assurance-architecture.md`](docs/adr/0001-planned-assurance-architecture.md) — planned local architecture.

## Foundation setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```bash
uv sync --locked --dev
make verify
```

`make verify` currently validates only the Phase 0 foundation: the lockfile, formatting, lint, types, structural tests, the planned MLflow API import surface, YAML parsing, local Markdown links, repository contracts, and the absence of Phase 1 modules. It does not run an assurance gate or validate an evidence pack because neither exists yet.

## License

Licensed under the MIT License. See [`LICENSE`](LICENSE).
