# Project Code Study Repository Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce the published Skill repository to current runtime, maintenance, test, release, license, and host-metadata files while keeping all removed process history recoverable in Git.

**Architecture:** Add an executable repository-hygiene gate first, then consolidate the few live links that still point to process reports and delete the complete approved process-artifact set. Verify the runtime package before committing, fast-forward the cleanup to `main`, and remove only local/remote branches proven fully reachable from `main`.

**Tech Stack:** Markdown Agent Skill, Python `unittest`, PowerShell, Git, GitHub HTTPS remote.

## Global Constraints

- Keep all current `assets/`, `references/`, `scripts/`, `tests/`, `skills/project-study-document/`, `agents/openai.yaml`, release docs, license, and `.gitignore`.
- Delete exactly the 15 approved root process artifacts and all eight `docs/superpowers` design/plan files, including this plan and its design after their commits preserve history.
- Delete local empty `.agents/`; keep tracked `agents/`.
- Do not modify the learner project, authorized Claude JSONL, training outputs, caches, tags, or Git history.
- Never force-push. Push the cleanup commit to `main` before deleting redundant branches.
- Delete a branch only if `git merge-base --is-ancestor <branch> main` succeeds.

---

### Task 1: Permanent repository-hygiene gate

**Files:**

- Modify: `tests/test_skill_structure_v6.py`
- Modify: `scripts/validate_skill_structure.py`

**Interfaces:**

- Produces: `validate_repository_hygiene(root: Path) -> list[str]`.
- Produces: `PROCESS_ARTIFACT_PATTERNS: tuple[str, ...]` covering root reports and `docs/superpowers`.
- Consumed by: `validate_structure(root)` and the static-structure unit test.

- [ ] **Step 1: Add a failing hygiene test**

Add a test that calls `validate_repository_hygiene(ROOT)` and expects no errors. Add a temporary-directory test containing `REMEDIATION_REPORT_9.9.9.md` and `docs/superpowers/specs/process.md`, and assert that both are reported.

- [ ] **Step 2: Run the focused test and observe the intended failure**

Run:

```powershell
python -m unittest tests.test_skill_structure_v6 -v
```

Expected before deletion: the live repository test fails and lists the current process artifacts.

- [ ] **Step 3: Implement the hygiene validator**

In `scripts/validate_skill_structure.py`, define root filename regexes for `REMEDIATION_REPORT_*`, `IMPLEMENTATION_AND_TEST_REPORT_*`, `SELF_TEST_REPORT_*`, `WORKFLOW_CLOSURE_AUDIT_*`, `PROJECT_CODE_STUDY_*_IMPLEMENTATION_REPORT.md`, `quality-report-*`, `improvement-plan-*`, and `update-report-*`. Also report every file under `docs/superpowers/`. Call this function from `validate_structure()`.

Remove `PROJECT_CODE_STUDY_V6_2_IMPLEMENTATION_REPORT.md` from `REQUIRED_PATHS`; runtime validation must not depend on a process report.

- [ ] **Step 4: Run the focused test and confirm only current clutter causes failure**

Run the same unittest command. The temporary-directory detection test must pass; the repository-clean test remains red until Task 2 deletes approved artifacts.

### Task 2: Consolidate durable documentation and delete process artifacts

**Files:**

- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Delete: the 15 root process files listed in the approved design
- Delete: every file under `docs/superpowers/plans/` and `docs/superpowers/specs/`
- Delete locally: empty untracked `.agents/`

**Interfaces:**

- README remains the behavior/user entry point.
- CHANGELOG remains the release-history index.
- Git history is the recovery interface for deleted process reports/specs/plans.

- [ ] **Step 1: Remove live links to deleted reports**

Delete both README links to `PROJECT_CODE_STUDY_V6_2_IMPLEMENTATION_REPORT.md`. Remove the CHANGELOG sentence linking `REMEDIATION_REPORT_5.0.0.md`. Do not remove their concise mechanism/release summaries.

- [ ] **Step 2: Delete all approved tracked process artifacts with `apply_patch`**

Delete the 15 exact root files and all eight `docs/superpowers` files. Do not delete `GITHUB_RESEARCH_AND_ACKNOWLEDGEMENTS.md`, `CHANGELOG.md`, `README.md`, or any runtime/test file.

- [ ] **Step 3: Delete the empty local `.agents/` directory**

Resolve `D:\skills\project-code-study\.agents`, verify it is an empty directory inside the Skill root, and remove only that directory. Do not touch tracked `agents/openai.yaml`.

- [ ] **Step 4: Prove references and tree are clean**

Run:

```powershell
rg -n -e 'REMEDIATION_REPORT|IMPLEMENTATION_AND_TEST_REPORT|SELF_TEST_REPORT|WORKFLOW_CLOSURE_AUDIT|PROJECT_CODE_STUDY_V6_2_IMPLEMENTATION_REPORT|quality-report-project-code-study|improvement-plan-project-code-study|update-report-project-code-study|docs/superpowers' .
rg --files | Sort-Object
```

Expected: the reference scan returns no match; the tree contains only the keep boundary.

### Task 3: Full runtime and protected-sample verification

**Files:**

- Test only: repository runtime and test files
- Read-only: authorized learner sample hashes

**Interfaces:**

- Consumes: current repository after Task 2.
- Produces: test counts, structure status, template status, diff status, and unchanged protected hashes.

- [ ] **Step 1: Run the full unit/regression suite**

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Expected: no failures and exactly the existing explicit real-host golden-conversation skip.

- [ ] **Step 2: Run static and template validators**

```powershell
python scripts/validate_skill_structure.py
python scripts/validate_learning_ledger.py assets/PROJECT_STUDY_LOG.template.md --template
python scripts/validate_learning_ledger.py assets/PROJECT_STUDY_QA.template.md --template
git diff --check
```

Expected: all pass.

- [ ] **Step 3: Recompute protected hashes**

Recompute SHA-256 for the audit report, QA, LOG, DOCUMENT, MEMORY, authorized Claude JSONL, and read-only research_stitching set. Compare the six priority hashes with the v6.2 baseline and confirm that no command wrote to the learner project.

### Task 4: Commit, publish `main`, and remove redundant branches

**Files:**

- Git index/history only
- GitHub refs only

**Interfaces:**

- Produces: one cleanup commit on `main` and a single remote branch `refs/heads/main`.

- [ ] **Step 1: Review and commit the cleanup**

Inspect `git status`, `git diff --stat`, deleted paths, and `git diff --check`. Stage only the approved cleanup and hygiene changes. Commit with:

```text
chore(repo): remove historical process artifacts
```

- [ ] **Step 2: Push the cleanup to default `main` without force**

```powershell
git push origin HEAD:main
```

Verify `git ls-remote origin HEAD refs/heads/main` returns the cleanup commit for both refs.

- [ ] **Step 3: Clean local branches**

Create/switch local `main` tracking `origin/main` at the cleanup commit. Recheck ancestry, then delete local `codex/skill-reliability-v5` and stale local `master` with ordinary `git branch -d`; do not use `-D`.

- [ ] **Step 4: Clean remote branches**

Recheck that `origin/codex/skill-reliability-v5` and `origin/master` are ancestors of `origin/main`, then delete both remote branches with ordinary Git push-delete. Keep all tags.

- [ ] **Step 5: Verify final repository state**

Run:

```powershell
git ls-remote --heads origin
git branch -vv
git status --branch --short
```

Expected: GitHub exposes only `main`; locally only `main` remains and tracks `origin/main`; worktree is clean.
