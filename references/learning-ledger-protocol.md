# Learning Record Protocol

Use this protocol whenever creating, reading, updating, validating, compacting, or migrating project-code-study records.

## 1. Record architecture

Schema 4.0 uses two linked files:

- `PROJECT_STUDY_LOG.md`: compact working state and trustworthy learning ledger.
- `PROJECT_STUDY_QA.md`: detailed substantive questions, follow-ups, complete answers, learner reflections, and feedback.

The log retains its original durable jobs: recovery, route, knowledge cards, evidence, mastery, open items, corrections, experiments, conflicts, reviews, milestones, and sessions. Moving detailed Q&A out does not reduce those functions.

The canonical templates are:

- `assets/PROJECT_STUDY_LOG.template.md`
- `assets/PROJECT_STUDY_QA.template.md`

## 2. Creation

When the user authorizes writing and records do not exist:

1. confirm the project root or writable location;
2. copy both templates unchanged;
3. initialize placeholders in a second minimal edit;
4. set repository revision, permissions, current scenario, Step, micro Step, and exact continuation node from evidence;
5. validate both files with `scripts/validate_learning_ledger.py`;
6. read back frontmatter and the current-state rows.

Never regenerate the schema from memory or overwrite an existing record with a fresh template.

If only one record exists, preserve it and create the missing companion only with authorization. Link the two paths in frontmatter.

## 3. Stable IDs

Use stable IDs and never recycle them:

- `RUN-`: runtime scenario/path
- `NODE-`: call-graph node
- `K-`: knowledge or demonstrated capability
- `SRC-`: source/evidence
- `Q-`: user question
- `FB-`: user feedback
- `NOTE-`: learner reflection
- `U-`: AI uncertainty
- `R-`: reproduction risk
- `M-`: misconception or wording correction
- `C-`: source/claim conflict
- `EXP-`: experiment or command
- `CMP-`: comparison or extension

Register details once and reference IDs elsewhere. Mark obsolete claims `stale`; do not silently rewrite history.

## 4. Context-selective reads

For ordinary continuation, read only:

- frontmatter and Section 1 hot state;
- the active route/micro-Step row and exact continuation node;
- due reviews and blocking open items;
- corrections that affect the current node;
- the latest session row;
- relevant unresolved/retest Q IDs and new/low-rated feedback from the Q&A file.

Do not reread all source history, all sessions, or all Q&A by default.

Read full records only for:

- schema migration or structural recovery;
- user-requested historical review;
- conflict resolution;
- global coverage audit;
- final-note generation.

## 5. Main-line anchor

Keep the top snapshot short enough to orient a new agent in about 60 seconds. It must contain:

- current scenario;
- current Step and micro Step;
- current node and exact continuation node;
- completed nodes on the representative path;
- active side-question IDs;
- blocking prerequisite or evidence gap;
- exactly one primary next action.

After every side question, update the side-question IDs and preserve the continuation node unless the route legitimately changes.

## 6. During-session capture

Capture state changes, not the transcript:

- a source was inspected;
- a runtime/call-path claim gained or lost evidence;
- a node or concept was introduced, traced, applied, or failed;
- a substantive question or follow-up was answered;
- wording or a prior conclusion was corrected;
- a route dependency, experiment, conflict, or risk changed;
- the learner changed goals or teaching preferences.

Detailed Q&A belongs in the Q&A file. The log keeps the Q ID, status, one-line summary, affected node, and whether it changes final notes.

## 7. Mastery and completion

Use observed behavior:

- `introduced`: exposed with evidence;
- `explainable`: learner explains the mechanism;
- `traceable`: learner reconstructs a caller/callee and data/shape boundary;
- `applied`: learner predicts, modifies, debugs, or designs an experiment;
- `verified`: later retrieval or runtime evidence succeeds;
- `revisit`: later evidence reveals forgetting or brittle transfer.

Exposure, agreement, copied wording, a `继续` message, or a Step label is not completion evidence.

## 8. Write transaction and receipt

After meaningful teaching or a substantive question, before the final response:

1. reread the target sections if another writer may have changed them;
2. patch only changed rows/sections;
3. update route, anchor, question/correction/evidence/mastery as applicable;
4. append one compact session row only when meaningful learning occurred;
5. set exactly one next action;
6. read back the changed IDs/rows and frontmatter;
7. report a concise receipt.

Example receipt:

```text
saved: LOG current=4.3/NODE-007, next=NODE-008; QA Q-014; correction M-003
```

If any required write or readback fails, say `unsaved` and preserve a compact delta in chat. Never imply success from an intended tool call.

## 9. Corrections and final wording

When a user question or new evidence corrects a claim:

- preserve the original wording in the correction record;
- write one canonical corrected formulation;
- link the evidence and affected Steps/knowledge cards;
- mark superseded wording `stale`;
- schedule a retest when the conceptual model changed.

Final notes use the canonical corrected wording. Run a stale-claim and terminology consistency audit before finalization.

## 10. Feedback-guided teaching

Treat user wording as authoritative input about the experience. Preserve it in the Q&A file. Reflect only a compact status and teaching adjustment in the log.

Prioritize:

1. blocking or `retest-due` feedback;
2. ratings below 3;
3. recurring complaints about pace, order, granularity, or missing answers;
4. positive signals that identify a useful explanation style.

## 11. Compaction and archiving

Compact in this order:

1. remove accidental duplicates while preserving canonical IDs;
2. keep only compact Q indexes in the main log;
3. synthesize old session rows into milestones;
4. move old closed session history to an archive only with authorization;
5. preserve unresolved questions, corrections, risks, dependencies, and their evidence.

Never archive an item merely by age if it still explains an active conclusion.

## 12. Legacy schema 3.1

Existing schema 3.1 logs remain readable and valid. Do not overwrite them.

For authorized migration:

1. preserve a backup or archive;
2. create new schema 4.0 files from the canonical templates;
3. migrate confirmed current state, evidence, mastery, corrections, experiments, reviews, milestones, and sessions;
4. move detailed user questions/feedback/reflections to the Q&A file while keeping compact IDs in the log;
5. mark reconstructed fields;
6. validate both new files before replacing active paths.

If migration is not authorized, continue with the legacy log and keep Q&A unsaved or in an authorized companion file without pretending the schema was upgraded.

## 13. Quality check

Before closing an update, verify:

- a new agent can resume in about 60 seconds;
- the route reflects actual runtime scenarios rather than a hard-coded architecture;
- current and next nodes are unambiguous;
- every promoted mastery level has behavior evidence;
- substantive questions and corrections have durable IDs;
- new/low-rated feedback changed teaching or has a scheduled action;
- final-note material contains no known stale wording;
- no full transcript, secrets, or irrelevant personal details were stored.
