# Skill Improvement Plan: project-code-study

## Priority Summary

- **High Priority**: 0 remaining; P0 implemented in 5.1.0.
- **Medium Priority**: 2 host-integration items remain.
- **Low Priority**: 1 rendering-observation item remains.

## High Priority Improvements

### 1. Close machine-control bypasses

**File**: `scripts/project_study_transaction.py`, `scripts/interaction_state.py`, `scripts/finalize_project_study.py`
**Dimension**: Structural Integrity
**Impact**: implemented

**Reason**: Unique allocators, staged cross-file commits, machine receipts, hard advancement gates, fresh readiness, preflight, final validation, and atomic replacement now prevent successful bypasses in deterministic tests.

### 2. Add generic evidence verification

**File**: `scripts/claim_verifier.py`
**Dimension**: Content Organization
**Impact**: implemented

**Reason**: Claim types are verified through a registry rather than project-specific rules.

## Medium Priority Improvements

### 3. Execute a real-host golden conversation

**File**: `tests/test_adversarial_regressions.py`
**Dimension**: Structural Integrity
**Impact**: pending external host

**Suggested**: Run T-31 in Claude/Codex, capture LOG/QA/document hashes and state transitions, and record `pass`, `fail`, or `not-run`.

### 4. Add host-level receipt enforcement

**File**: host integration layer
**Dimension**: Structural Integrity
**Impact**: pending host API

**Suggested**: Make the host reject a text-only success claim when no machine receipt object is present.

## Low Priority Improvements

### 5. Sample diagram rendering

**File**: `references/teaching-output-contract.md`
**Dimension**: Writing Style
**Impact**: pending host observation

**Suggested**: Render one multi-layer Mermaid graph in each supported host and record fallback quality.

## Expected score

- Before 5.1.0 protocol implementation: approximately 84/100 (B), with executable control and fail-closed gaps.
- After deterministic 5.1.0 changes: 92/100 (A-).
- After T-31 and host integration: target 95/100 (A).
