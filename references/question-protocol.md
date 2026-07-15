# Question, Feedback, and Correction Protocol

Use this protocol whenever the learner asks a substantive question, answers an active-recall prompt, corrects the agent, or reports a teaching problem.

## 1. What must be recorded

Create a new `Q-` entry for:

- the first question on a topic;
- a follow-up that asks for a different reason, example, implication, or code path;
- a new question during the same Step;
- a syntax question that affects reading the current node;
- a question that reveals or corrects an imprecise prior claim.

Do not create Q entries for operational acknowledgements such as `继续`, `好的`, or `明白` unless they also change the route or constraints.

Never reuse or overwrite a Q ID. Use `parent_id` for follow-ups.

## 2. Persistence transaction

After answering a substantive question in the same turn:

1. append or update the full Q&A entry in `PROJECT_STUDY_QA.md`;
2. update the compact question index or open item in `PROJECT_STUDY_LOG.md`;
3. update the main-line continuation anchor;
4. if the answer changes a prior claim, create/update an `M-` or `C-` record and the affected Step knowledge card;
5. read back the Q ID and affected rows;
6. report `saved: Q-xxx` or explicitly report `unsaved` with the reason.

Do not wait until the end of a large Step to save questions.

## 3. Active-recall answer contract

After the learner answers, always provide all of the following:

1. **Verdict**: `正确`, `部分正确`, `错误`, or `证据不足`.
2. **Correct parts**: what should be preserved.
3. **Repair**: what is missing, ambiguous, or wrong.
4. **Complete reference answer**: a standalone answer suitable for later review, even when the learner was fully correct.
5. **Evidence**: source/paper/runtime evidence or an explicit project-specific evidence gap.
6. **Impact**: whether the answer changes mastery, a prior conclusion, the route, or a review schedule.
7. **Persistence**: Q/M/C IDs and save receipt.

Never reply only with “基本正确，我来精确化” or a verdict without the complete answer.

## 4. Canonical correction chain

When a statement is corrected, preserve a compact chain:

```text
Correction ID: M-xxx or C-xxx
Original wording:
Why it was imprecise or wrong:
Canonical corrected wording:
Evidence:
Affected Steps / notes:
Retest question:
Status:
```

Mark superseded wording `stale`. Update current summaries and final-note material to use the canonical wording. Do not erase the history that explains why the correction occurred.

## 5. Side questions and the main line

Answer side questions fully, but keep them subordinate to the main route. End with:

- how the question relates to the current node;
- the current main-line anchor;
- the exact continuation node.

When multiple questions arrive together, assign IDs to each, answer them in a bounded sequence, and preserve the same continuation anchor unless a question legitimately changes the route.

## 6. Read strategy

On ordinary continuation, read only:

- unresolved or `retest-due` questions relevant to the current node;
- recent follow-ups for the active parent Q;
- low-rated or new feedback;
- corrections affecting the current explanation.

Read the full Q&A file only for migration, conflict recovery, a user-requested question review, global audit, or finalization.
