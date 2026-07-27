# Host Enforcement Boundary

The Skill can provide executable validators and a mandatory response-claim
guard, but a Skill loaded as context cannot technically prevent its host from
skipping tools and emitting arbitrary text. This distinction must remain
visible in audits.

## Available layers

1. `SKILL.md` makes the memory index and response guard part of the normal
   workflow.
2. `scripts/validate_protocol_memory.py` and
   `scripts/sync_protocol_memory.py` make memory writes deterministic on their
   own path.
3. `scripts/response_claim_guard.py` rejects exact response text that claims
   persistence/readiness without a matching receipt.
4. A host adapter can run the guard in a pre-response hook and refuse delivery
   when it fails. That is the only layer that turns the audit into a hard
   delivery gate.

## Minimum always-loaded rule

Hosts that support `AGENTS.md`, `CLAUDE.md`, or an equivalent standing-rules
file should load this compact rule there:

```text
For project-code-study, read .project-study-memory/MEMORY.md at turn start;
call the control tools before persistence/advance/finalization claims; run
response_claim_guard.py on exact outgoing text; without a passing receipt,
state unsaved/unverified and do not use saved/validated/complete language.
```

Do not claim that this snippet is a hard enforcement layer on hosts that do not
execute it. Record host capability as `enforced`, `best-effort`, or `not-run`.
