# Interaction Mode Protocol 6.2

This protocol connects natural learner input to the Skill state machine. The learner chooses words; the Skill chooses a mode and proves every state change.

## 1. Standard loop

Every ordinary learning turn follows:

```text
定位 → 学习 → 检验 → 沉淀 → 等待
```

The loop does not mean every response has the same headings. It means every response is located in authoritative state, performs one bounded action, checks its result, persists the appropriate durable record, and ends at a declared waiting/repair state.

## 2. Modes and response profiles

| Learner situation | Mode | Response profile | Required outcome |
| --- | --- | --- | --- |
| New project or new goal | `START` | `start` | evidence boundary, route start, one next action |
| Current runtime node | `LEARN` | `node-teaching` | one source-grounded NODE plus self-check |
| One or more questions | `ASK` | `question-answer` | full intake first, then per-Q answer transactions |
| Recall/retest response | `ASSESS` | `recall-assessment` | evaluate first, explain fully, retain/retest |
| Resume after pause/compaction | `RECOVER` | `recovery` | hash-checked handoff restoration |
| End of a safe learning unit | `CLOSE` | `close` | durable result, evidence boundary, wait |
| State, hash, or receipt conflict | `REPAIR` | `repair` | no teaching; one repair action |

All profiles display current Step, micro-Step, RUN, NODE, main-line anchor, and QA/receipt status. `scripts/validate_teaching_response.py` enforces profile-specific sections and content-specific evidence.

## 3. Input event envelope

`scripts/study_events.py` creates a schema `6.2` envelope. It binds the raw text hash and received state to ordered intents. Every intent contains its input/intent IDs, exact source span/hash, kind, target, parent, optional Q-ID, and status.

The deterministic splitter handles explicit numbering, bullets, line/semicolon separation, and multiple question sentences. A model may propose a semantic split for ambiguous prose only when the validator proves that all spans are exact, ordered, non-overlapping, and hash-bound. A complex question with one question boundary remains one intent; arbitrary hidden semantic splitting is forbidden.

Any substantive question or correction in an input event expires a `continue` intent from that same event. An expired continue can never be replayed after the question queue closes.

## 4. Arbitrary-size question batch

There is no protocol maximum N. Display may be paged, but persistence may not truncate the queue.

Stage A — intake transaction:

1. capture the exact return state and main-line anchor;
2. validate the input envelope;
3. allocate every Q-ID in source order;
4. write every QA detail and QA/LOG index row as `answer_status: pending`;
5. record input event, intent ID/order, Parent Q, anchor, and queue;
6. strictly validate and emit one `question-intake` receipt.

No answer may be emitted before Stage A succeeds for all questions.

Stage B — answer transactions:

1. select the next Q in registered order;
2. produce its type-specific complete answer and evidence;
3. update the existing Q-ID to `answered`;
4. update LOG queue state and issue one `question-answer` TX/receipt;
5. proceed to the next Q only after validation.

If question N fails, questions before N remain answered; N enters `QUESTION_BATCH_REPAIR`; later questions remain pending. Repair returns to the same Q. When the queue is empty, restore the exact captured return state. A follow-up always gets a new Q-ID and a Parent Q link.

## 5. Recall, correction, and continuation precedence

Recall answers are evaluated before the canonical explanation. A side question never consumes the active recall item. Corrections are evidence-checked and propagated before ordinary questions when they invalidate an answer premise. Advancement is forbidden while pending intents, pending Q answers, retest, corrections, state drift, or unverified receipts exist.

## 6. Handoff and recovery

Before compaction, serialize current Step/RUN/NODE/anchor, completed nodes, active input event, ordered question queue/current Q/return state, open questions, pending intents, retest, recent corrections, evidence, memory candidates, artifact hashes, and exactly one next action. Restore only if hashes match. Otherwise enter `REPAIR_REQUIRED`.

## 7. Claim boundary

The protocol is advisory unless the host executes transaction and pre-response controls. Without those controls, responses must not claim `saved`, `validated`, `complete`, or formal publication. Static tests never prove a Claude/Codex hook, real compaction, or multi-model cold start.
