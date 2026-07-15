# Global Coverage and Blind-Spot Audit

Use this for Step 9 or any checkpoint audit. Reinspect evidence; do not merely summarize prior prose.

## 1. Runtime scenario coverage

| Scenario | Entrypoint | Required nodes | Traced nodes | Missing / stale nodes | Runtime verified |
| --- | --- | --- | --- | --- | --- |

Check training, inference, evaluation, export, or deployment paths that matter to the learner's goal.

## 2. Concept dependency coverage

| Concept / node | Depends on | Was prerequisite taught first? | Behavioral evidence | Action |
| --- | --- | --- | --- | --- |

Missing prerequisites require a backfill micro Step. Do not retroactively mark them learned because they appeared in a later summary.

## 3. Questions, corrections, and feedback

- Unresolved/retest Q IDs:
- Corrections that affect current summaries:
- New or low-rated feedback:
- User questions missing from the final-note plan:
- Main-line anchors that were lost or changed without evidence:

## 4. Evidence and implementation gaps

| Gap | Why it matters | Current evidence | Risk | Verification action |
| --- | --- | --- | --- | --- |

Include source files only discovered but not read, paper claims not mapped, unverified defaults, runtime paths not executed, and repository revision drift.

## 5. Related-method and composition gaps

- Same-task alternatives not compared:
- Same-bottleneck methods not considered:
- Analogous ideas worth studying:
- Module-composition hypotheses lacking interface/objective checks:

## 6. Largest current regret and next actions

Name the single largest learning gap. Rank no more than three next actions by impact and verification cost. Update the dynamic route and records before declaring the audit complete.
