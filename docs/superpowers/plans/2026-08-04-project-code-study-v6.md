# Project Code Study v6 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Execution status (2026-08-04):** Implemented and verified. The checkboxes
below preserve the approved prospective plan; actual files, scoped deviations,
test evidence, host attempts, and not-run boundaries are recorded in
`IMPLEMENTATION_AND_TEST_REPORT_6.0.0.md`.

**Goal:** Build a local, fail-closed project-learning workflow with durable state recovery, typed teaching validation, unified receipts, curated memory, and standalone source-grounded handbooks.

**Architecture:** Keep Markdown artifacts as source of truth, add JSON event/handoff/receipt envelopes, and use a write-ahead journal plus final commit marker for cross-file publication. Split static validation from real-host validation and make every formal claim depend on a matching committed receipt.

**Tech Stack:** Python 3.9+ standard library, Markdown, JSON, `unittest`, Git.

## Global Constraints

- Do not add database, vector, cloud-memory, model-SDK, or network runtime dependencies.
- Do not modify the pedestrian-detection project or its QA/LOG/memory/document audit samples.
- Preserve all twenty v5.5 non-regression invariants named in the approved design.
- Do not claim real-host, multi-model, real-compaction, or pre-response-hook success from static tests.
- Use Conventional Commits and push only Skill, README, tests, and design artifacts.

---

### Task 1: Event State and Recovery

**Files:**
- Modify: `scripts/interaction_state.py`
- Create: `scripts/study_events.py`
- Create: `tests/test_event_state_and_handoff.py`

**Interfaces:**
- Produces: `split_intents(text, input_event_id)`, `consume_continue(state, event_id)`, `build_handoff(state, artifact_hashes)`, `validate_handoff(payload, artifact_hashes)`.

- [ ] Write tests proving mixed prose intents remain ordered, continue events are single-use, and mismatched handoff hashes enter repair.
- [ ] Run the tests and verify missing APIs fail.
- [ ] Implement immutable event IDs, consumed continue IDs, typed pending intents, and handoff validation.
- [ ] Run focused and full unit tests.

### Task 2: Type-Specific QA Contracts

**Files:**
- Modify: `scripts/validate_learning_ledger.py`
- Modify: `assets/PROJECT_STUDY_QA.template.md`
- Modify: `references/question-protocol.md`
- Create: `tests/test_qa_depth_contracts.py`

**Interfaces:**
- Produces: `validate_question_depth(question_type, body) -> list[str]`.

- [ ] Add failing fixtures for shallow concept/code/shape/metric/review/correction answers.
- [ ] Verify each fails for the missing semantic section.
- [ ] Implement per-type requirements and legacy type mappings.
- [ ] Add complete passing fixtures and run all tests.

### Task 3: Memory Lifecycle and Compaction Handoff

**Files:**
- Create: `scripts/memory_lifecycle.py`
- Modify: `scripts/sync_protocol_memory.py`
- Modify: `scripts/validate_protocol_memory.py`
- Modify: `assets/PROJECT_STUDY_MEMORY.template.md`
- Create: `assets/PROJECT_STUDY_HANDOFF.template.json`
- Create: `tests/test_memory_lifecycle_v6.py`

**Interfaces:**
- Produces: `classify_memory_candidate`, `transition_candidate`, `create_compaction_handoff`, `restore_compaction_handoff`.

- [ ] Add failing tests for one-off questions, durable preferences, corrections, quality feedback, Step rules, rejection redaction, stale transitions, and hash-mismatched restore.
- [ ] Implement trigger classification and fail-closed transitions.
- [ ] Bind saved memory updates to the source transaction hash.
- [ ] Run memory doctor and full tests.

### Task 4: Unified Release Transaction and Receipt Chain

**Files:**
- Create: `scripts/release_transaction.py`
- Modify: `scripts/project_study_transaction.py`
- Modify: `scripts/response_claim_guard.py`
- Modify: `scripts/validate_finalization_bundle.py`
- Modify: `scripts/finalize_project_study.py`
- Create: `assets/PROJECT_STUDY_RELEASE_RECEIPT.schema.json`
- Create: `tests/test_release_transaction_v6.py`

**Interfaces:**
- Produces: `prepare_release`, `commit_release`, `recover_release`, `validate_release_receipt`, `authorize_claim`.

- [ ] Add failing tests for missing memory/document hashes, rollback, dangling PREPARED journal, receipt-chain mismatch, stale source revision, and exact-response claim binding.
- [ ] Implement canonical JSON hashing, WAL, rollback verification and final commit marker.
- [ ] Route question/document publication through the unified receipt.
- [ ] Run focused adversarial and full tests.

### Task 5: Handbook Contract and Source Fidelity

**Files:**
- Modify: `skills/project-study-document/SKILL.md`
- Modify: `skills/project-study-document/assets/PROJECT_STUDY_DOCUMENT.template.md`
- Modify: `skills/project-study-document/references/document-generation-protocol.md`
- Modify: `skills/project-study-document/references/document-selection-rules.md`
- Modify: `skills/project-study-document/references/document-validation-checklist.md`
- Modify: `skills/project-study-document/scripts/validate_study_document.py`
- Create: `scripts/cold_start_test.py`
- Create: `tests/test_handbook_contract_v6.py`

**Interfaces:**
- Produces: `validate_chapter_contract`, `validate_source_excerpt`, `evaluate_cold_start_report`.

- [ ] Add failing tests for missing 20-part chapters, missing key Q absorption, wrong source lines/hash, cyclic chat references, incomplete Step 4.x/6/10 profiles, and `not-run` cold-start.
- [ ] Implement chapter/source/profile validation and deterministic cold-start questions.
- [ ] Add a complete v6 gold fixture and prove publication passes.
- [ ] Prove the unchanged pedestrian-detection document fails v6 publication audit for expected reasons.

### Task 6: Teaching Response and Host Capability Contract

**Files:**
- Create: `scripts/validate_teaching_response.py`
- Modify: `references/teaching-output-contract.md`
- Modify: `references/host-enforcement-boundary.md`
- Modify: `references/user-prompts.md`
- Modify: `SKILL.md`
- Create: `tests/test_host_and_response_contract_v6.py`

**Interfaces:**
- Produces: `validate_node_response`, `evaluate_host_capabilities`.

- [ ] Add failing tests for missing anchor/code/shape/rationale/error/self-test/receipt state and unauthorized formal claims.
- [ ] Implement the short teaching contract loader and capability manifest rules.
- [ ] Ensure advisory hosts cannot produce formal saved/validated/complete claims.
- [ ] Run full tests.

### Task 7: Documentation and Research Acknowledgements

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `references/continuity-memory-protocol.md`
- Modify: `references/transaction-and-evidence-protocol.md`
- Modify: `references/quality-rubric.md`
- Modify: `references/final-summary-template.md`

- [ ] Document the real goal, state machine, artifact responsibilities, memory triggers, unified receipts, handbook standard, cold-start method, commands, tests and limitations.
- [ ] Add an acknowledgements section with project links, borrowed ideas, licenses and explicit non-adoptions.
- [ ] Check commands against actual `--help` output.

### Task 8: Verification, Host Attempt, Git and Push

**Files:**
- Create: `IMPLEMENTATION_AND_TEST_REPORT_6.0.0.md`

- [ ] Run structural checks, all unit tests, strict v6 gold checks, memory doctor, final document validator, cold-start, mixed intents, retest, stale continue, all ID uniqueness, receipt hash, memory rejection, and compaction restore.
- [ ] Attempt an isolated real Claude/Codex host test and record exact capability/status.
- [ ] Record multi-model, real-compaction and pre-response hook as pass only with direct evidence; otherwise `not-run`.
- [ ] Review `git diff`, confirm no private/sample artifacts are tracked, create a Conventional Commit, and push the current branch to `origin`.
