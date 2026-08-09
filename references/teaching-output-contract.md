# Teaching Output Contract

## Mode-aware short contract before every response

Load `assets/NODE_TEACHING_CONTRACT.md`, reconcile Step, micro-Step, RUN, NODE,
main-line anchor, question queue, pending intents, retest, and handoff hashes,
then select a response profile and validate the draft with
`scripts/validate_teaching_response.py`. All profiles include the authoritative
location strip and honest QA/receipt closure. Only `node-teaching` uses the full
problem/call/code/I-O/rationale/error/self-test body; ASK, ASSESS, recovery,
repair, start, and close have smaller mode-specific contracts.

Select `content_kind` independently from response profile. Tensor explanations
need a concrete Shape flow; code needs a fenced verified excerpt; metric needs
the equation, threshold, and project field; config/state explains real fields
and transitions without inventing numeric Shape.

A recall answer starts with evaluation and then gives the complete explanation.
A side question preserves the original recall prompt. Long context never permits
summary-only output. State drift enters `REPAIR_REQUIRED`.

Use semantic fields rather than response length as the quality gate.

## Source NODE contract

Every source NODE names the current `RUN`/`NODE`, caller, callee, upstream/downstream, problem, verified clickable source location, and the smallest source excerpt needed for the explanation. Explain code groups in execution order. Track input, output, Shape, state, and each dimension's meaning, origin, transformation, and downstream consumer. Explain design reason, alternatives, trade-offs, failure modes, evidence level, and the unverified boundary. End with a self-check and complete reference answer.

Reject a node made only of a copied code block, line-by-line paraphrase, architecture nouns, a bare shape list, or a path containing `...` or an unverified line number.

## Active recall contract

Record the learner's answer as understood. Map each intent to the learner span and evidence. State correct, missing, ambiguous, and conflicting parts separately. Do not invent an error from a short answer. Provide the full canonical answer, why it is correct, evidence, a changed-angle explanation, and a retest for partial or wrong answers. Persist the closure before returning to `AWAITING_QUESTIONS_OR_CONTINUE`.

## Chat and QA contract

QA stores the complete standalone canonical answer, evidence, parent Q, anchor, verdict, correction links, retest, and transaction. Chat gives a concise closure: conclusion, key reason, evidence summary, Q-ID, clickable QA location, current anchor, and the waiting/blocked state. “See QA” alone is not a response contract.

## Compound questions

Build a source-bound input envelope, register every independent question in one
intake transaction, and only then begin teaching answers. Update one existing
Q-ID per answer transaction. Display in batches when necessary, but never
truncate the queue. A failure preserves earlier commits and later pending Qs;
no main-line advance occurs while any member is pending, open, or `retest-due`.

## Visual and formula contract

Use a short linear chain for a short call path, tables for Shape/field mappings, and Mermaid for multi-layer calls, data flow, and state machines. Keep `RUN`/`NODE` labels and editable source. Use a plain-text equivalent when rendering is unknown. Express formula-to-code mappings as a variable table or numbered equations; do not depend on whitespace alignment.

## Independent UNIT contract

Each completed Step/micro-Step maps to exactly one or more complete UNITs. A UNIT is independently relearnable and contains objective, runtime position, source order, I/O/Shape/formula/config/state, rationale/trade-offs/failures, important questions and canonical corrections, evidence boundary, self-check/full answer, and next connection. Short administrative summaries cannot satisfy the contract.
