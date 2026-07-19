# Study Quality Rubric

Apply these gates without reciting the checklist in every response.

## Evidence levels

| Level | Meaning | Permitted wording |
| --- | --- | --- |
| E0 | no project evidence | `当前材料中未看到证据` |
| E1 | direct source/document observation | `已确认` with path/symbol/page |
| E2 | cross-source inference | `可推断` plus missing verification |
| E3 | runtime/experiment verification | `已验证` with command/log/output |

Background knowledge is separate from E0–E3. Suggested commands, executed commands, and observed results are distinct records.

## Route gate

Before deep teaching, the relevant source inventory is indexed; representative RUN scenarios are chosen; Step 3 records caller/callee nodes and dependencies; Step 4.x comes from the graph; and shared/training/inference/evaluation nodes are distinguishable. Every NODE uses one allowed state. Deferred/skipped nodes include reason, impact, revisit condition, and acceptance.

## Micro-Step semantic completion gate

A micro Step is `done` only when all are true:

1. one primary NODE was taught in its actual scenario;
2. caller, symbol, callee, source location, execution order, inputs/outputs, Shape/state, design reason, and relevant risk are explained;
3. blocking prerequisites are resolved or the Step remains blocked;
4. important Q/M/C records contain standalone canonical content;
5. the learner passes a recall/trace/predict task and receives the complete reference answer;
6. a non-placeholder durable K card contains every field from `step-template.md`;
7. the transaction writes and exactly reads back both records;
8. strict validation passes;
9. the workflow pauses and waits for a fresh continue before leaving.

Exposure, a long explanation, agreement, continue, or a status label never substitutes for these gates.

## Step gate

A Step is complete only when required micro Steps are done or explicitly skipped with accepted impact, the central mechanism has behavior evidence, a key call/data boundary is reconstructable, unresolved dependencies have actions, every done item has durable knowledge, and the final transaction validates.

## Q&A and interaction gate

Active recall closure is:

`verdict -> correct parts -> repair -> complete answer -> evidence -> impact -> save receipt -> pause`.

Every substantive question has a unique Q ID and complete answer. Side questions and recall do not move the continuation NODE. An earlier continue cannot survive a question. The answer response contains no next-NODE teaching.

## Correction promotion gate

Every M/C record contains original wording, canonical wording, evidence/status, impact, stale pattern, retest, and transaction. Scan hot summaries, K cards, final summaries, relearning units, important questions, and conclusions for stale patterns. Historical correction tables may quote old wording only as explicitly historical.

High-impact claims require evidence labels. Do not write `全部匹配`, `全部确认`, or equivalent when the linked paper/source was not fully inspected.

## Document-ready gate

Run `scripts/validate_finalization_bundle.py`. Formal finalization requires:

- all required Steps final and every done Step backed by a durable K card;
- required scenario/NODE/dependency coverage complete;
- no open/retest question or pending learner response;
- Q&A contains no hidden-chat dependency;
- correction/stale audit passes;
- learner explicitly closed questions and consented.

Any blocker yields a readiness report. Only an explicitly requested early artifact may use `status: incomplete-draft`; it must list all blockers.

## Cold-start relearning gate

For each final UNIT, a reader with no chat must be able to state its objective/runtime position, reconstruct the main sequence, explain input/output/Shape/state, answer important Qs, give canonical corrections, solve the self-check, and identify the next NODE plus unverified boundary. Static validation is a minimum proxy; release evidence should record any real cross-model cold-start run separately.

## Context discipline

Normal continuation reads authoritative hot state and relevant IDs, not full history. Teach one primary NODE unless the user explicitly requests synthesis.
