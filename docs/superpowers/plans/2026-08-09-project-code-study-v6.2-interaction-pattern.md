# Project Code Study v6.2 Interaction Pattern — Implementation Plan

> **Execution rule:** implement this plan locally with test-driven development. For every behavioral change, add or change the focused test first, observe the intended failure, implement the smallest mechanism, then rerun the focused and related suites.

**Goal:** Turn the v6.2 design into one repeatable natural-language interaction pattern in which an arbitrary-size user question batch is registered completely before teaching, each question is answered and persisted independently, and the exact learning anchor is recoverable after interruption or compaction.

**Constraints:** Preserve fail-closed validation, source evidence boundaries, retest/continue gates, existing IDs, transactional writes, and v6.1 compact handbook behavior. Do not modify the audited learner project or its study artifacts. Host-only claims remain `not-run` unless a real host action executes them.

## Task 1 — Intent envelope and deterministic routing

**Files:**

- Modify: `scripts/study_events.py`
- Create: `tests/test_interaction_modes_v62.py`

1. Add failing tests for zero questions, a complex single question, unnumbered multiple questions, numbered 20-question input, mixed correction/question/continue input, stable source spans, hashes, and order.
2. Run `python -m unittest tests.test_interaction_modes_v62 -v` and record the expected failures.
3. Add schema `6.2` input envelopes with `INPUT-*`, raw-text hash, ordered `INTENT-*` records, source spans/hashes, kind, target, parent, Q binding, and status.
4. Preserve `split_intents()` compatibility. Allow a caller-proposed semantic split only when every span is exact, non-overlapping, ordered, and hash-valid.
5. Expire a `continue` intent whenever the same input event contains a substantive question or correction.
6. Rerun the focused test and existing event/handoff tests.

## Task 2 — Batch question intake and per-question answer transactions

**Files:**

- Modify: `scripts/project_study_transaction.py`
- Modify: `scripts/validate_learning_ledger.py`
- Modify: `assets/PROJECT_STUDY_QA.template.md`
- Modify: `assets/PROJECT_STUDY_LOG.template.md`
- Create: `tests/test_question_batch_v62.py`
- Modify: `tests/test_regressions.py`
- Modify: `tests/test_adversarial_regressions.py`

1. Add failing tests proving that 1, 3, and 20 questions are all registered before the first answer, Q IDs preserve source order, and the LOG/QA records share input and intent identities.
2. Add failing tests proving that answers update the existing Q rather than allocating another ID, every answer gets an independent TX/receipt, and a failure on question N leaves earlier answers committed and later questions pending.
3. Add failing tests for follow-up Parent Q linkage, duplicate IDs, tampered spans/hashes, forbidden chat placeholders, and publication rejection while any answer remains pending.
4. Introduce ledger schema `4.2` and QA schema `1.2`, while keeping strict read compatibility with `4.1`/`1.1` samples.
5. Implement `register_question_batch(...)` as one atomic intake transaction and `answer_question(...)` as one atomic per-Q answer transaction. Each intake record must include input event, intent/order, answer status, anchor, state, TX, and receipt.
6. Extend the validator so pending intake records are valid working state but cannot qualify for publication. Apply type-specific depth checks only after an answer is present.
7. Rerun focused, regression, adversarial, transaction, and validator tests.

## Task 3 — Question queue state machine and compaction recovery

**Files:**

- Modify: `scripts/interaction_state.py`
- Modify: `scripts/study_events.py`
- Modify: `scripts/validate_learning_ledger.py`
- Modify: `tests/test_event_state_and_handoff.py`
- Modify: `tests/test_question_batch_v62.py`

1. Add failing tests for `REGISTERING_QUESTION_BATCH`, `ANSWERING_QUESTION_QUEUE`, `QUESTION_BATCH_REPAIR`, and `REPAIR_REQUIRED` transitions.
2. Test exact return-state restoration, queue order across handoff/restore, refusal to advance with pending questions, and recovery after an answer transaction failure.
3. Implement the queue transition helpers and serialize input event, remaining Q IDs, current Q, captured return state, pending intents, retest, corrections, evidence, and unique next action in handoff.
4. Keep advancement fail-closed whenever queue, retest, receipt, or state consistency is unresolved.
5. Rerun focused state/handoff and adversarial suites.

## Task 4 — Mode-aware teaching response contract

**Files:**

- Modify: `scripts/validate_teaching_response.py`
- Modify: `assets/NODE_TEACHING_CONTRACT.md`
- Modify: `references/teaching-output-contract.md`
- Modify: `tests/test_teaching_response_contract_v6.py`
- Modify: `tests/test_interaction_modes_v62.py`

1. Add failing fixtures for `start`, `node-teaching`, `question-answer`, `recall-assessment`, `recovery`, `repair`, and `close` profiles.
2. Prove that every profile requires a location strip and closure/receipt strip, but only node teaching requires the complete teaching body.
3. Prove conditional evidence contracts: tensor content requires concrete Shape flow; code requires a source-grounded code block; metric requires formula/threshold/project field; state/config does not require fabricated numeric Shape.
4. Implement profile-aware validation with backward-compatible default `node-teaching` behavior.
5. Rerun focused teaching and Skill regression tests.

## Task 5 — Standard interaction mode and learner-facing prompts

**Files:**

- Modify: `SKILL.md`
- Rewrite: `references/user-prompts.md`
- Create: `references/interaction-mode-protocol.md`
- Modify: `references/prompt-workflow-patterns.md`
- Modify: `references/question-protocol.md`
- Modify: `references/learning-ledger-protocol.md`
- Modify: `tests/test_user_prompts_contract.py`

1. Replace brittle prompt-text assertions with behavioral tests that execute the v6.2 router and response validator against natural learner messages.
2. Reduce the learner surface to one start prompt plus natural commands/questions; move diagnostics, repair, receipts, and internal state wording to an advanced appendix.
3. Define the fixed loop `定位 → 学习 → 检验 → 沉淀 → 等待`, six learner-visible modes, seven internal response profiles, and the two-stage question batch contract.
4. Require: evaluate recall before explaining; preserve the original recall after side questions; never consume an old continue; and never say saved/validated/complete without host-executed controls and verified receipts.
5. Rerun prompt, interaction, response, and structure tests.

## Task 6 — Documentation, research acknowledgements, and release metadata

**Files:**

- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `GITHUB_RESEARCH_AND_ACKNOWLEDGEMENTS.md`
- Modify: `scripts/validate_skill_structure.py`
- Create: `PROJECT_CODE_STUDY_V6_2_IMPLEMENTATION_REPORT.md`

1. Update version references to `6.2.0` and require the new protocol/tests in static structure checks.
2. Make README the behavior entry point: standard loop, natural input, arbitrary question batches, QA/LOG/memory/document boundaries, receipts, compact handbook, commands, tests, limitations, and host-dependent `not-run` items.
3. Thank the real reference projects and state what was adopted as an idea versus rejected or not copied: learn-codebase, GitHub Copilot customization, Claude Code skills, Anthropic skill-creator, Superpowers, and awesome-copilot.
4. Record the mapping from v6.1 usability gaps to v6.2 mechanisms and remaining risks.
5. Run static structure and documentation contract tests.

## Task 7 — Full verification, protected-sample check, commit, and push

**Files:**

- Test only: repository test suite
- Read-only hash comparison: `D:/python program/Pedestrian detection system`

1. Record hashes of the protected sample artifacts before verification.
2. Run all unit tests, strict QA/LOG validation fixtures, memory doctor, document validator, cold-start tests, mixed-intent tests, retest/old-continue gates, ID uniqueness, receipt hashes, memory maintenance/refusal, compaction recovery, and static structure.
3. Run a real Codex-host conversational smoke test within this implementation session where possible; mark multi-model, real host compaction, Claude hooks, and pre-response control hooks `not-run` unless actually executed.
4. Compare protected sample hashes and confirm no learner project artifact changed.
5. Inspect `git diff`, status, branch, and remote. Stage only Skill/design/test/report files, create a clear v6.2 commit, push the current branch, and verify the remote SHA.
6. Report tests, not-run boundaries, commit, branch, remote, push result, changed files, retained mechanisms, mechanism mapping, acknowledgements, and residual risks.
