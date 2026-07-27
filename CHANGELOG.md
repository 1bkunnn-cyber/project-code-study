# Changelog

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
