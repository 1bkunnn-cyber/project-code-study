---
name: project-study-document
description: This skill should be used when a learner has completed a project-code-study route, has no remaining questions for the study round, and explicitly asks to "生成学习文档", "整理最终源码学习笔记", or create a final evidence-grounded Markdown study document containing important user questions and corrected conclusions.
version: 1.0.0
---

# Project Study Document

## Goal

Turn a completed `project-code-study` evidence bundle into one durable, self-contained Markdown learning document. Reconstruct the project from verified learning records and source evidence; do not concatenate Step responses or rewrite the chat transcript.

## Entry Boundary

Run only after the parent workflow confirms all required Steps and micro Steps are complete, audits have passed, substantive questions are answered or intentionally deferred, no learner response is pending, and the learner explicitly consents to generation.

If invoked directly, recheck those conditions. If they fail, return a short readiness report and hand control back to `project-code-study`; do not disguise an incomplete route as a final document. A user may explicitly request an incomplete draft, but its frontmatter and title must say `status: incomplete-draft` and list every blocking gap.

## Required Resources

Read these before writing:

- `references/document-generation-protocol.md`: evidence bundle, chapter planning, writing transaction, and results-report-inspired synthesis rules.
- `references/important-question-selection.md`: select and present important user questions without copying the whole Q&A history.
- `references/quality-gates.md`: completeness, evidence, correction, readability, and final acceptance checks.
- `assets/PROJECT_STUDY_DOCUMENT.template.md`: canonical single-file Markdown structure.

Use `scripts/validate_study_document.py` after writing the artifact.

## Default Output

Write one file in the studied project root:

```text
PROJECT_STUDY_DOCUMENT.md
```

Use another path only when the learner requests it. Do not split the document merely because it is long. Prefer a table of contents, concise reference tables, appendices, and internal links. If the target already exists, ask whether to update it or create a dated copy; never overwrite silently.

## Workflow

### 1. Revalidate readiness and consent

Confirm the dynamic route—not a hard-coded Step number—is complete. Check scenario/node/dependency coverage, mastery gates, open questions, pending active recall, corrections, stale claims, and user consent.

### 2. Lock the source bundle

Read the complete `PROJECT_STUDY_LOG.md` and `PROJECT_STUDY_QA.md` because this is a finalization action. Lock the repository revision, source/paper/runtime evidence, experiments, comparisons, and relevant generated artifacts. Record unavailable sources explicitly.

The learning records are memory and indexes, not automatic proof. Recheck high-impact technical claims against their linked evidence before promoting them into the document.

### 3. Derive the document plan

Identify the core learned abstractions from completed `RUN-`, `NODE-`, and knowledge records. Analyze their relationships and order chapters by actual runtime paths plus concept dependencies. Do not order chapters only by file layout, chat chronology, or Step number.

Within the single Markdown file, keep four reader modes distinguishable:

- tutorial: the coherent learning path through the project;
- reference: exact symbols, parameters, shapes, evidence IDs, and paths;
- explanation: design reasons, alternatives, and trade-offs;
- how-to: reproduction, verification, modification, or experiment actions.

### 4. Include important user questions

Select questions by learning impact, not recency. Include questions that changed a conclusion, exposed a misconception, unlocked a core node, clarified a shape/math/paper-code issue, affected reproduction, or led to a useful comparison or extension.

For every included question preserve the learner's intent, then provide the canonical answer, evidence, affected understanding, and linked correction IDs. Exclude routine syntax questions unless they materially changed project understanding. Keep a compact index of omitted Q IDs when traceability matters.

### 5. Write synthesis, not transcript

Use the template. Include the highest-confidence conclusions, what changed the learner's understanding, actual runtime call paths, core-node explanations, important questions, canonical corrections, limitations, unresolved items, related methods, module-composition ideas, reproducibility evidence, and next actions.

Separate `已确认`, `可推断`, `背景知识`, and `待验证`. Preserve negative results and failed attempts when they change interpretation. Use the latest canonical wording and remove known stale formulations.

### 6. Run quality gates

Apply `references/quality-gates.md`. A final document fails if a core runtime scenario is missing, an important included claim lacks evidence, a correction still uses stale wording, important user questions were silently omitted, mastery is overstated, or the document depends on hidden chat context.

### 7. Persist and verify

Write only after confirming the target. Read back frontmatter, table of contents, important-question section, correction section, evidence index, and final action section. Run:

```powershell
python skills/project-study-document/scripts/validate_study_document.py PROJECT_STUDY_DOCUMENT.md
```

If the companion skill is installed separately, run the validator from its actual installation path. Report `saved` with the artifact path and source revision, or `unsaved` with the reason. When authorized, add the artifact path and generation date to the learning ledger without rewriting its history.

## Quality and Safety Boundaries

- Do not create the document before explicit learner consent.
- Do not use temporary model memory as the primary source.
- Do not turn questions into invented learner quotes or expose hidden reasoning.
- Do not include credentials, private paths that the learner did not authorize, or irrelevant personal information.
- Do not claim complete mastery where the ledger records only exposure.
- Do not hide missing evidence behind polished prose.
