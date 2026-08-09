# Question, Feedback, and Correction Protocol

Use this protocol when the learner asks a substantive question, answers active recall, corrects a claim, or reports a teaching problem.

## 1. Allocate a stable Q ID

Create a new Q entry for every first question, follow-up asking for a different reason/example/implication/path, new question in the same Step, syntax question that affects the current NODE, active-recall response, or question that revises an earlier claim. Do not create Q entries for operational acknowledgements such as `继续`, `好的`, or `明白` unless they change constraints.

Never reuse an ID. Set `parent_id` for follow-ups. Preserve the current scenario, Step/NODE, interaction state, and exact continuation NODE before answering. Bind every Q to its schema 6.2 input event, intent ID/order, exact source span/hash, and `answer_status`.

## 2. Standalone Q&A record

Every Q detail must contain:

- user's question intent;
- parent Q or `none`;
- current main-line anchor and return position;
- complete canonical answer, including the reasoning needed to reuse it;
- code/paper/runtime/background evidence and evidence status;
- whether it changes an old conclusion;
- linked M/C/SRC/K IDs;
- minimum verification action;
- Q status and transaction receipt.

Forbidden answer substitutions: `详见 chat`, `同上`, `前文已解释`, `见之前回答`, circular `详见对应 UNIT`, or a summary that omits the key derivation. One Q entry must be understandable without chat history.

## 3. Persistence order

For one input containing N questions, persistence has two stages.

Intake stage, before any answer:

1. validate the input envelope and capture the exact return state;
2. allocate all N Q IDs in source order;
3. write every QA detail/index and LOG index as `answer_status: pending`;
4. record input/intent identity, Parent Q, anchor, and ordered queue;
5. strictly validate and emit one `question-intake` receipt.

Answer stage, once per existing Q:

1. allocate one new TX ID but retain the existing Q ID;
2. replace that Q's pending answer with the standalone answer and update its indexes;
3. read back Q ID, parent, complete answer, status, anchor, evidence links, and TX ID;
4. write the LOG Q index, authoritative state, correction/K-card changes, and same TX ID;
5. read back LOG current/next/state and affected rows;
6. run strict cross-file validation;
7. return `saved` only after all checks pass.

Do not defer questions until the end of a Step. Partial success is `unsaved-partial`, never `saved`. A failed answer transaction changes no file; earlier answered Qs remain committed and later Qs remain pending.

## 4. Active-recall closure

After the learner answers, always provide:

1. verdict: `正确`, `部分正确`, `错误`, or `证据不足`;
2. correct parts to preserve;
3. repair for missing, ambiguous, or wrong parts;
4. a standalone complete reference answer even when fully correct;
5. source/paper/runtime evidence or an explicit project-specific gap;
6. impact on mastery, prior conclusions, route, and review schedule;
7. Q/M/C/K IDs and honest transaction receipt.

Then set `interaction_state: AWAITING_QUESTIONS_OR_CONTINUE`, preserve the continuation NODE, and stop. The response must not teach the next micro Step.

If a learner asks a side question while `interaction_state: AWAITING_RECALL`, do not discard the pending recall. Allocate the side question, set `ANSWERING_RECALL_SIDE_QUESTION`, persist the answer, and return to `AWAITING_RECALL`. The recall response remains pending until the learner answers it. If a message contains a recall answer plus another intent, place the additional intent in `pending_user_intents`; consume intents in order and block `continue` until the queue is empty.

## 5. One-use continuation rule

A continue instruction is valid only when received after entering `AWAITING_QUESTIONS_OR_CONTINUE`. Consume it on transition to `TEACHING_CURRENT_NODE`. If a side question or recall answer intervenes, any earlier continue is expired. Answer completion restores the anchor and waits for a new user message.

## 6. Canonical correction chain

Preserve:

```text
Correction ID: M-xxx or C-xxx
Original wording:
Why imprecise or wrong:
Canonical wording:
Evidence and status:
Affected Steps / K / Q:
Stale pattern:
Retest question:
Status:
Transaction ID:
```

Mark superseded promoted wording stale. Update hot summaries and affected K cards in the same transaction. Finalization must scan summary, units, important questions, and conclusions for stale patterns; the historical correction section may quote the old wording only when clearly marked historical.

## 7. Multiple questions and feedback

When multiple substantive questions arrive, there is no protocol N limit. Register every intent before answering, answer in source order with one receipt per Q, and preserve the captured return state unless evidence legitimately changes the route through a correction transaction. Chat may show at most three answers per response, but display paging never removes a queue member. A follow-up receives a new Q and correct Parent Q. Teaching feedback receives an `FB-` ID and records concrete adjustment without advancing. A mixed message that includes `继续`, a recall response, a question, a correction, or a mode change must be represented as an explicit pending-intent queue; never silently drop an intent. A question/correction makes same-event `继续` expired rather than delayed.

## 8. Read strategy

Ordinary continuation reads only unresolved/retest questions for the current NODE, recent follow-ups for the active parent, low-rated/new feedback, and relevant corrections. Read the full Q&A only for migration, conflict recovery, global audit, requested review, or finalization.
