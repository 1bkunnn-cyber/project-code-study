# PROJECT_STUDY_LOG.md Template

This is a working learning ledger, not a transcript and not the final study note. Keep the top useful for a 60-second restart. Update state tables in place; append only the session log.

# <Project Name> Learning Ledger

## 0. Record Control

- Ledger path:
- User authorized writing: yes / no / chat-only
- Created:
- Last meaningful update:
- Maintainer: AI with user review
- Project root / repository:
- Repository revision: `<branch>@<commit>` or `unknown`
- Ledger schema version: 2

## 1. Current Snapshot

Read this section first at every session. Keep it short and current.

- Study mode: new / resume / review / advance / blocked / finalize
- Target outcome: read / reproduce / modify / research-extend
- Current step:
- Current session budget: quick / standard / deep / `<minutes>`
- Last session:
- Days since last session:
- Primary next action: exactly one action
- Why this action has highest value:
- Current blocker:
- Review due now:
- Biggest learning risk:
- AI's least certain important claim:
- User's current concern in their own words:

### Restart Brief

Write no more than 8 bullets:

- What the project does:
- Where execution begins:
- What the learner can currently explain:
- What the learner can currently trace in code:
- What remains fuzzy or incorrect:
- What evidence is still missing:
- What changed since the previous session:
- What to do next:

## 2. Learning Contract

- Learner background:
- Prerequisites already mastered:
- Motivation:
- Deliverable that proves success:
- Available time per session / total period:
- Preferred explanation style:
- Runtime experiments authorized: yes / no / ask first
- Network or paper retrieval authorized: yes / no / ask first
- Project code modification authorized: yes / no / ask first
- Out of scope:

Update this only when the user changes goals, constraints, or available time.

## 3. Route and Step State

Do not use completion percentage as a proxy for understanding.

| Step | Topic | Status | Exit evidence required | Actual evidence | Next decision |
| --- | --- | --- | --- | --- | --- |
| 0 | Project map | planned | Can locate entrypoints and describe main flow |  |  |
| 1 | Task and paper problem | planned | Can explain problem, motivation, and paper claim |  |  |
| 2 | Data and preprocessing | planned | Can trace one sample into a batch with shapes |  |  |
| 3 | Architecture | planned | Can reconstruct module graph and major interfaces |  |  |
| 4 | Core source reading | planned | Can explain and trace selected core modules |  |  |
| 5 | Paper-code mapping | planned | Can name verified matches and deviations |  |  |
| 6 | Loss/postprocess/metrics | planned | Can connect formulas, tensors, code, and metrics |  |  |
| 7 | Training/config | planned | Can trace one training iteration and config resolution |  |  |
| 8 | Inference/reproduction | planned | Can run or specify a verified inference/reproduction path |  |  |
| 9 | Context audit | planned | Important blind spots and uncertainties are prioritized |  |  |
| 10 | Graduate synthesis | planned | Can critique, modify, and propose an evidence-backed experiment |  |  |

Allowed status: `planned`, `active`, `review`, `blocked`, `done`, `skipped`, `stale`.

### Route Changes

| Date | Change | Reason | User confirmed | Impact |
| --- | --- | --- | --- | --- |
|  |  |  | yes / no |  |

## 4. Mastery Map

Track demonstrated performance, not just content exposure.

| ID | Concept or skill | Importance | Demonstrated level | Evidence of learning | Self-confidence (1-5) | Last tested | Next review |
| --- | --- | --- | --- | --- | --- | --- | --- |
| K-001 |  | core / supporting | unseen / introduced / explainable / traceable / applied / verified / revisit | teach-back, trace, prediction, code change, experiment |  |  |  |

Interpretation:

- `introduced`: learner has seen the explanation.
- `explainable`: learner can explain it unaided.
- `traceable`: learner can locate and follow it through code or shapes.
- `applied`: learner can use it in a modification, debugging task, or experiment.
- `verified`: performance has held across a later review or real run.
- `revisit`: a misconception, forgotten dependency, or weak transfer was observed.

## 5. Source and Evidence Register

Register a source once, then refer to its ID elsewhere.

| ID | Type | Locator | Revision / page | What was actually inspected | Supports | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SRC-001 | code / config / paper / docs / runtime / user | `<path:symbol>` or paper section |  |  | K-001 / Q-001 / U-001 | confirmed / partial / stale / missing |

Rules:

- README claims are documentation evidence, not runtime verification.
- Search snippets are discovery aids, not substitutes for the original source.
- When the repository revision changes, mark affected sources and conclusions `stale` until rechecked.

## 6. Open Loops

Every unresolved item needs a concrete next action. Close or defer items explicitly.

| ID | Type | Statement | Blocking | Evidence needed | Next action | Target step | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q-001 | user question |  | yes / no |  |  |  | open / answered / deferred / stale |
| U-001 | AI uncertainty |  | yes / no |  |  |  | open / resolved / accepted-risk / stale |
| R-001 | reproduction risk |  | yes / no |  |  |  | open / mitigated / accepted-risk |

Do not keep a large generic TODO list. The current snapshot should name only the highest-value next action.

## 7. Misconceptions and Corrections

Do not erase a wrong understanding after explaining it. Retest it later.

| ID | Observed misunderstanding | How it was detected | Correct model | Evidence | Retest prompt | Status |
| --- | --- | --- | --- | --- | --- | --- |
| M-001 |  | teach-back / shape trace / prediction / code task |  | SRC-... |  | observed / corrected / retest-due / resolved |

## 8. User Questions Worth Preserving

Keep the user's real intent, but summarize instead of copying the conversation.

| ID | Step | Question | Short answer | Evidence IDs | Changed prior understanding | Final-note tag |
| --- | --- | --- | --- | --- | --- | --- |
| Q-001 |  |  |  | SRC-... | yes / no | include / omit |

## 9. Experiments, Commands, and Failed Attempts

Record commands only when they teach, verify, reproduce, or prevent repeated failure.

| ID | Date | Hypothesis / purpose | Command or change | Result | Evidence artifact | Interpretation | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EXP-001 |  |  |  | not-run / pass / fail / partial | log / metric / output / diff |  |  |

Never rewrite a failed attempt as if it worked. Record environment and configuration when they affect interpretation.

## 10. Paper-Code and Source Conflicts

| ID | Claim | Source A | Source B | Current assessment | Confidence | Verification action | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C-001 |  | SRC-... | SRC-... |  | high / medium / low |  | open / resolved / accepted-ambiguity |

## 11. Review Queue

| Due | Knowledge ID | Why review is due | Review form | Result | Reschedule |
| --- | --- | --- | --- | --- | --- |
|  | K-... | new / wrong / hinted / unaided / applied | explain / trace / predict / debug / modify | pending / weak / adequate / strong |  |

## 12. Maintenance State

- Last duplicate/stale-entry review:
- Closed items still referenced elsewhere:
- Archive recommended: yes / no
- Archive authorized by user: yes / no
- Archive path, if created: `PROJECT_STUDY_LOG_ARCHIVE.md`
- Material ready for final summary:
- Material explicitly excluded from final summary:

## 13. Milestone Syntheses

Create a compact synthesis after a meaningful milestone, not after every answer. These are the main inputs to the final Markdown note.

### Milestone <name / steps>

- Durable understanding:
- Key source IDs:
- Call and shape path learned:
- Paper-code relationship:
- What changed in the learner's mental model:
- Remaining open-loop IDs:
- Reusable final-note material:

## 14. Session Log

Keep this as the final section of the file. Append exactly one entry after each meaningful learning session. Partial or interrupted sessions still get an honest entry.

### Session <N> — <YYYY-MM-DD>

- Mode and duration: quick / standard / deep, `<minutes>`
- Repository revision checked:
- User's intended focus:
- Review performed before new material:
- Sources inspected: SRC-...
- Work completed:
- Learner evidence: what they explained, traced, predicted, applied, or failed to recall
- Misconceptions observed or retested: M-...
- Questions added or answered: Q-...
- Experiments attempted: EXP-...
- State changes: step status and mastery changes
- Outcome: advanced / reviewed / blocked / interrupted / finalized
- Primary next action:
- Suggested return timing:
