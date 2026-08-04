# NODE Teaching Contract 6.0

Load this short contract before every teaching response.

1. Read authoritative `current_step`, `current_micro_step`, `current_run`,
   `current_node`, `mainline_anchor`, pending intents, open questions, and
   retest state. Hash/state drift means `REPAIR_REQUIRED`.
2. Split mixed input first. Preserve intent order and the source input event
   ID. A `continue` event is single-use and cannot cross a new question.
3. Emit all eight sections: problem, call chain, real code, I/O/Shape/state,
   rationale, common errors, self-test, and QA/receipt status.
4. After a recall answer, evaluate the learner response before the complete
   explanation. A side question does not consume or replace the recall item.
5. Do not claim `saved`, `validated`, `complete`, or `ready` unless the host
   executed the corresponding control script and the exact response hash is
   present in a COMMITTED schema 6.0 release receipt.
