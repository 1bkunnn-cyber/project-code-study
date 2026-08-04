# Project Code Study v6.1 Compact Handbook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Execution status (2026-08-04):** Implemented and verified. The prospective
checkboxes below preserve the TDD plan; actual changes, tests, sample audit, and
not-run boundaries are recorded in `IMPLEMENTATION_AND_TEST_REPORT_6.1.0.md`.

**Goal:** Replace the bloated schema 2.0 textbook contract with a compact, searchable, source-grounded schema 2.1 Step manual without weakening independent relearning.

**Architecture:** Keep one release-bound Markdown document and one chapter per completed Step, but render each chapter as an eight-slot progressive-disclosure entry with explicit reading profiles. Extend the validator with content, source-excerpt, duplication, index, deep-dive, and retrieval-oriented cold-start gates while keeping schema 2.0 readable for migration.

**Tech Stack:** Python 3.9+ standard library, Markdown, JSON, `unittest`, Git.

## Global Constraints

- Do not modify the pedestrian-detection project or its QA/LOG/memory/document samples.
- Keep schema 2.0 readable, but require schema 2.1 for new formal publication.
- Do not add a documentation-site runtime, database, vector store, model SDK, or network dependency.
- Preserve fail-closed readiness, consent, receipt, source evidence, correction and host-claim boundaries.
- Do not report static validation as a fresh-host result.

---

### Task 1: Compact Handbook Validation Contract

**Files:**
- Create: `tests/test_compact_handbook_v61.py`
- Modify: `skills/project-study-document/scripts/validate_study_document.py`

**Interfaces:**
- Produces: `validate_compact_step_contract(step_id, block, repo_root) -> list[str]`
- Produces: `validate_excerpt_budget(block, profile, repo_root) -> list[str]`
- Produces: `validate_chapter_duplication(chapters) -> list[str]`

- [x] Write failing tests proving an eight-slot compact Step passes only after the new validator exists.
- [x] Write failing tests for over-budget prose, whole-file copying, excessive excerpt lines and duplicate long paragraphs.
- [x] Run the focused tests and verify failures name missing compact-contract behavior.
- [x] Implement profile budgets, exact-source coverage limits and normalized paragraph duplication checks.
- [x] Run focused tests and the existing schema 2.0 tests.

### Task 2: Navigation, Shared Deep Dives and QA Lookup

**Files:**
- Modify: `tests/test_compact_handbook_v61.py`
- Modify: `skills/project-study-document/scripts/validate_study_document.py`
- Modify: `scripts/cold_start_test.py`
- Modify: `assets/PROJECT_STUDY_COLD_START_REPORT.template.json`

**Interfaces:**
- Produces: `validate_lookup_index(text, completed_steps, required_qids) -> list[str]`
- Extends: `evaluate_report(..., handbook_schema=None) -> list[str]`

- [x] Add failing tests for missing Step/keyword/source/Q-ID lookup rows and broken deep-dive anchors.
- [x] Add a failing schema 2.1 cold-start fixture that explains a Step but cannot locate it.
- [x] Implement lookup/deep-dive validation and schema-aware retrieval fields.
- [x] Prove local core explanation plus one document-local deep dive passes while chat/external hidden context fails.
- [x] Run focused and full unit tests.

### Task 3: Protocol, Template and Version Migration

**Files:**
- Modify: `SKILL.md`
- Modify: `skills/project-study-document/SKILL.md`
- Modify: `skills/project-study-document/assets/PROJECT_STUDY_DOCUMENT.template.md`
- Modify: `skills/project-study-document/references/document-generation-protocol.md`
- Modify: `skills/project-study-document/references/important-question-selection.md`
- Modify: `skills/project-study-document/references/quality-gates.md`
- Modify: `scripts/finalize_project_study.py`

**Interfaces:**
- Publication requires: `schema_version: "2.1"` and `handbook_mode: "layered-step-manual"`.

- [x] Replace “textbook chapter” wording with the positive eight-slot Step manual recipe.
- [x] Add reading profiles, source budgets, shared deep dives and QA lookup rules to the canonical template.
- [x] Keep schema 2.0 migration diagnostics explicit; do not silently upgrade existing documents.
- [x] Run structure validation and all unit tests.

### Task 4: Documentation, Research and Acknowledgements

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `GITHUB_RESEARCH_AND_ACKNOWLEDGEMENTS.md`
- Create: `IMPLEMENTATION_AND_TEST_REPORT_6.1.0.md`

- [x] Record repository, core idea, implementation shape, license, activity, suitability and adoption decision for each new reference.
- [x] Thank the reference projects explicitly and state that no code/protocol text was copied.
- [x] Explain the schema 2.1 reading model, budgets, anti-copy gate, cold-start lookup and migration in Chinese and English README sections.
- [x] Record exact tests and `not-run` host boundaries.

### Task 5: Verification and Publication

**Files:**
- Review all modified files and repository status.

- [x] Run static Skill structure validation.
- [x] Run all 88+ unit tests.
- [x] Run template validation and focused schema 2.1 publication/cold-start tests.
- [x] Run the read-only sample dual audit and verify no sample hash or file changed.
- [x] Review `git diff --check`, scoped diff and secret/private-path exposure.
- [ ] Create a Conventional Commit and push the current feature branch to `origin`.
