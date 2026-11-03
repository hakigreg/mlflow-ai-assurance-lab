# Release readiness

**Local review decision:** PASS  
**Public publication decision:** BLOCKED pending owner-controlled hosted settings

This record separates checks observed locally on 2026-11-02 from owner-controlled GitHub settings.
`PASS` applies only to the bounded synthetic lab and is not enterprise release authorization.

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
| Repository destination and public visibility | VERIFIED / PRIVATE | `origin/main` and local `main` resolve to `ab2b4e8`; explicitly change visibility only after final review. |
| Repository rules and required CI checks | PENDING PUBLICATION | GitHub Free returned `403` for the private repository; after making it public, configure a `main` ruleset requiring `offline-assurance`. |
| Hosted CI on the current commit | PASS | GitHub Actions run `41526813368` completed successfully for `ab2b4e8` on `main`. |
| Dependabot alerts | DISABLED / DEFERRED | Enable alerts in repository security settings; the owner accepted completing this later. |
| Dependabot security updates | DISABLED / DEFERRED | Enable security updates after alerts; the committed weekly uv/Actions configuration covers version updates only. |
| Private security contact | CONFIGURED | `SECURITY.md` directs private reports to `contacto@vektoria.io`; the owner must confirm that the mailbox is reachable and monitored. |
| Private vulnerability reporting | POST-PUBLICATION | GitHub exposes this feature for public repositories; consider enabling it as an additional channel after changing visibility. |
| Public issue path | PASS | Blank issues are disabled; the two issue forms require sanitized non-security reports and direct vulnerabilities to `SECURITY.md`. |
| Screenshots | NOT REQUIRED | Add only a real, sanitized, small screenshot if it improves the portfolio; record its provenance. The reproducible Markdown/JSON evidence is currently clearer. |

Read-only GitHub inspection confirmed the private repository, current synchronized commit, hosted
CI success, read-only default workflow permissions, and the disabled Dependabot settings. No
visibility, ruleset, security-setting, publication, release, or remote change was performed.

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
- [x] Document a real private security contact in `SECURITY.md`.
- [ ] Confirm that `contacto@vektoria.io` is reachable and monitored.
- [ ] After publication, consider enabling GitHub Private Vulnerability Reporting.
- [ ] Push only with explicit authorization and observe hosted CI.
- [ ] Publish a release only if separately authorized; no release is required for the portfolio.
