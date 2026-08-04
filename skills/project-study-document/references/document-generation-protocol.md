# Final Study Document Generation Protocol

Transform a ready learning bundle into one durable artifact. The process is fail-closed and uses a unique in-memory Step/chapter map, exact source excerpts, a temporary sibling file, two validation passes, a real cold-start report, and one unified release receipt.

The parent `scripts/finalize_project_study.py` is the sole formal commit entry. This protocol describes the candidate it consumes; it does not authorize a model or companion Skill to write the formal target directly.

## 1. Readiness decision

Formal generation requires a fresh passing manifest from:

```powershell
python scripts/validate_finalization_bundle.py --ledger PROJECT_STUDY_LOG.md --qa PROJECT_STUDY_QA.md
```

The manifest must report a final route, complete required scenarios/NODEs/dependencies, no open/retest questions, no pending learner response, no unresolved corrections or stale promoted wording, no done Step without durable knowledge, no hidden-chat Q&A dependency, explicit question-phase closure, explicit consent, and zero record-validation errors.

Any blocker returns a readiness report. Only an explicit early-draft request permits `status: incomplete-draft` under a separate target; a draft lists all blockers and cannot use `validation_status: validated`.

## 2. Source-bundle lock

Lock paths, schema, last transaction IDs, and immutable revision for:

| Source class | Expected content | Treatment |
| --- | --- | --- |
| LOG | authoritative state, route, RUN/NODE/K/SRC/M/C/EXP/CMP | read fully; record last TX |
| Q&A | all questions, standalone answers, feedback | read fully; reject hidden chat references |
| repository | revision, entrypoints, symbols, configs, tests | pin immutable revision; verify promoted claims |
| paper/docs | claims, formulas, official docs | record exact source/version |
| runtime | commands, logs, outputs, metrics | separate executed from suggested |
| experiments | successes, failures, negative results | retain interpretation-changing results |

Missing evidence is disclosed. A ledger pointer never substitutes for direct verification of a high-impact claim.

## 3. Build the knowledge graph

Derive abstractions from durable learning records, not repository popularity or model memory. For each abstraction collect related RUN/NODE/K, source/paper evidence, I/O or Shape/state boundary, upstream/downstream relationships, Q/M/C, mastery behavior, and unresolved limits.

Order chapters by prerequisites, primary runtime order, inserted dependencies, alternate scenarios/shared differences, architecture reconstruction, and reproduction/comparison/extension.

## 4. Build a unique Step and chapter manifest

Enumerate every required Step/micro Step once. Each coverage row records status, durable knowledge, RUN/NODE/K, evidence, Q/M/C, behavior evidence, UNIT IDs, and accepted skip impact.

Build one in-memory mapping before rendering:

```text
CHAPTER ID -> unique title -> unique explicit anchor -> one completed Step -> complete textbook content
```

Gates before rendering:

- Step coverage IDs are unique;
- CHAPTER IDs, headings, and anchors are unique;
- every done Step maps to one standalone chapter;
- skipped Steps are not presented as learned;
- completed/mapped/skipped/unmapped counts reconcile and unmapped is zero.

Do not create a second chapter for an already mapped Step; revise the existing map.

## 5. Standalone chapter contract

Each chapter implements the complete 20-item contract in the companion Skill. A source excerpt is accepted only when its relative path, start/end line, and fenced contents match the locked repository. Important QA is taught in the chapter body and also remains traceable in the Q section.

A route row, takeaway, pseudocode fragment, or cross-reference is not a textbook chapter. `详见 chat`, `同上`, `前文已解释`, circular chapter references, and unexplained `不涉及` are forbidden. A genuinely inapplicable field explains why and gives the applicable evidence/skill instead.

## 6. Synthesis rules

The document is not chronological chat. Include highest-confidence conclusions, project identity/decision context, mechanisms explaining most behavior, evidence strength, failures/negative results/limitations, what changed understanding, reproducibility evidence, related methods, composition hypotheses, and one next action.

Use the latest canonical correction globally. Historical old wording appears only in the correction history and is labelled historical/stale. Distinguish `已确认`, `可推断`, `背景知识`, and `待验证`.

For visuals, prefer the smallest useful linear chain or table; use Mermaid for multi-layer call/data/state graphs and label RUN/NODE IDs. Avoid fragile large ASCII art.

## 7. One-pass assembly and atomic commit

1. Confirm output path and overwrite choice.
2. Create a temporary sibling file in the same directory.
3. Instantiate schema 2.0 once from the unique Step/chapter map.
4. Set real ISO generation time, immutable revision (or explicit `uncommitted:<hash>`), source LOG/QA paths, source TX, readiness receipt, and source limitations.
5. Set `status: complete`, `validation_status: pending` for preflight.
6. Run:

```powershell
python skills/project-study-document/scripts/validate_study_document.py <temp> --ledger PROJECT_STUDY_LOG.md --qa PROJECT_STUDY_QA.md --repo-root <PROJECT_ROOT> --publication --preflight
```

7. On any error, do not touch the target. Rebuild the affected UNIT map/section and reassemble; never use unconstrained global replacement or tail append.
8. After zero preflight errors, change only `validation_status` to `validated`.
9. Run a real fresh-model/no-chat cold-start against the exact validated candidate and save its per-Step JSON report.
10. Run final validation without `--preflight` and with `--publication --cold-start-report <REPORT>`.
11. Read back frontmatter, TOC, counts, all CHAPTER headings/anchors, important questions, corrections, evidence index, and next action.
12. Stage the target through `finalize_project_study.py --publication`, then create the only success marker through `release_transaction.py`. The finalizer's `release-pending` result cannot authorize a saved claim.

Code fences must balance and all content must remain within intended heading boundaries. The final receipt records path, revision, TX/readiness IDs, coverage counts, final validation, cold-start evidence, and limitations.
