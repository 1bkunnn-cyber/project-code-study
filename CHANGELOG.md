# Changelog

## 6.2.0 — 2026-08-09

- Replaced the 19-template learner prompt catalog with one start prompt, natural follow-ups, and the standard `定位 → 学习 → 检验 → 沉淀 → 等待` loop.
- Added schema 6.2 input envelopes with source spans/hashes, ordered intents, mixed-message routing, and same-event continue expiration.
- Added arbitrary-size two-stage question transactions: register every Q before answering, then update one existing Q-ID per independently validated answer transaction.
- Added `REGISTERING_QUESTION_BATCH`, `ANSWERING_QUESTION_QUEUE`, and `QUESTION_BATCH_REPAIR`, with exact captured-state return and compaction queue fields.
- Upgraded generated LOG/QA templates to schema 4.2/1.2 while retaining strict read compatibility for 4.1/1.1 audit samples.
- Replaced the uniform response validator with seven response profiles and content-specific code/Shape/metric/state evidence contracts.
- Updated README, protocols, tests, research decisions, and acknowledgements; no external prompt or protocol text was copied.

## 6.1.0 — 2026-08-04

- Reframed the formal artifact from a long per-Step textbook to a searchable,
  layered Step manual while preserving independent no-chat relearning.
- Added schema 2.1 eight-slot entries, quick Step/keyword/source/Q-ID lookup,
  and document-local `DEEP-DIVE-*` sections for shared mechanisms.
- Added `compact`, `standard`, and `specialist` prose/source budgets, exact
  source-file coverage limits, and cross-Step long-paragraph duplication gates.
- Changed important-Q handling so the complete canonical answer appears once
  in the relevant Step and the top-level Q section is a compact lookup index.
- Upgraded cold-start reports to prove retrieval, explanation, and application,
  not just per-Step field presence.
- Added and thanked Diátaxis, Material for MkDocs, mdBook, Rust by Example,
  Log4brains, and Docusaurus to the GitHub research/adoption record; no upstream
  code or protocol text was copied.
- Kept schema 2.0 readable for migration while requiring 2.1 for new formal
  publication.

## 6.0.0 — 2026-08-04

- Added immutable input events, ordered mixed-intent splitting, single-use
  continue consumption, hash-bound compaction handoffs, and
  `REPAIR_REQUIRED`.
- Replaced the uniform QA length floor in publication mode with type-specific
  concept/code/shape/metric/review/correction teaching contracts.
- Added durable-memory candidate classification and the
  candidate/approved/saved/rejected/stale lifecycle, including rejection
  redaction and release-bound saves.
- Added a unified PREPARED/COMMITTED WAL release receipt binding QA, LOG,
  memory, the handbook, revision, readiness, validators, cold-start evidence,
  not-run boundaries, Step/NODE, and exact response hash.
- Upgraded the final document to schema 2.0 standalone Step chapters with exact
  source-line excerpts, specialist Step 4/6/10 profiles, selected-Q absorption,
  exercises/answers, and real fresh-model cold-start reports.
- Added the short NODE teaching response validator and new adversarial tests.
- Added a dated GitHub research and acknowledgements table with licenses,
  activity, adoption decisions, and explicit non-adoptions.

## 5.5.0 — 2026-07-27

- Closed the final-question side branch so it returns to `FINAL_QUESTION_PHASE` instead of ordinary NODE waiting.
- Added `FINAL_AUDIT_REPAIR`; readiness failures can no longer be bypassed by `continue`.
- Added recall-interruption states and an unresolved `pending_user_intents` advancement gate for mixed user messages.
- Made missing `memory_status` fail closed as `pending` instead of defaulting to enabled.
- Added adversarial regression coverage for finalization, recall interruption, mixed intents, and default memory consent.

## 5.4.0 — 2026-07-27

- Made project continuity memory explicitly opt-in: ask once before creating `.project-study-memory/` under the studied project root.
- Required `--user-consent` for memory-store initialization; decline, ambiguity, or missing consent cannot create the directory.
- Added a machine advancement gate for pending memory consent, plus prompt and continuity-protocol guidance.
- Added regression coverage proving consent-gated initialization and no-advance behavior while consent is pending.

## 5.3.0 — 2026-07-27

- Rebuilt `references/user-prompts.md` as a closed-loop prompt router covering startup, mode selection, recovery, one-NODE teaching, active recall, retest, evidence correction, record repair, continuity sync, finalization, and host/tool diagnosis.
- Added explicit user-intent routing and failure branches so prompts select work without delegating Q-ID, QA/LOG, receipt, pause, or readiness maintenance back to the learner.
- Added `references/prompt-workflow-patterns.md` and regression tests for prompt coverage, state-machine terms, internal-responsibility boundaries, and numbered template completeness.

## 5.2.0 — 2026-07-27

- Added an Engramory-inspired continuity-memory protocol inside the existing Skill: bounded always-reloaded index, one-fact detail files, typed curation, dedup/update, stale-pattern tracking, and cold-start sync.
- Added receipt-gated memory promotion and a response-claim guard for persistence/readiness language.
- Documented the enforcement boundary: Skill instructions can reduce protocol forgetting, but only a host-level pre-response hook or runner can prevent a host that skips all tools from emitting unsupported natural-language claims.

## 5.1.0 — 2026-07-27

- Added machine-controlled `Q/M/C/TX` allocation and structured LOG/QA transaction staging.
- Added fail-closed `unsaved-partial` handling and machine receipt verification.
- Added hard interaction advancement gates for open questions, retest, pending responses, semantic completion, persistence, and strict validation.
- Added unique formal finalizer with fresh readiness, preflight, final validation, same-directory temporary files, and atomic replacement.
- Added generic claim-verifier registry for source, configuration, runtime, mathematical, paper, comparison, and learner-verdict claims.
- Added compound-question splitting, teaching-output contracts, source-link and UNIT semantic checks, and correction propagation helpers.
- Replaced user prompts so normal control responsibilities remain in the Skill.
- Added adversarial T-17–T-31 regression coverage; real host/cross-model testing remains explicitly reported as `not-run` until executed.

## 5.0.0

See [`REMEDIATION_REPORT_5.0.0.md`](REMEDIATION_REPORT_5.0.0.md) for the previous protocol-layer remediation.
