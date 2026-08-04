# Final Study Document Quality Gates

The document is accepted only when every blocking gate passes.

## 1. Readiness and identity

- a fresh finalization manifest reports `ready: true`;
- explicit question closure and generation consent are recorded;
- canonical schema 2.0 frontmatter contains project identity, real ISO generation time, immutable repository revision, source LOG/QA, source/readiness/release transaction IDs, selected Q IDs, language, goal, and status;
- unavailable evidence is disclosed;
- `complete/validated` appears only after final zero-error validation.

## 2. Coverage and uniqueness

- each required Step/micro Step has exactly one coverage row;
- every done Step maps to one standalone textbook chapter;
- CHAPTER IDs, headings, and explicit anchors are unique;
- completed/mapped/skipped/unmapped counts reconcile; unmapped is zero;
- skipped Steps state reason/impact/acceptance and are not mastered;
- required RUN scenarios, core NODEs, dependencies, and scenario-specific/shared components are covered;
- Step, micro-Step, and NODE counts are never mixed.

## 3. Independent relearning

With no chat, every chapter satisfies the 20-item contract, contains an exact source excerpt whose lines match the locked revision, and teaches important QA in full rather than pointing to an index.

Step 5/6/9/10 and administrative Steps must preserve durable architecture, reproduction, audit, or synthesis knowledge rather than one-line conclusions. They must not invent technical mechanisms.

Forbidden fillers include `详见 chat`, `同上`, `前文已解释`, `见之前回答`, circular chapter references, and generic `不涉及此方面`. A truly inapplicable dimension must explain why and what evidence or durable skill replaces it.

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
- one COMMITTED schema 6.0 receipt binds QA/LOG/memory/document hashes, revision, TX/DOC-TX, readiness, all validators, cold-start evidence, not-run boundaries, current Step/NODE, timestamp, and exact response hash.

## 8. Cold-start acceptance

For each completed Step, a fresh model with no chat must recover objective/runtime position, call order, source explanation, I/O/Shape/state, important Q, exercise answer, and unverified boundary. The report is bound to the exact document SHA-256. Static semantic checks are only a proxy. If a real fresh-host run is not performed, record it as `not-run`, never `pass`.
