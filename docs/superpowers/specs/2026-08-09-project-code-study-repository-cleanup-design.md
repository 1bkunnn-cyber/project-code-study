# Project Code Study Repository Cleanup Design

Date: 2026-08-09

## Goal

Turn the repository into a lean publishable Skill package. Keep only runtime instructions, protocols, templates, control scripts, tests, user-facing release documentation, license, and host metadata. Remove historical process artifacts that are already recoverable from Git history and delete remote branches that are fully contained in `main`.

## Keep boundary

The following remain in the working tree and GitHub `main`:

- `SKILL.md`, `README.md`, `CHANGELOG.md`, `LICENSE`;
- `GITHUB_RESEARCH_AND_ACKNOWLEDGEMENTS.md` because it is the durable license/adoption record;
- `agents/openai.yaml` because it is host metadata;
- all current `assets/`, `references/`, `scripts/`, `tests/`, and `skills/project-study-document/` files;
- `.gitignore` and Git metadata.

No learner project artifact, Claude conversation, training output, cache, or private file is part of this repository cleanup.

## Delete boundary

Delete these 15 root-level process artifacts:

1. `IMPLEMENTATION_AND_TEST_REPORT_6.0.0.md`
2. `IMPLEMENTATION_AND_TEST_REPORT_6.1.0.md`
3. `PROJECT_CODE_STUDY_V6_2_IMPLEMENTATION_REPORT.md`
4. `REMEDIATION_REPORT_5.0.0.md`
5. `REMEDIATION_REPORT_5.1.0.md`
6. `REMEDIATION_REPORT_5.2.0.md`
7. `REMEDIATION_REPORT_5.3.0.md`
8. `REMEDIATION_REPORT_5.4.0.md`
9. `REMEDIATION_REPORT_5.5.0.md`
10. `SELF_TEST_REPORT_5.4.0.md`
11. `WORKFLOW_CLOSURE_AUDIT_5.4.0.md`
12. `improvement-plan-project-code-study.md`
13. `quality-report-project-code-study-5.1.0.md`
14. `quality-report-project-code-study.md`
15. `update-report-project-code-study-5.1.0.md`

Delete all eight process-only files under `docs/superpowers/`, including this cleanup design after the implementation plan has been committed:

- the three existing version design documents;
- the three existing version implementation plans;
- this cleanup design document;
- the cleanup implementation plan created after approval.

The final working tree therefore contains no `docs/superpowers/` directory. The designs and plans remain permanently recoverable from Git history.

Delete the empty, untracked local `.agents/` directory. Keep tracked `agents/openai.yaml`.

## Consolidation edits

Before deletion, preserve only durable information:

- `README.md`: remove links to the v6.2 implementation report and keep the concise mechanism summary already present;
- `CHANGELOG.md`: remove the old remediation-report link; the release entry itself remains the historical summary;
- `scripts/validate_skill_structure.py`: stop requiring the v6.2 implementation report;
- tests or docs: remove any remaining live references to deleted paths.

Do not move process reports into an archive directory because that would retain the same repository clutter under a different name.

## Remote branch cleanup

Remote ancestry was checked before design approval:

- `origin/codex/skill-reliability-v5` equals `origin/main` at `5dba546`;
- `origin/master` is an ancestor of `origin/main` and has no unique commits;
- the legacy line is also reachable from tags `v4.0.0`, `v4.1.0`, `v4.2.0`, and `v5.0.0`.

After the cleanup commit is pushed to `main`, delete remote branches `codex/skill-reliability-v5` and `master`. Do not delete tags. Keep only `main` as the remote branch.

## Verification

The cleanup is accepted only when:

1. no deleted filename is referenced by a live file;
2. `rg --files` shows the intended lean tree and no empty `.agents/`;
3. `python -m unittest discover -s tests -p "test_*.py"` retains the expected one explicit real-host skip and no failure;
4. `python scripts/validate_skill_structure.py` passes;
5. LOG 4.2 and QA 1.2 templates validate;
6. `git diff --check` passes;
7. the protected learner sample hashes remain unchanged;
8. the cleanup commit is pushed to `main` and `git ls-remote --heads origin` shows only `refs/heads/main`.

## Recovery and risk

Every deleted tracked file remains recoverable from commit `5dba546` or earlier history. Remote branch deletion does not remove reachable commits because `main` contains both branches and legacy tags remain. No force push, history rewrite, tag deletion, or learner-project mutation is allowed.
