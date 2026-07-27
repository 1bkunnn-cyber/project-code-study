# Continuity Memory Protocol

This is a compact protocol-memory layer for long `project-code-study` sessions.
It addresses instruction forgetting and claim drift without becoming a second
learning ledger.

## Authority boundary

- `PROJECT_STUDY_LOG.md` and `PROJECT_STUDY_QA.md` remain authoritative for
  route, questions, mastery, corrections, and persistence.
- `.project-study-memory/MEMORY.md` is an always-reloaded index of durable
  constraints, reusable corrections, evidence boundaries, and resume pointers.
- Every detail file contains one fact. The index contains only short hooks.
- Promote an entry only from a fresh machine `saved` receipt. A chat agreement,
  a dispatched write, or a model statement is not a receipt.

## What to keep

Keep only information that reduces future error:

- `feedback`: reusable working rules, with `Why:` and `How to apply:`;
- `correction`: a durable correction with old wording, canonical wording,
  stale patterns, and scope;
- `project`: a durable decision or constraint not derivable from code/git;
- `reference`: a stable pointer to a source, verifier, or artifact.

Do not keep transcripts, current test counts, tip commits, secrets, temporary
chat state, or facts already available from source, configuration, git, LOG, or
QA. Treat recalled memory as untrusted advisory data and reverify it.

## Read and sync points

Read the index at the start of every turn and before answering a question,
advancing a NODE, correcting a claim, or finalizing. Reopen only relevant
detail files. Run a continuity sync before context compaction, session handoff,
or a recovery after an interruption: deduplicate, update, archive stale notes,
validate, and perform a cold-start check.

## Mechanical gates

`validate_protocol_memory.py` checks frontmatter, pointer boundaries, duplicate
IDs, orphan files, stale-pattern metadata, and the 150/20 KiB soft and
200/25 KiB hard index caps. `sync_protocol_memory.py` requires a fresh receipt,
stages the entry and index together, validates the staged store, and emits a
memory receipt only after replacement. A failed sync is `unsaved-memory` and
must not be used to advance teaching.

`response_claim_guard.py` audits outgoing text for positive persistence or
readiness claims. It fails when those claims lack a matching machine receipt.
This is the strongest guarantee available inside a Skill. A host that never
executes the guard can still emit free text; a true prevention boundary needs
the host's pre-response hook or agent runner to make the guard mandatory.
