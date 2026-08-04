# Transaction and Evidence Protocol

## Unified release transaction (schema 6.0)

QA/LOG, memory, and document finalization may produce intermediate receipts,
but those receipts do not prove that the artifacts belong to one publication.
Formal release follows:

```text
USER INPUT → INTENT SPLIT → Q/M/C/TX allocation → TEACHING RESPONSE
→ QA → LOG → MEMORY candidate/update → DOCUMENT candidate
→ validators → real cold-start → PREPARED WAL → COMMITTED receipt
```

`scripts/release_transaction.py` computes and rechecks the SHA-256 of QA, LOG,
memory, and document. The PREPARED journal also binds source revision,
readiness manifest, validator results, cold-start result, not-run capabilities,
current Step/NODE, DOC-TX/TX, timestamp, and exact response hash. A changed
artifact aborts the WAL. Only a COMMITTED receipt authorizes final positive
claims; recovery is idempotent and a mismatching receipt is rejected.

This protocol turns the learning workflow into a fail-closed control plane. The Markdown records remain human-readable views; a machine transaction is the authority for successful persistence and advancement.

## Transaction lifecycle

1. Read LOG and QA completely when creating, repairing, migrating, or auditing a bundle.
2. Allocate `Q-`, `M-`, `C-`, and `TX-` IDs with `project_study_transaction.py`. Reject requested IDs already present in either record.
3. Build one structured delta per event. Insert a Q detail before the next section heading and append its index row inside the unique Q table. Never overwrite a whole file, tail-append an unbounded block, or replace an unknown string.
4. Stage both files in the same directory. Read back the new section boundaries, IDs, parent, anchor, answer, state, and transaction.
5. Reconcile LOG/QA maximum IDs, hot state, transaction row, correction indexes, and status views. Run `validate_learning_ledger.py --strict` with the companion record.
6. Atomically replace both targets only after validation succeeds. Emit a JSON receipt containing file hashes, `TX`/`Q`/`M`/`C` IDs, validator pass, and `persistence_status: saved`.

Any exception, failed readback, duplicate ID, validator error, or missing companion update returns `persistence_status: unsaved-partial`, preserves the old files, and blocks teaching. The model may quote a receipt; it may not manufacture one.

## Correction transaction

Store the original wording, canonical wording, evidence/status, impact, affected Steps/NODEs/Q/K records, stale patterns, retest question, and transaction ID. Update promoted LOG, QA, summary, and document views in one staged operation. Permit the original wording only in a clearly labelled historical correction section. Scan every promoted artifact after the commit and fail if an unmarked stale pattern remains.

## Claim-verifier registry

Select a verifier from `scripts/claim_verifier.py` by semantic claim type:

| Claim type | Required proof |
| --- | --- |
| `source` | real repository-relative path, symbol, and in-range line |
| `configuration` | resolved values, not an unmerged fragment |
| `runtime` | command, log, artifact receipt, and observed result |
| `mathematical` | explicit expressions checked by a deterministic calculator |
| `paper` | exact locator, title, and scope |
| `comparison` | baseline, new value, unit, scope, and labelled deltas |
| `learner_verdict` | one learner span per intent; a wrong verdict requires conflicting evidence |

Distinguish `exists`, `configured`, `resolved`, `loaded`, and `observed`. Distinguish suggested, executed, and observed commands. If a required input is absent, downgrade the claim to `待验证` instead of filling the gap from memory.

## Recovery

Recover from the last successful transaction. Do not hide a partial write by changing status fields, reusing an ID, or rebuilding a summary from chat. Repair record boundaries first; rerun strict validation; only then resume the interaction state machine.
