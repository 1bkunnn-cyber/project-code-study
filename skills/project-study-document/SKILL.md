---
name: project-study-document
description: This skill should be used when a learner has completed a project-code-study route, explicitly closed the question phase, passed finalization readiness, and asks to "生成学习文档", "整理最终源码学习笔记", or create a standalone evidence-grounded Markdown document from which every completed Step can be relearned.
version: 3.0.0
---

# Project Study Document

## Goal

Transform a ready `project-code-study` evidence bundle into one self-contained Markdown document from which every completed Step can be relearned without the original chat. Reconstruct from verified records and source evidence; never concatenate Step responses or invent missing teaching.

## Fail-closed entry boundary

Run `scripts/validate_finalization_bundle.py --ledger PROJECT_STUDY_LOG.md --qa PROJECT_STUDY_QA.md` before planning or writing. Formal generation is allowed only when `ready: true`, including explicit question-phase closure and learner consent. Use the parent Skill's `scripts/finalize_project_study.py` as the unique commit entry; direct target writes are not formal generation.

If any field blocks:

- do not create or overwrite a `complete` document;
- return the full readiness report and one minimum backfill action;
- hand control back to `project-code-study`;
- generate only `status: incomplete-draft` under a separate target when the learner explicitly requests an early draft, and list every blocker in frontmatter/body.

Direct invocation does not bypass the gate. Silence, elapsed time, the last numbered Step, or a polished ledger is not consent.

## Required resources

Read completely before writing:

- `references/document-generation-protocol.md`: source lock, unique UNIT map, temporary assembly, preflight, and atomic commit.
- `references/important-question-selection.md`: select questions by NODE-unlocking and learning impact.
- `references/quality-gates.md`: readiness, independent relearning, evidence/correction, and cold-start gates.
- `assets/PROJECT_STUDY_DOCUMENT.template.md`: canonical schema 2.0 textbook structure.

Use `scripts/validate_study_document.py` after assembly.

## Default output

Prepare one candidate for `PROJECT_STUDY_DOCUMENT.md` in the studied project root. Let `scripts/finalize_project_study.py` decide the target replacement after preflight and final validation. Never overwrite silently or bypass that entry.

## Language policy

This policy applies to the generated `PROJECT_STUDY_DOCUMENT.md`, not to the companion Skill's internal implementation documentation. Use Simplified Chinese (`zh-CN`) for the final document by default. Write all learner-facing titles, explanations, table headings, captions, conclusions, limitations, and next actions in Chinese unless the learner explicitly requests another language. Preserve source-code symbols, commands, paths, formulas, schema keys, IDs, and fixed protocol enum values exactly; explain them in Chinese instead of translating identifiers that validators or source references depend on.

The language declared in frontmatter must match the actual document body. A few necessary English identifiers do not make a document bilingual. Do not add a full English duplicate or English appendix unless the learner explicitly asks for one.

## Workflow

### 1. Revalidate readiness and consent

Run the bundle validator immediately before source lock. Record its manifest and successful LOG/QA transaction IDs. A failed manifest stops formal generation.

### 2. Lock the source bundle

Read the complete LOG and Q&A. Lock repository revision, source/paper/runtime evidence, experiments, comparisons, and relevant artifacts. Learning records are indexes/memory, not automatic proof; recheck promoted high-impact claims against linked evidence. Record unavailable sources.

### 3. Build one unique Step/chapter manifest

Enumerate every required Step and micro Step exactly once, including backfills and accepted skips. Build an in-memory map with one unique CHAPTER ID and explicit anchor per completed Step. Every done Step maps to one standalone chapter. A route row is navigation, not a chapter.

Order the teaching body by actual runtime and concept dependencies, not file layout, chat chronology, or Step numbering alone. Keep tutorial, reference, explanation, and how-to modes distinguishable.

### 4. Write standalone textbook chapters

Every completed Step chapter must answer all 20 items:

1. the problem this Step solves;
2. prerequisites;
3. its actual position in the project call chain;
4. upstream inputs and downstream outputs;
5. related RUN/NODE/micro-Step IDs;
6. exact source paths and line ranges;
7. exact key source excerpts;
8. paragraph-by-paragraph or line-by-line explanation;
9. variable, parameter, and state meaning;
10. input, output, concrete Shape, and state changes;
11. formulas and parameter calculations;
12. why this design was chosen;
13. alternative implementations and trade-offs;
14. common errors and their observable symptoms;
15. connection to previous and next NODEs;
16. one project-specific worked example;
17. important QA absorbed as complete teaching;
18. recall questions, exercises, and reference answers;
19. confirmed, inferred, and unverified evidence boundaries;
20. an observable chapter completion standard.

Administrative Steps teach durable navigation, audit, or evidence methods without fabricated technical mechanisms. Every source excerpt uses an exact relative path and line range and must byte-match the locked revision. Step 4.x, 6, and 10 use the mandatory specialist profiles enforced by the validator.

Forbidden fillers include `详见 chat`, `同上`, circular chapter references, and unexplained `不涉及此方面`. When a dimension truly does not apply, explain why, cite the evidence boundary, and state what replaces that dimension.

### 5. Include important questions and canonical corrections

Select by learning impact. Preserve learner intent, standalone canonical answer, evidence, affected mental model, and M/C IDs. Core mechanism questions are not excluded merely because they look local. Scan summary, chapters, important questions, and conclusions for stale patterns before promotion.

### 6. Assemble, cold-start, then commit one release

Follow `document-generation-protocol.md`:

1. render the entire unique chapter map into a temporary sibling file;
2. set real `generated_at`, immutable revision, source TX, and readiness TX/receipt;
3. use `status: complete`, `validation_status: pending` during preflight;
4. run the document validator with `--publication --preflight --ledger ... --qa ...`;
5. if preflight passes, change only `validation_status` to `validated`;
6. give that exact candidate to a fresh model with no chat and save its hash-bound per-Step report;
7. run final validation with `--publication --cold-start-report ...`;
8. read back frontmatter, TOC, CHAPTER/anchor counts, question/correction/evidence sections, and final actions;
9. let `finalize_project_study.py --publication` atomically stage the target;
10. commit QA, LOG, memory, document, readiness, validators, cold-start result, source revision, not-run boundary, and exact response hash through `release_transaction.py`.

Never repair a failed document by unconstrained string replacement or tail append. Rebuild the affected chapter map and reassemble the temporary file.

### 7. Cold-start acceptance

Static validation is necessary, not sufficient. Record a cold-start test for each completed Step: with no chat, recover objective/runtime position, call order, source explanation, I/O/Shape/state, important Q, exercise answer, and unverified boundary. A static proxy cannot set `cold_start_status: pass`. If a real fresh-host run was not performed, formal publication remains blocked and the capability is `not-run`.

## Receipt

Report `saved` only from a `COMMITTED` unified release receipt after target replacement and final readback. A finalizer `release-pending` result is not saved. Include release TX/DOC-TX, artifact hashes, repository revision, readiness, Step/chapter/Q coverage, validator results, real cold-start status, not-run boundaries, and limitations. Otherwise report `unsaved` or `release-pending`.

## Safety boundaries

Do not expose hidden reasoning, full chat transcripts, credentials, unauthorized private paths, or irrelevant personal data. Do not overstate mastery, execution, paper coverage, or experiment results. Missing evidence remains visible.
