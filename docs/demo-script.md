# Portfolio demo script (5–7 minutes)

Use only synthetic data and the generated repository evidence. Do not present the governed `PASS`
as a production, compliance, or semantic-quality conclusion.

## 0:00–0:45 — State the value and boundary

Open `README.md` and say:

> This lab turns AI risk into controls, automated MLflow evaluation, a fail-closed decision, and
> hash-validated evidence. It compares an intentionally weak baseline with a governed variant on
> eight synthetic cases. The result demonstrates the assurance workflow, not production safety or
> compliance.

Point to the architecture diagram and the bounded assurance statement.

## 0:45–2:15 — Show the behavioral difference

Run:

```bash
make demo
```

Highlight the same supported policy question in both variants. Then show the out-of-scope weather
question: baseline answers it; governed returns `refuse_scope`. Mention that trace tags distinguish
the variants and configured prohibited content is redacted before persistence.

## 2:15–3:30 — Execute evaluation and decision

Run:

```bash
make evaluate
make gate
```

Expected output is `baseline=FAIL governed=PASS`, followed by a governed `PASS`. Explain that the
five scorers check citation IDs, scope action, configured marker absence, expected action, and
lexical response—not semantic truth.

Show the failure path without treating it as an error in the demo:

```bash
MLFLOW_DISABLE_AGENT_HINT=1 UV_CACHE_DIR=.uv-cache uv run --locked --no-sync \
  python -m mlflow_ai_assurance_lab gate --variant baseline
```

It must exit `1`. Invalid evidence or gate inputs exit `2` rather than falling back to success.

## 3:30–5:00 — Follow the evidence chain

Open `docs/control-matrix.md` at `CTRL-CITE-001` and follow:

`risk -> control -> scorer/config -> test -> case/run/trace -> evidence -> decision -> residual risk`

Then open `evidence/sample/report.md` and `evidence/sample/manifest.json`. Explain that the pack is
generated from results and validated for schemas, hashes, complete case coverage, current input and
source digests, recomputed decisions, control relations, and configured prohibited content.

## 5:00–6:00 — Demonstrate reproducibility

Run or show the final lines from:

```bash
make verify
```

This covers the lockfile, lint, formatting, types, tests and negative paths, repository consistency,
offline evaluation, governed gate, generated evidence, and committed sample evidence.

## 6:00–7:00 — Close with honest limitations

Open `RELEASE_READINESS.md`. State that local review passes but publication remains blocked on
owner-controlled hosted settings and a private vulnerability-reporting path. Close with the main
technical limits: synthetic cases, lexical checks, configured-pattern redaction, a deterministic
non-LLM provider, and local unsigned evidence.

## Optional trace inspection

If time permits, start the loopback-only UI after a demo or evaluation:

```bash
MLFLOW_DISABLE_AGENT_HINT=1 UV_CACHE_DIR=.uv-cache uv run --locked --no-sync mlflow ui \
  --backend-store-uri sqlite:///artifacts/mlflow/mlflow.db \
  --host 127.0.0.1 \
  --port 5000
```

Open `http://127.0.0.1:5000`, select `mlflow-ai-assurance-lab-offline`, and inspect one baseline and
one governed trace. A screenshot is not required because the committed Markdown and JSON evidence
is reproducible and more reviewable.
