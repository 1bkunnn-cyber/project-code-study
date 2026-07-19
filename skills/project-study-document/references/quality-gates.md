# Final Study Document Quality Gates

The document is accepted only when every blocking gate passes.

## 1. Readiness and identity

- a fresh finalization manifest reports `ready: true`;
- explicit question closure and generation consent are recorded;
- canonical schema 1.2 frontmatter contains project identity, real ISO generation time, immutable repository revision, source LOG/QA, source/readiness transaction IDs, language, goal, and status;
- unavailable evidence is disclosed;
- `complete/validated` appears only after final zero-error validation.

## 2. Coverage and uniqueness

- each required Step/micro Step has exactly one coverage row;
- every done Step maps to >=1 UNIT and every UNIT maps back to >=1 done Step;
- UNIT IDs, headings, and explicit anchors are unique;
- completed/mapped/skipped/unmapped counts reconcile; unmapped is zero;
- skipped Steps state reason/impact/acceptance and are not mastered;
- required RUN scenarios, core NODEs, dependencies, and scenario-specific/shared components are covered;
- Step, micro-Step, and NODE counts are never mixed.

## 3. Independent relearning

With no chat, every UNIT teaches objective, prerequisites, actual RUN/NODE position, upstream/downstream, source execution order, I/O/Shape/formula/config/state, rationale/alternatives/trade-offs/failures, important questions/corrections, evidence boundary, self-check/full answer, and next connection.

Step 5/6/9/10 and administrative Steps must preserve durable architecture, reproduction, audit, or synthesis knowledge rather than one-line conclusions. They must not invent technical mechanisms.

Forbidden fillers include `详见 chat`, `同上`, `前文已解释`, `见之前回答`, circular `详见对应 UNIT`, and generic `不涉及此方面`. A truly inapplicable dimension must explain why and what evidence or durable skill replaces it.

## 4. Evidence and correction

- high-impact claims link source/paper/config/runtime evidence and status;
- suggested, executed, and observed results are distinct;
- paper/source coverage is not overstated;
- every M/C preserves original/canonical wording, evidence, impact, stale pattern, and transaction;
- promoted summary, UNIT, Q&A, and conclusions contain no stale pattern; historical correction tables may quote it only as history.

## 5. Questions and mastery

- Q&A source has no hidden-chat dependency and every Q has a standalone answer;
- correction-triggering and core-NODE-unlocking questions are included;
- included Qs preserve intent, canonical answer, evidence, impact, and M/C links;
- omitted Qs remain traceable;
- exposure is not represented as explainable/traceable/applied/verified without behavior evidence.

## 6. Structure and navigation

- TOC targets exist once;
- code fences are balanced;
- content is within expected UNIT/section boundaries;
- visuals are materially useful, readable in Markdown, and label RUN/NODE IDs;
- terminology is consistent and the document ends with concrete actions and evidence/artifact indexes.

## 7. Persistence

- the target was confirmed and not silently overwritten;
- a temporary sibling file was assembled once from the unique map;
- preflight passed with `validation_status: pending`;
- final validation passed after changing only that field to `validated`;
- high-risk sections and final target were read back;
- receipt reports path, revision, TX/readiness IDs, coverage, validators, cold-start evidence, and limitations.

## 8. Cold-start acceptance

For each UNIT, a no-chat reader must recover objective/runtime position, call order, I/O/Shape/state, important Q, canonical correction, self-check answer, next NODE, and unverified boundary. Static semantic checks are only a proxy. If a real fresh-session/cross-model run is not performed, record it as `not-run`, never `pass`.
