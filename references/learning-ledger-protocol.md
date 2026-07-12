# Learning Ledger Protocol

Use this protocol whenever creating, reading, updating, compacting, or recovering `PROJECT_STUDY_LOG.md`.

The canonical structure is `assets/PROJECT_STUDY_LOG.template.md` with schema version 3.0. This asset is the single source of truth for headings, order, tables, status values, and placeholders. Do not maintain a second prose copy of the template.

## 1. Purpose and boundaries

The ledger has four jobs:

1. Recover the learning state quickly after context loss.
2. Make evidence, uncertainty, misconceptions, and progress inspectable.
3. Select the next best learning activity from demonstrated need.
4. Supply trustworthy material for the final study note.

It is not a transcript, a scratchpad, a hidden-reasoning dump, a generic TODO list, or the final polished note.

## 2. Two-layer design

Maintain two layers in one file:

- Hot state: sections 0–12. Update these in place. They answer “where are we now?”
- History: milestone syntheses and the final session-log section. Append records that answer “how did we get here?”

On session start, read the current snapshot, mastery rows due for review, blocking open loops, unresolved misconceptions, and the latest session entry. Do not reread the entire history unless the current task requires it.

## 2.1 Creation and initialization

When no ledger exists and the user authorized writing:

1. Copy `assets/PROJECT_STUDY_LOG.template.md` to `<project-root>/PROJECT_STUDY_LOG.md` unchanged.
2. Confirm that the destination is inside the authorized project root or save location.
3. In a second, minimal edit, replace every `{{PLACEHOLDER}}` with known information or `待确认`.
4. Set dates, repository revision, permissions, current mode, and current Step from evidence.
5. Keep empty register sections and table headers intact.
6. Validate with `scripts/validate_learning_ledger.py` when Python is available.

Never generate a fresh structure from remembered instructions. Never overwrite an existing ledger. Never leave `{{PLACEHOLDER}}` values in an initialized project ledger.

The following are schema invariants:

- YAML `schema_version` stays `3.0` until the bundled template itself is intentionally revised.
- H2 names and order remain identical to the canonical asset.
- Existing table columns are not renamed, removed, reordered, or given project-specific variants.
- `## 14. 会话日志` remains the final H2 so entries can be appended at the end of the file.
- Unknown and irrelevant values use `待确认`, `无`, or `不适用（原因）`; sections are not deleted.

## 3. Stable IDs and single source of truth

Use stable IDs:

- `SRC-` source or evidence
- `K-` knowledge or skill
- `Q-` user question
- `U-` AI uncertainty
- `R-` reproduction risk
- `M-` misconception
- `EXP-` experiment or command
- `C-` source conflict

Register details once and reference the ID elsewhere. Never recycle an ID. When an item becomes obsolete, mark it `stale`; when finished, mark it closed/resolved. Do not delete history merely to make the ledger look clean.

## 4. Session start transaction

Before teaching:

1. Verify the ledger path and write authorization.
2. Read the current snapshot and latest session entry.
3. Compare the current branch/commit or available file revision with the recorded revision.
4. Calculate days since the last session when dates are available.
5. Check the review queue, blocking open loops, and `retest-due` misconceptions.
6. Select the session mode:
   - quick: review/recovery, no new major topic;
   - standard: review plus one bounded advance;
   - deep: sustained source tracing, experiment, or synthesis.
7. Propose one primary next action. If it conflicts with the user's immediate goal, explain the tradeoff and let the user decide.

If the learner returns after a gap, prioritize retrieval before new exposition. If the repository changed, revalidate only the conclusions linked to affected source IDs.

## 5. During-session capture

Capture state-changing information, not every sentence:

- a source was actually inspected;
- the learner demonstrated or failed a capability;
- a misconception appeared or was resolved after retest;
- a question changed the route or mental model;
- a command provided runtime evidence or failed meaningfully;
- a claim became confirmed, uncertain, contradicted, or stale;
- the user changed goals, constraints, or permissions.

Keep the learner's wording only when it reveals a useful mental model, recurring confusion, or explicit goal. Never store secrets, credentials, unnecessary personal information, or private content unrelated to learning.

## 6. Mastery transitions

Use observed behavior:

- explanation supports `explainable`;
- source/call/shape reconstruction supports `traceable`;
- a correct modification, debug, or experimental design supports `applied`;
- successful later retrieval or real execution supports `verified`.

Exposure, agreement, copying an answer, or self-confidence alone does not advance mastery. A learner may report confidence 5 while demonstrated level remains `introduced`; preserve that mismatch because it guides teaching.

Downgrade to `revisit` when later evidence reveals forgetting, brittle transfer, or a misconception. This is not failure; it is a scheduling signal.

## 7. Review scheduling

Schedule from performance rather than a fixed calendar:

- wrong or unable to answer: later in the same session or next day;
- correct only with hints: about 1–3 days;
- correct unaided: about 7 days;
- correctly applied in code/experiment: about 14–30 days;
- failed later transfer: return to 1–3 days with a different task form.

Rotate review form among explain, trace, predict, debug, and modify. Do not repeat the same wording until it becomes recognition rather than recall.

## 8. Session end transaction

After a meaningful session:

1. Update the current snapshot in place.
2. Update only state rows that changed.
3. Add or update source, open-loop, misconception, question, experiment, and conflict records.
4. Update mastery using observed evidence.
5. Schedule reviews.
6. Append one session-log entry, including `blocked` or `interrupted` outcomes honestly.
7. Set exactly one primary next action and a suggested return time.
8. Confirm that the written ledger matches what was actually read, discussed, or run.

If nothing meaningful changed, do not add a noisy session entry. Updating `Last meaningful update` is preferable to pretending progress.

## 9. Compaction and archiving

Compact when the current file becomes difficult to scan, contains repeated closed items, or approaches the host's practical context limit.

Compaction order:

1. Remove accidental duplicates while preserving the canonical ID.
2. Mark stale/closed rows instead of repeating them in active sections.
3. Create a milestone synthesis from old session entries.
4. Move only old closed session entries to `PROJECT_STUDY_LOG_ARCHIVE.md` after user authorization.
5. Keep unresolved items, mastery state, source IDs they depend on, and the latest milestone synthesis in the main ledger.

Never archive merely by age if the entry still explains an open question, misconception, experiment, or source conflict. Record the archive path and date in Maintenance State.

## 10. Human edits and conflicting writers

Treat user edits as authoritative unless they contradict observable evidence; in that case record the conflict and ask. Before writing, reread the target section if another agent or session may have edited it. Prefer minimal section-level patches over rewriting the whole file.

If two sessions produce conflicting updates, preserve both claims, source them, and create a `C-` conflict record. Do not silently choose the newest statement.

## 11. Recovery when the ledger is missing or damaged

- Missing but authorized: recreate from the template, label reconstructed fields, and ask the user to confirm the restart brief.
- Missing and unauthorized: keep a chat-only ledger and state that it is unsaved.
- Partially corrupted: preserve readable content, create a recovery copy only with authorization, and reconstruct current state from source evidence plus recent conversation.
- Older schema: do not overwrite it. Ask before migration, preserve a backup or archive when authorized, copy the current canonical template, then migrate confirmed content into matching sections with stable IDs. Mark reconstructed fields and validate before replacing the active path.

## 12. Quality check

Before closing an update, verify:

- The restart brief can orient a new agent in about 60 seconds.
- The next action follows from a demonstrated gap, user goal, or blocking evidence need.
- Every promoted mastery level has behavioral evidence.
- Every important uncertainty has an owner/action or accepted-risk status.
- Repository claims point to source IDs and revisions.
- The session log describes what happened, not what the AI intended to do.
- No sensitive or irrelevant conversation content was stored.
