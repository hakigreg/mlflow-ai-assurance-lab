# Source register

Consulted initially on 2026-10-29 and updated on 2026-11-02. This register uses official primary
sources to support repository decisions. A reference is not a claim that the lab implements a
standard, satisfies a regulation, or verifies an MLflow capability end to end.

| ID | Official source | Organization | Version or date | Decision supported |
|---|---|---|---|---|
| SRC-001 | [Python support lifecycle](https://devguide.python.org/versions/) | Python Software Foundation | Accessed 2026-10-29 | Python 3.12 remains supported through October 2028. Pin 3.12.16 for the foundation rather than adopting a prerelease branch. |
| SRC-002 | [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) | Astral | Accessed 2026-10-29 | Use `uv.lock`, `uv sync --locked`, and `uv lock --check` for reproducible dependency installation. |
| SRC-003 | [MLflow 3.17.2 release](https://pypi.org/project/mlflow/3.17.2/) | MLflow maintainers / PyPI | 3.17.2, 2026-10-21 | Pin the stable patch release used by the deterministic offline path. Later upgrades require re-running compatibility and evidence checks. |
| SRC-004 | [MLflow tracing](https://mlflow.org/docs/latest/genai/tracing/) | MLflow | Accessed 2026-10-29; package 3.17.2 | Use manual root/child spans for input handling, retrieval, generation, control decisions, and output validation; tag traces by variant. Manual persistence boundaries allow pre-persistence redaction. |
| SRC-005 | [MLflow evaluation datasets SDK](https://mlflow.org/docs/latest/genai/datasets/sdk-guide/) | MLflow | Accessed 2026-10-29; package 3.17.2 | Evaluation datasets require SQL. Use a managed, version-tagged dataset with SQLite and merge versioned dictionary records using the documented `inputs`/`expectations` schema. |
| SRC-006 | [MLflow custom code-based scorers](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/custom/) | MLflow | Accessed 2026-10-29; package 3.17.2 | Implement deterministic field-based scorers with `@scorer`, `Feedback`, and mean aggregation. Keep LLM judges out of the mandatory path. |
| SRC-007 | [MLflow tracking server](https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/) | MLflow | Accessed 2026-10-29; package 3.17.2 | Use local SQLite metadata and filesystem artifacts. The optional UI binds loopback; remote exposure and production deployment are out of scope. |
| SRC-008 | [AI Risk Management Framework 1.0](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10) | NIST | NIST AI 100-1, 2023-01-26; rechecked 2026-11-02 | Use the public GOVERN, MAP, MEASURE, and MANAGE functions and named categories as educational crosswalk themes. NIST states that AI RMF 1.0 is being revised, so the mapping stays pinned to 1.0 and does not claim alignment. |
| SRC-009 | [Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) | NIST | NIST AI 600-1, 2024-07-26; page updated 2026-04-08; rechecked 2026-11-02 | Use the public governance, content-provenance, pre-deployment-testing, and incident-disclosure considerations as bounded comparison themes. The deterministic lab does not implement the profile or represent a foundation model. |
| SRC-010 | [ISO/IEC 42001 public overview](https://www.iso.org/standard/42001?browse=ics) | ISO/IEC | ISO/IEC 42001:2023, Edition 1; rechecked 2026-11-02 | Reference only the public overview themes: establishing, implementing, maintaining, and continually improving an AIMS; risk/opportunity management; responsible use; traceability; transparency; and continual learning. Do not reproduce protected clauses or claim a complete management system, conformity, or certification. |
| SRC-011 | [OWASP GenAI LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) | OWASP GenAI Security Project | 2026 edition, 2026-08-03; rechecked 2026-11-02 | Use the current edition as threat vocabulary for selected defensive fixtures. Exact identifiers are cross-checked against SRC-017 and SRC-024; a vocabulary mapping is not evidence of complete threat coverage. |
| SRC-012 | [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng) | European Union | Official Journal, 2024-07-12; rechecked 2026-11-02 | Treat documentation, logging/traceability, transparency, human oversight, and robustness as relevant themes only. The lab makes no legal classification, role/territory analysis, applicability conclusion, or compliance determination. |
| SRC-013 | [European Commission AI Act overview](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) | European Commission | Rechecked 2026-11-02 | Record the current risk-based framing and public descriptions of documentation, logging, oversight, robustness, and transparency as changeable context; do not infer that high-risk or other obligations apply to this lab. |
| SRC-014 | [Dependabot options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference) | GitHub | Accessed 2026-10-29 | Configure supported `uv` and `github-actions` ecosystems with weekly grouped updates and small PR limits. |
| SRC-015 | [GitHub Actions workflow permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions) | GitHub | Accessed 2026-10-29 | Limit the CI token to `contents: read`; no write permission or secret is required. |
| SRC-016 | [MLflow evaluation quickstart](https://mlflow.org/docs/latest/genai/eval-monitor/quickstart/) | MLflow | Accessed 2026-10-29; package 3.17.2 | Use the stable `mlflow.genai.evaluate(data, predict_fn, scorers)` path and consume its run ID, aggregate metrics, per-case results, and traces. Local behavioral checks confirmed the pinned signature. |
| SRC-017 | [OWASP Top 10 for LLM Applications 2026 PDF](https://genai.owasp.org/download/56857/) | OWASP GenAI Security Project | Version 2026; landing page dated 2026-08-03; accessed 2026-10-29 | Use selected current identifiers in the educational crosswalk: LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM07 Misinformation, and LLM09 Vector and Embedding Weaknesses. |
| SRC-018 | [MLflow trace masking](https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/masking/) | MLflow | Accessed 2026-10-29; package 3.17.2 | Treat trace masking as a client-side responsibility. The lab applies its own narrow, versioned synthetic-marker redaction before calling span input/output persistence APIs and tests the stored trace. |
| SRC-019 | [MLflow v3.17.2 tracing API source](https://github.com/mlflow/mlflow/blob/v3.17.2/mlflow/tracing/fluent.py) | MLflow | Tag `v3.17.2`; verified 2026-10-30 | Pin the implemented `start_span`, `update_current_trace`, and `search_traces` signatures to the exact release source rather than relying only on mutable `latest` documentation. |
| SRC-020 | [MLflow v3.17.2 GenAI evaluation API source](https://github.com/mlflow/mlflow/blob/v3.17.2/mlflow/genai/evaluation/base.py) | MLflow | Tag `v3.17.2`; verified 2026-10-30 | Confirm the implemented `evaluate(data, scorers, predict_fn, model_id)` call shape and `EvaluationResult` return contract for the pinned release. |
| SRC-021 | [MLflow v3.17.2 evaluation dataset API source](https://github.com/mlflow/mlflow/blob/v3.17.2/mlflow/genai/datasets/__init__.py) | MLflow | Tag `v3.17.2`; verified 2026-10-30 | Confirm the implemented `create_dataset` and filtered `search_datasets` call shapes. `EvaluationDataset.merge_records` was also checked in the same tagged source tree. |
| SRC-022 | [MLflow v3.17.2 scorer API source](https://github.com/mlflow/mlflow/blob/v3.17.2/mlflow/genai/scorers/base.py) | MLflow | Tag `v3.17.2`; verified 2026-10-30 | Confirm the implemented `@scorer` arguments, supported `mean` aggregation, `Scorer` return type, and custom `Feedback` use for deterministic local scorers. |
| SRC-023 | [MITRE ATLAS technique catalog](https://atlas.mitre.org/) | MITRE | Live catalog; accessed 2026-11-02 | Use only named, pertinent techniques as threat vocabulary: `AML.T0051` for the prompt-injection fixture and `AML.T0057` as a qualified synthetic leakage analogue. Record `AML.T0070`, `AML.T0071`, `AML.T0068`, and `AML.T0129` as out of scope where their attack lifecycle is not exercised. ATLAS mapping is not a control-effectiveness claim. |
| SRC-024 | [OWASP GenAI LLM Top 10 2026 source files](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final) | OWASP GenAI Security Project | 2026 final files; accessed 2026-11-02 | Confirm `LLM01` Prompt Injection, `LLM02` Sensitive Information Disclosure, `LLM07` Misinformation, and `LLM09` Vector and Embedding Weaknesses. Because the lab uses lexical retrieval, `LLM09` is explicitly not applicable to the implemented retriever. |

## MLflow 3.17.2 API verification record

On 2026-10-30, local signature inspection observed installed MLflow `3.17.2` and matched the
repository calls to official tag `v3.17.2` sources:

| Implemented surface | Repository use | Verification decision |
|---|---|---|
| Tracking and manual tracing | Local SQLite tracking; experiment selection; nested `start_span`; trace tags/metadata; filtered trace search returning trace objects. | The installed signatures used by `tracking.py`, `application.py`, and `evaluation.py` match the pinned release. Keep the manual pre-persistence redaction boundary. |
| Managed evaluation datasets | Create or find one named dataset in the current experiment and merge versioned `inputs`/`expectations` records. | The installed `create_dataset`, filtered `search_datasets`, and `EvaluationDataset.merge_records` signatures match the pinned release. Keep SQLite because the managed dataset path requires a database-backed tracking store. |
| GenAI evaluation | Pass the managed dataset, `PolicyAssistant.ask`, and deterministic scorers to `mlflow.genai.evaluate`. | The installed signature and official tagged source match the implemented call. The executable checks verify this path behaviorally; the claim does not extend to later versions or hosted deployments. |
| Code-based scorers | Define custom scorers with `@scorer(name=..., aggregations=["mean"])` and return `Feedback`. | The installed signature and official tagged source support the implemented form. This verification establishes API compatibility only; scorer validity remains assigned to P2-02. |

## Register limits

- `latest` MLflow guides can change after consultation. Exact implemented API decisions are now
  cross-checked against official tag `v3.17.2` sources in SRC-019 through SRC-022; conceptual
  guidance links remain date-stamped and must be rechecked before any dependency upgrade.
- ISO/IEC 42001 content beyond the public ISO overview was not used. No clause-level mapping is
  authorized by this source register.
- NIST, OWASP, MITRE ATLAS, and EU materials evolve. Mappings use the recorded version/date and
  distinguish technical evidence from governance, security-framework, or legal conclusions. A
  current catalog identifier does not demonstrate that the lab exercised the full threat lifecycle.
- The executable checks verify the pinned MLflow tracing, managed dataset, evaluation, scorer,
  gate, and evidence path locally. This does not validate later MLflow releases or production
  deployment architecture.
