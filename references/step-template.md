# Runtime-NODE Micro-Step Template

Use for Step 4.x and any runtime-driven source lesson. Keep one primary NODE per teaching response.

## Step <N.x>: <RUN scenario> — <NODE ID> <symbol>

### Main-line preflight

- Interaction state before teaching: `TEACHING_CURRENT_NODE`
- Scenario / caller / current symbol:
- Exact continuation NODE:
- Pending learner response: `false`
- Relevant Q/M/C IDs:

### Learning target and evidence

State one observable behavior for completion.

- Source location and revision:
- Config/paper/runtime evidence when relevant:
- Evidence status: `已确认` / `可推断` / `背景知识` / `待验证`
- Largest unverified boundary:

### NODE explanation

Explain local responsibility, important inputs/outputs and Shape/state, key logic in execution order, blocking syntax, design rationale/trade-offs, downstream consumer, and one relevant risk. Do not force unrelated paper, AMP, deployment, or every parameter into the NODE.

| Boundary | Symbol / operation | Data, Shape, or state | Meaning / evidence |
| --- | --- | --- | --- |
| Caller -> NODE |  |  |  |
| Inside NODE |  |  |  |
| NODE -> callee |  |  |  |

### Dependency and comparison

- Missing prerequisite/backfill, if any:
- One useful comparison only when it clarifies this NODE:

### Verification and pause

Ask one or two retrieval/trace/predict questions, set `interaction_state: AWAITING_RECALL`, and wait. Do not include the answer or next NODE teaching in the same turn.

After the learner responds, follow `question-protocol.md`, persist the complete reference answer, set `interaction_state: AWAITING_QUESTIONS_OR_CONTINUE`, preserve the continuation NODE, and stop.

### Durable knowledge card (required before `done`)

```text
K ID:
Step / NODE:
Transaction ID:
Prerequisites:
Learning objective:
Runtime position:
Complete explanation:
Source locations:
Inputs / outputs / Shapes / states:
Rationale / alternatives / trade-offs:
Important Q IDs:
Canonical M/C IDs and wording:
Evidence status and remaining boundary:
Self-check:
Complete reference answer:
Next connection:
Mastery behavior evidence:
```

Empty fields, answer placeholders, or one-line exposure notes fail completion.

### End state

- Micro-Step status:
- Current scenario / NODE:
- Most important unresolved issue:
- Exact continuation NODE:
- Interaction state:
- Persistence receipt with TX/Q/M/C/K IDs and strict validation:
