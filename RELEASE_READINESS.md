# Release readiness

**Local review decision:** PASS  
**Public publication decision:** BLOCKED pending owner-controlled hosted settings

This record separates checks observed locally on 2026-11-02 from GitHub settings that were not
verified or changed. `PASS` applies only to the bounded synthetic lab and is not enterprise release
authorization.

## Locally verified

| Check | Result | Observed command or evidence |
|---|---|---|
| Locked setup with Python 3.12.16 and uv 0.13.6 | PASS | `make setup` with the installed uv executable resolved 102 packages and checked 98 installed packages. |
| Offline baseline/governed demo | PASS | `make demo` showed baseline answering the weather query and governed returning `refuse_scope`. |
| MLflow evaluation | PASS | `make evaluate` produced the expected `baseline=FAIL governed=PASS` across eight cases per variant. |
| Governed decision gate | PASS | `make gate` returned `PASS` with no failed metrics. |
| Regression and invalid-input semantics | PASS | The 62-test suite includes a governed citation regression exiting `1` and invalid gate inputs exiting `2`; the explicit baseline gate is also required to exit `1`. |
| Lint and formatting | PASS | `make verify` reported Ruff lint success and 23 files formatted. |
| Static types | PASS | `make verify` reported no mypy issues in 23 source files. |
| Tests | PASS | `make verify` reported 62 passed and one upstream MLflow/SQLAlchemy deprecation warning. |
| Repository, links, claims, CI, and traceability validation | PASS | `make repository` completed successfully; CI has `contents: read`, pinned actions, and no secret reference. |
| Generated evidence | PASS | `make evidence` and `make evidence-validate` generated and validated the local pack. |
| Committed sample evidence | PASS | `make sample-evidence-validate` validated schemas, hashes, provenance, decisions, cases, controls, and configured-content safety. |
| License and attribution consistency | PASS | Project metadata and `LICENSE` declare MIT; installed MLflow 3.17.2 metadata carries the Apache License 2.0 text. |
| Publishable-content scan | PASS | Repository validation found no personal absolute path or credential-shaped value in public text; generated runtime state is ignored. |

The first preflight in the review shell found that `uv` was not on `PATH`; no project command had
run at that point. The documented prerequisite now says so explicitly. The complete quickstart then
passed using the installed uv 0.13.6 executable. Dependency acquisition may require network access;
the required application/evaluation path remains offline after setup.

## Remote or owner-controlled checks

| Check | Result | Required owner action |
|---|---|---|
| Repository destination and public visibility | NOT VERIFIED | Confirm the existing `origin` is the intended destination, review history, and explicitly make it public or create the publication remote. |
| Repository rules and required CI checks | NOT VERIFIED | Configure branch/ruleset protection for `main` and require the `offline-assurance` CI job. |
| Hosted CI on the publication commit | NOT VERIFIED | Push only after authorization and observe a successful clean GitHub Actions run. |
| Dependabot alerts | NOT VERIFIED | Enable alerts in repository security settings. |
| Dependabot security updates | NOT VERIFIED | Enable security updates; the committed weekly uv/Actions update configuration is only the local configuration. |
| Private vulnerability reporting | FAIL / BLOCKER | Enable GitHub Private Vulnerability Reporting or document a real private security contact, then update `SECURITY.md`. |
| Public reporting path | FAIL / BLOCKER | Confirm that security reports stay private and sanitized quality/governance issues can use the issue forms. |
| Screenshots | NOT REQUIRED | Add only a real, sanitized, small screenshot if it improves the portfolio; record its provenance. The reproducible Markdown/JSON evidence is currently clearer. |

The GitHub CLI detected the configured `origin`, but its local authentication token was invalid;
therefore no hosted setting or current CI run was claimed as verified. No push, publication,
release, remote creation, or hosted setting change was performed.

## Known issues and accepted limits

- One upstream SQLAlchemy loader deprecation warning is emitted by MLflow during tests; it does not
  change the observed decisions.
- Evidence is local, unsigned, independently untimestamped, non-append-only, and not
  custody-controlled.
- The provider, corpus, and dataset are synthetic; lexical and ID checks do not establish semantic
  correctness or real-model safety.
- Redaction covers configured patterns only. Real sensitive data remains prohibited.
- A dirty working-tree provenance marker requires reviewer judgment; publish from a reviewed clean
  commit and regenerate evidence if application source, inputs, policy, catalog, or schemas change.

## Publication checklist

- [ ] Review the final diff and commit from a clean working tree.
- [ ] Re-run `make setup`, `make verify`, and the explicit baseline gate on the publication commit.
- [ ] Confirm the intended remote and public visibility; inspect commit history for sensitive data.
- [ ] Configure repository rules and the required `offline-assurance` CI check.
- [ ] Enable Dependabot alerts and security updates.
- [ ] Enable private vulnerability reporting or document a real private contact.
- [ ] Update `SECURITY.md` with the verified private reporting path.
- [ ] Push only with explicit authorization and observe hosted CI.
- [ ] Publish a release only if separately authorized; no release is required for the portfolio.
