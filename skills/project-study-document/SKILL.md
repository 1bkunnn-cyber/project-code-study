---
name: project-study-document
description: This skill should be used when a learner has completed a project-code-study route, explicitly closed the question phase, passed finalization readiness, and asks to "生成学习文档", "整理最终源码学习笔记", or create a standalone evidence-grounded Markdown document from which every completed Step can be relearned.
version: 2.0.0
---

# Project Study Document

## Goal

Transform a ready `project-code-study` evidence bundle into one self-contained Markdown document from which every completed Step can be relearned without the original chat. Reconstruct from verified records and source evidence; never concatenate Step responses or invent missing teaching.

## Fail-closed entry boundary

Run `scripts/validate_finalization_bundle.py --ledger PROJECT_STUDY_LOG.md --qa PROJECT_STUDY_QA.md` before planning or writing. Formal generation is allowed only when `ready: true`, including explicit question-phase closure and learner consent.

If any field blocks:

- do not create or overwrite a `complete` document;
- return the full readiness report and one minimum backfill action;
- hand control back to `project-code-study`;
- generate only `status: incomplete-draft` when the learner explicitly requests an early draft, and list every blocker in frontmatter/body.

Direct invocation does not bypass the gate. Silence, elapsed time, the last numbered Step, or a polished ledger is not consent.

## Required resources

Read completely before writing:

- `references/document-generation-protocol.md`: source lock, unique UNIT map, temporary assembly, preflight, and atomic commit.
- `references/important-question-selection.md`: select questions by NODE-unlocking and learning impact.
- `references/quality-gates.md`: readiness, independent relearning, evidence/correction, and cold-start gates.
- `assets/PROJECT_STUDY_DOCUMENT.template.md`: canonical schema 1.2 structure.

Use `scripts/validate_study_document.py` after assembly.

## Default output

Write one `PROJECT_STUDY_DOCUMENT.md` in the studied project root unless the learner chooses another path. If it exists, ask whether to update it or create a dated copy. Never overwrite silently.

## Language policy

Use Simplified Chinese (`zh-CN`) for the final document by default. Write all learner-facing titles, explanations, table headings, captions, conclusions, limitations, and next actions in Chinese unless the learner explicitly requests another language. Preserve source-code symbols, commands, paths, formulas, schema keys, IDs, and fixed protocol enum values exactly; explain them in Chinese instead of translating identifiers that validators or source references depend on.

The language declared in frontmatter must match the actual document body. A few necessary English identifiers do not make a document bilingual. Do not add a full English duplicate or English appendix unless the learner explicitly asks for one.

## Workflow

### 1. Revalidate readiness and consent

Run the bundle validator immediately before source lock. Record its manifest and successful LOG/QA transaction IDs. A failed manifest stops formal generation.

### 2. Lock the source bundle

Read the complete LOG and Q&A. Lock repository revision, source/paper/runtime evidence, experiments, comparisons, and relevant artifacts. Learning records are indexes/memory, not automatic proof; recheck promoted high-impact claims against linked evidence. Record unavailable sources.

### 3. Build one unique Step/UNIT manifest

Enumerate every required Step and micro Step exactly once, including backfills and accepted skips. Build an in-memory map with one unique UNIT ID and explicit anchor per unit. Every done Step maps to at least one UNIT; every UNIT maps back to at least one done Step. A route row is navigation, not a UNIT.

Order the teaching body by actual runtime and concept dependencies, not file layout, chat chronology, or Step numbering alone. Keep tutorial, reference, explanation, and how-to modes distinguishable.

### 4. Write independent relearning UNITs

Every UNIT must answer:

1. what problem the Step solves;
2. its actual RUN/NODE position;
3. upstream inputs and downstream outputs;
4. source execution order;
5. Shape/formula/config/state changes;
6. rationale, alternatives, trade-offs, and failure modes;
7. important learner questions that unlocked understanding;
8. historical misconception and current canonical correction;
9. evidence status and unresolved boundary;
10. a self-check plus complete reference answer;
11. connection to the next NODE or concept.

Administrative Steps teach durable navigation, audit, or evidence methods without fabricated technical mechanisms. Step 5/6/9/10 receive complete relearning content, not administrative summaries.

Forbidden fillers include `详见 chat`, `同上`, circular `详见对应 UNIT`, and unexplained `不涉及此方面`. When a dimension truly does not apply, explain why, cite the evidence boundary, and state what replaces that dimension.

### 5. Include important questions and canonical corrections

Select by learning impact. Preserve learner intent, standalone canonical answer, evidence, affected mental model, and M/C IDs. Core mechanism questions are not excluded merely because they look local. Scan summary, UNITs, important questions, and conclusions for stale patterns before promotion.

### 6. Assemble once, validate twice, commit atomically

Follow `document-generation-protocol.md`:

1. render the entire unique UNIT map into a temporary sibling file;
2. set real `generated_at`, immutable revision, source TX, and readiness TX/receipt;
3. use `status: complete`, `validation_status: pending` during preflight;
4. run the document validator with `--preflight --ledger ... --qa ...`;
5. if preflight passes, change only `validation_status` to `validated` and run final validation without `--preflight`;
6. read back frontmatter, TOC, UNIT/anchor counts, question/correction/evidence sections, and final actions;
7. atomically replace the target only after final validation passes.

Never repair a failed document by unconstrained string replacement or tail append. Rebuild the affected UNIT map and reassemble the temporary file.

### 7. Cold-start acceptance

Static validation is necessary, not sufficient. Record a cold-start test for each UNIT when release evidence is required: with no chat, recover objective/runtime position, call order, I/O/Shape/state, important Q, canonical correction, self-check, next NODE, and unverified boundary. If a real cross-model run was not performed, report it as an outstanding observation rather than claiming it passed.

## Receipt

Report `saved` only after target replacement and final readback. Include path, repository revision, source/readiness transaction IDs, Step/UNIT/Q coverage, validator results, cold-start evidence status, and remaining limitations. Otherwise report `unsaved` and preserve the temporary/readiness diagnostics.

## Safety boundaries

Do not expose hidden reasoning, full chat transcripts, credentials, unauthorized private paths, or irrelevant personal data. Do not overstate mastery, execution, paper coverage, or experiment results. Missing evidence remains visible.
