# Final Study Document Generation Protocol

Use this protocol to transform completed learning evidence into a durable Markdown artifact. The design combines three useful patterns:

- post-process synthesis from `results-report`: lock source artifacts, separate supported conclusions from tentative interpretation, retain failures and limitations, state what changed understanding, and finish with evidence plus next actions;
- codebase-to-tutorial generation: identify core abstractions, analyze relationships, order chapters, write each chapter with prior context, then combine the result;
- documentation coverage discipline: keep tutorial, reference, explanation, and how-to reader modes distinct even inside one file.

## 1. Readiness decision

Final generation is allowed only when:

1. every required dynamic Step and micro Step is complete or explicitly skipped with accepted impact;
2. required runtime scenarios and core nodes pass coverage audit;
3. no blocking concept dependency remains;
4. every substantive user question is answered and closed or intentionally deferred;
5. no active-recall answer or learner response is pending;
6. correction and stale-claim audits pass;
7. the learner says they have no more questions for this round and explicitly accepts generation.

Do not infer consent from silence, elapsed time, or the last numbered Step.

## 2. Source-bundle manifest

Lock the following before drafting:

| Source class | Expected content | Required treatment |
| --- | --- | --- |
| Learning ledger | route, RUN/NODE/K/SRC/M/C/EXP/CMP records, mastery, milestones | read fully; record path and schema |
| Q&A record | user questions, follow-ups, complete answers, feedback | read fully; select important Q IDs |
| Repository | revision, entrypoints, symbols, configs, tests | pin revision; verify promoted technical claims |
| Paper/docs | paper claims, formulas, official documentation | identify exact source and version |
| Runtime evidence | commands, logs, outputs, metrics | distinguish executed evidence from planned checks |
| Experiments | successes, failures, negative results, ablations | retain interpretation-changing results |

If a source is missing, state the limitation in frontmatter and the evidence-boundary section. The ledger can point to evidence but cannot replace it for high-impact claims.

## 3. Build a document knowledge graph

### Identify abstractions

Derive abstractions from completed learning records, not from repository popularity or model memory. Typical abstractions include runtime scenarios, lifecycle components, data representations, objective mechanisms, configuration systems, and evaluation contracts.

For each abstraction collect:

- related RUN/NODE/K IDs;
- source and paper evidence IDs;
- input/output or shape boundary;
- upstream/downstream relationships;
- important Q/M/C IDs;
- mastery evidence and unresolved limitations.

### Analyze relationships

Represent relationships such as `calls`, `constructs`, `transforms`, `supervises`, `matches`, `optimizes`, `post-processes`, or `evaluates`. Prefer actual runtime and data relationships over generic architecture labels.

### Order chapters

Use this precedence:

1. prerequisites needed to understand the representative input;
2. actual runtime order in the primary scenario;
3. concept dependencies that must be inserted before a downstream node;
4. alternate scenarios and shared-node differences;
5. architecture reconstruction and cross-cutting explanations;
6. reproduction, comparison, and extension material.

Chapter order must not be copied blindly from Step numbers or file layout.

## 4. Build complete Step-to-knowledge coverage

### Create the Step manifest

Enumerate every Step and micro Step from the completed dynamic route, including inserted prerequisite/backfill Steps and explicitly skipped Steps. Build one coverage row per Step with:

- Step or micro-Step identifier and status;
- the durable knowledge learned in that Step, not merely its topic or activity;
- related RUN/NODE/K, source, question, misconception, and correction IDs;
- mastery evidence;
- the `UNIT-` relearning unit that teaches the knowledge again;
- skip reason and impact when the Step was not learned.

Every completed Step must map to one or more relearning units. Every relearning unit must map back to one or more Step rows. Multiple Steps may share a unit when they form one coherent concept, but each Step retains its own coverage row. Deduplicate explanations in the body, not coverage in the manifest.

The manifest must report the number of completed, mapped, skipped, and unmapped Steps. `unmapped` must be zero before a complete document can be accepted.

### Write standalone relearning units

A one-line takeaway or route table is not enough for relearning. Each `UNIT-` unit must let a learner recover the knowledge without the original chat and should include:

1. covered Steps and prerequisites;
2. learning objective and runtime/conceptual position;
3. a complete explanation of the mechanism;
4. exact source symbols, configurations, formulas, and paper links when applicable;
5. inputs, outputs, shapes, state changes, invariants, or data transformations;
6. design rationale, alternatives, trade-offs, and failure modes;
7. important user questions, misconceptions, and canonical corrections;
8. evidence status and unresolved boundaries;
9. a self-check or transfer question followed by a reference answer;
10. the connection to the next runtime node or concept.

Do not pad administrative Steps with invented technical content. Explain what durable project-navigation or evidence skill the learner gained. For skipped Steps, record the reason and impact without creating false mastery.

## 5. Write one coherent Markdown document

Default to `PROJECT_STUDY_DOCUMENT.md`. Treat it as a standalone learning artifact for a smart reader who does not have the original conversation.

Use the canonical template. Organize the main explanation by runtime and conceptual dependency, then use the Step coverage manifest as a complete navigation layer. Every major chapter should answer:

- What problem or role does this concept have?
- Where is it in the actual runtime path?
- What evidence supports the explanation?
- What are the important inputs, outputs, shapes, parameters, or invariants?
- Why is it designed this way, and what alternatives exist?
- What did the learner initially misunderstand or ask about?
- What remains uncertain or unverified?

Use Mermaid only when it materially clarifies call, data, dependency, or lifecycle relationships. Keep diagrams traceable to RUN/NODE IDs.

## 6. Results-report-inspired synthesis

The document is not a transcript. It must explicitly include:

- highest-confidence learning conclusions;
- study identity and decision context: project revision, learning goal, route, and audience;
- main findings: the few mechanisms that explain most project behavior;
- evidence strength and unsupported-claim boundaries;
- failures, negative results, limitations, and missing evidence;
- what changed the learner's understanding, especially through questions and corrections;
- next actions: stop, continue, review, reproduce, modify, compare, or experiment;
- artifact and reproducibility index.

Avoid chronological transcript summaries such as “Step 1 discussed X, then Step 2 discussed Y.” Complete Step coverage is mandatory, but the teaching body should still follow runtime and conceptual relationships. Use the Step manifest to connect route order to the relevant relearning units.

## 7. Writing transaction

1. Confirm output path and overwrite behavior.
2. Instantiate the template and replace all placeholders.
3. Draft sections from the knowledge graph and evidence manifest.
4. Run the Step coverage, important-question, and correction audits.
5. Run the quality gates and validator with the source ledger.
6. Read back high-risk sections.
7. When authorized, add one ledger artifact record with path, revision, date, and validation result.
8. Return a concise receipt.

Never claim the document is final if validation fails or a readiness condition was discovered to be false.
