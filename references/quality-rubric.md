# Study Quality Rubric

Use this rubric without turning every answer into a checklist recital.

## Evidence levels

| Level | Meaning | Permitted wording |
| --- | --- | --- |
| E0 | No project evidence | `当前材料中未看到证据` |
| E1 | Direct source/document observation | `已确认` with path/symbol/page |
| E2 | Cross-source inference | `可推断` plus missing verification |
| E3 | Runtime/experiment verification | `已验证` with command/log/output |

Background knowledge is separate from E0–E3 project evidence.

## Route quality gate

Before deep source teaching:

- relevant source inventory was scanned or indexed;
- at least one representative runtime scenario was chosen;
- Step 3 records caller/callee nodes and concept dependencies;
- Step 4.x order comes from the call graph rather than a fixed model taxonomy;
- training-only, inference-only, and shared nodes are distinguishable.

If these are missing, do not claim the core architecture is covered.

## Micro-Step completion gate

A node is `done` only when the learner can, with evidence:

- locate it from its caller;
- state its local purpose;
- reconstruct one input/output or shape/data boundary;
- identify its downstream consumer;
- answer or schedule the largest uncertainty.

Otherwise use `blocked-prerequisite`, `review`, or `active`.

## Step completion gate

A Step is complete only when:

- required micro Steps are complete or explicitly skipped with impact;
- the learner demonstrates the central mechanism in their own words;
- at least one important call path and data/shape path is reconstructed;
- unresolved core dependencies have actions;
- the record write and readback succeeded.

Exposure, a long explanation, agreement, `继续`, self-confidence, or a manually advanced Step number is not evidence of mastery.

## Active-recall closure

After every learner answer provide:

`verdict → correct parts → repair → complete reference answer → evidence → impact → save receipt`

Never leave the learner with only an evaluation or partial hints.

## Correction and final-note gate

When wording changes, preserve the old wording, create a canonical correction, mark stale material, and update affected knowledge cards. Before final notes:

- resolve correction IDs;
- search for stale formulations;
- verify terminology consistency;
- distinguish exposure from demonstrated mastery;
- report unresolved evidence honestly.

## Context discipline

Normal continuation reads hot state plus relevant IDs, not the full ledger or Q&A history. A response should teach one primary node unless the user requests synthesis.
