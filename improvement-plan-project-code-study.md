# Skill Improvement Plan: project-code-study

## Priority Summary

- **High Priority**: 0 repository-local blockers
- **Medium Priority**: 3 host/evaluation follow-ups
- **Low Priority**: 3 maintenance improvements

## Historical high-priority work retained

### Machine-control bypasses (implemented in 5.1.0, extended in 6.0.0)

`project_study_transaction.py`, `interaction_state.py`, claim verification,
fresh readiness, preflight/final validation, and atomic single-file replacement
closed the original deterministic bypasses. Version 6 retains these controls
and adds ordered input events, typed memory, schema 2.0 publication, unified
release receipts, and exact-response binding.

### Generic evidence verification (implemented in 5.1.0)

`claim_verifier.py` continues to route source, configuration, runtime,
mathematical, paper, comparison, and learner-verdict claims through a registry
instead of project-specific exceptions.

## Medium Priority

### 1. Run a fresh-load golden teaching conversation

**Scope**: external Claude/Codex host
**Reason**: Current Codex Desktop maintenance execution proves real tool
orchestration, but the edited v6 Skill was not reloaded into a fresh teaching
task. Run mixed intent, recall interruption, retest, recovery, and publication
claim scenarios and attach the transcript-derived report without committing
private chat.

### 2. Integrate the exact-response guard in a host pre-response hook

**Scope**: host runner/plugin, not this Skill repository
**Reason**: `response_claim_guard.py` is enforceable only when the host invokes
it against the exact final response. Until then, report the hook `not-run`.

### 3. Exercise a real context compaction

**Scope**: host compact/handoff facility
**Reason**: Local handoff hash mismatch tests pass, but a genuine host
compaction and resume must confirm that the complete handoff is loaded before
the model guesses state.

## Low Priority

### 4. Add more schema 2.0 gold fixtures

Create non-vision examples for backend and tooling repositories so specialist
profiles remain project-neutral outside Steps 4/6/10.

### 5. Track upstream acknowledgement changes

Recheck repository licenses, archive status, and implementation relevance at
release time. Do not automatically import upstream code when a project changes
license or architecture.

### 6. Observe diagram rendering in supported hosts

Render one multi-layer Mermaid RUN/NODE graph in each supported host and record
fallback readability. This remains a host observation, not a static pass.

## Expected Outcome

Completing the three host-dependent items would raise confidence from an A
repository implementation to an A+ multi-host release. They are intentionally
not marked complete by local static tests.
