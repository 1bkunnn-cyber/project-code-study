# Learning Record Protocol

Use this protocol whenever creating, reading, updating, validating, compacting, or migrating project-code-study records.

## 1. Record architecture and authority

Schema 4.1 uses two linked files:

- `PROJECT_STUDY_LOG.md`: authoritative working state, route, evidence, mastery, durable knowledge, corrections, experiments, reviews, transactions, milestones, and sessions.
- `PROJECT_STUDY_QA.md`: authoritative full questions, follow-ups, standalone answers, learner reflections, and feedback.

Templates:

- `assets/PROJECT_STUDY_LOG.template.md`
- `assets/PROJECT_STUDY_QA.template.md`

The authoritative state fields are `current_scenario`, `current_step`, `current_micro_step`, `current_node_id`, `continuation_node_id`, `interaction_state`, `pending_user_response`, `active_side_question_ids`, `pending_user_intents`, `last_question_id`, `last_transaction_id`, and `updated_at`. Frontmatter and Section 1 must match exactly. Route tables, indexes, review queues, knowledge cards, and session rows are derived views; update them in the same transaction.

## 2. Creation

When writing is authorized and records do not exist:

1. confirm the project root;
2. instantiate both canonical templates;
3. initialize placeholders in a second minimal edit;
4. set revision, permissions, authoritative state, and exact continuation NODE from evidence;
5. allocate `TX-0001` for creation;
6. validate both with `scripts/validate_learning_ledger.py --strict` and their peer paths;
7. read back frontmatter, hot state, and transaction rows.

Never regenerate a schema from memory or overwrite an existing record with a template. If only one file exists, preserve it and create the companion only with authorization.

## 3. Stable IDs

Never recycle IDs:

- `RUN-`: runtime scenario/path
- `NODE-`: call-graph node
- `K-`: durable knowledge or demonstrated capability
- `SRC-`: source/evidence
- `Q-`: substantive question or active-recall response
- `FB-`: teaching feedback
- `NOTE-`: learner reflection
- `U-`: uncertainty
- `R-`: reproduction risk
- `M-`: misconception/wording correction
- `C-`: source/claim conflict
- `EXP-`: experiment or command
- `CMP-`: comparison/extension
- `TX-`: cross-file write transaction

Register details once and reference IDs elsewhere. Preserve superseded claims as history and mark their promoted use `stale`.

## 4. Enumerated states

Use only these values:

- Step/micro Step: `planned`, `active`, `blocked-prerequisite`, `review`, `done`, `skipped`, `stale`.
- NODE: `discovered`, `planned`, `active`, `traced`, `verified`, `blocked-prerequisite`, `deferred`, `skipped`, `stale`.
- question: `open`, `answered`, `retest-due`, `closed`, `deferred`, `stale`.
- interaction: states defined in `SKILL.md`.

Each object has exactly one current state. A range summary is allowed only when every member row exists with an individual state. `deferred` and `skipped` NODE rows require reason, impact, revisit condition, and learner acceptance. Count Steps, micro Steps, and NODEs separately.

## 5. Context-selective reads

For ordinary continuation, read only authoritative state, the active route/NODE, exact continuation, due reviews, blockers, affected corrections, latest transaction/session, and relevant Q/feedback IDs. Read the full bundle only for migration, global audit, conflict recovery, or finalization.

## 6. Main-line anchor and interaction state

Keep the hot snapshot readable in about 60 seconds. It must show current scenario, Step/micro Step, NODE, completed representative nodes, active side questions, blocker, exact continuation NODE, interaction state, pending response, and exactly one primary next action.

Side questions and recall closure preserve `continuation_node_id`. A side question that interrupts `AWAITING_RECALL` returns to `AWAITING_RECALL` after its answer is saved; a side question in `FINAL_QUESTION_PHASE` returns to `FINAL_QUESTION_PHASE`. After ordinary side-question or recall closure, set `interaction_state: AWAITING_QUESTIONS_OR_CONTINUE` and `pending_user_response: true`. Only a fresh continue event may enter `TEACHING_CURRENT_NODE`; consume it once. A `FINAL_AUDIT` failure enters `FINAL_AUDIT_REPAIR` and cannot be converted into ordinary waiting. Any unresolved user-intent queue blocks advancement.

## 7. Mastery and durable knowledge

Use behavior evidence:

- `introduced`: exposed with evidence
- `explainable`: learner explains mechanism
- `traceable`: learner reconstructs a call/data boundary
- `applied`: learner predicts, modifies, debugs, or designs an experiment
- `verified`: later retrieval/runtime evidence succeeds
- `revisit`: later evidence shows brittle transfer

A `done` Step requires a detailed `K-` card, behavior evidence, successful transaction, and these non-placeholder fields:

`prerequisites`, `learning_objective`, `runtime_position`, `complete_explanation`, `source_locations`, `inputs_outputs_shapes`, `rationale_tradeoffs`, `important_questions`, `canonical_corrections`, `evidence_status`, `self_check`, `reference_answer`, `next_connection`.

Exposure, agreement, copied wording, a continue message, or a status label is not completion evidence.

## 8. Atomic logical transaction

Markdown hosts cannot guarantee a filesystem-wide atomic rename, so use a fail-closed logical transaction with one monotonic `TX-` ID:

```text
construct delta and TX ID
  -> write Q&A detail/index/correction references
  -> exact Q&A readback
  -> write ledger state/index/knowledge/session/transaction
  -> exact ledger readback
  -> cross-file ID and state reconciliation
  -> strict validation
  -> saved only if all pass
```

Required readback checks:

- Q ID, parent, complete answer, status, main-line anchor, linked M/C/SRC/K, and TX ID;
- current/continuation NODE, interaction state, pending response, last Q/TX IDs, and updated time;
- LOG and Q&A maximum Q ID and transaction ID agree;
- relevant `retest-due`, M/C, and review-queue views agree.

If the Q&A write succeeds but the ledger write/readback fails, return `unsaved-partial`, list exact written/missing pieces, retain the compact delta, and set the next action to repair—not teaching. Never issue `saved` from an intended or dispatched tool call.

A success receipt contains files, TX/Q/M/C IDs, current, next, interaction state, and strict validation result.

## 9. Questions, corrections, and final wording

Detailed Q&A belongs in Q&A; the log keeps a compact index. When evidence corrects a claim, preserve original wording, canonical wording, evidence, impact, stale pattern, and retest. Update every current summary and affected K card in the same transaction. Finalization scans promoted sections for stale patterns.

Separate suggested commands, executed commands, and observed results. Never promote `not-run` to runtime evidence or claim complete paper/code agreement without direct inspection.

## 10. Feedback and compaction

Preserve learner wording in Q&A and only a compact status/adjustment in the log. Prioritize blocking/retest feedback, ratings below 3, and recurring pace/order/granularity issues.

Compact by removing accidental duplicates, keeping only Q indexes in the log, synthesizing old sessions into milestones, and archiving only with authorization. Never archive an item still supporting an active conclusion.

## 11. Compatibility and migration

Schema 4.0 and legacy 3.1 remain readable. Strict cross-file guarantees apply to 4.1. Migrate only with authorization:

1. preserve a backup;
2. instantiate 4.1 templates;
3. migrate confirmed state, route, evidence, mastery, knowledge, corrections, experiments, reviews, and sessions;
4. migrate full Q&A while retaining compact indexes;
5. mark reconstructed fields;
6. run strict validation before replacing active paths.

## 12. Quality check

Before closing a transaction, verify that a new agent can resume in about 60 seconds, route and state views agree, every promoted mastery has behavior evidence, questions/corrections have durable IDs and complete content, stale wording is absent from current conclusions, exactly one next action exists, and no transcript, secrets, or irrelevant personal data were stored.
