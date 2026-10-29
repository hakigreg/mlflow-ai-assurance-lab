# Source register

Consulted on 2026-10-29. This register uses official primary sources to support repository decisions. A reference is not a claim that the planned lab implements a standard, satisfies a regulation, or verifies an MLflow capability end to end.

| ID | Official source | Organization | Version or date | Decision supported |
|---|---|---|---|---|
| SRC-001 | [Python version status](https://devguide.python.org/versions/) | Python Software Foundation | Accessed 2026-10-29 | Python 3.12 remains supported through October 2028. Pin 3.12.16 for the foundation rather than adopting a prerelease branch. |
| SRC-002 | [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) | Astral | Accessed 2026-10-29 | Use `uv.lock`, `uv sync --locked`, and `uv lock --check` for reproducible dependency installation. |
| SRC-003 | [MLflow 3.17.2 release](https://pypi.org/project/mlflow/3.17.2/) | MLflow maintainers / PyPI | 3.17.2, 2026-10-21 | Pin the current stable patch release for Phase 0 compatibility work. Actual lab API behavior remains unimplemented and must be tested in Phase 1. |
| SRC-004 | [MLflow tracing](https://mlflow.org/docs/latest/genai/tracing/) | MLflow | Accessed 2026-10-29 | Plan MLflow-native traces for distinguishable baseline and governed execution. No trace implementation exists in Phase 0. |
| SRC-005 | [MLflow evaluation datasets](https://mlflow.org/docs/latest/genai/datasets/) | MLflow | Accessed 2026-10-29 | Evaluation datasets require a SQL backend; plan SQLite locally rather than FileStore. Dataset creation is deferred to Phase 1. |
| SRC-006 | [MLflow custom code-based scorers](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/custom/) | MLflow | Accessed 2026-10-29 | Plan deterministic code-based scorers with `mlflow.genai.evaluate()` for offline evaluation. Do not use default LLM judges in the mandatory path. |
| SRC-007 | [MLflow tracking server](https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/) | MLflow | Accessed 2026-10-29 | Plan a local tracking server on loopback with SQLite metadata. Remote exposure and production deployment are out of scope. |
| SRC-008 | [AI Risk Management Framework 1.0](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10) | NIST | NIST AI 100-1, 2023-01-26 | Use GOVERN, MAP, MEASURE, and MANAGE as educational crosswalk themes. NIST states that AI RMF 1.0 is being revised, so mappings must remain versioned and bounded. |
| SRC-009 | [Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) | NIST | NIST AI 600-1, 2024-07-26; page updated 2026-04-08 | Use selected GenAI risk-management themes to inform later risks and controls without claiming conformity. |
| SRC-010 | [ISO/IEC 42001 public overview](https://www.iso.org/standard/42001) | ISO/IEC | ISO/IEC 42001:2023, Edition 1 | Reference only public themes such as risk management, traceability, transparency, and continual improvement. Do not reproduce protected clauses or claim conformity or certification. |
| SRC-011 | [OWASP GenAI LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) | OWASP GenAI Security Project | 2026 edition, 2026-08-03 | Select later application-security risks from the current LLM list, especially those relevant to prompt injection, sensitive information disclosure, vector/embedding weaknesses, and system prompt leakage. Exact risk IDs require Phase 2 crosswalk review. |
| SRC-012 | [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng) | European Union | Official Journal, 2024-07-12 | Treat risk management, logging/traceability, documentation, transparency, human oversight, robustness, cybersecurity, and accuracy as relevant regulatory themes only; this lab does not make a legal classification or compliance determination. |
| SRC-013 | [European Commission AI Act overview](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) | European Commission | Accessed 2026-10-29 | Record the current risk-based framing and implementation timeline as changeable context; defer any legal applicability analysis. |
| SRC-014 | [Dependabot options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference) | GitHub | Accessed 2026-10-29 | Configure supported `uv` and `github-actions` ecosystems with weekly grouped updates and small PR limits. |
| SRC-015 | [GitHub Actions workflow permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions) | GitHub | Accessed 2026-10-29 | Limit the CI token to `contents: read`; no write permission or secret is required. |

## Register limits

- `latest` MLflow documentation can change after consultation; the implementation must re-check documentation against the pinned package and record any mismatch.
- ISO/IEC 42001 content beyond the public ISO overview was not used. No clause-level mapping is authorized by this source register.
- NIST, OWASP, and EU materials evolve. Later mappings must include the recorded version/date and distinguish technical evidence from governance or legal conclusions.
- The Phase 0 checks validate repository structure and configuration only. They do not verify the planned MLflow tracing, dataset, evaluation, scorer, gate, or evidence APIs.
