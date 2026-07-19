# Runtime Trace Protocol

Use this protocol to generate Step 3 and dynamic Step 4.x from repository evidence.

## 1. Scan first, teach selectively

Index the complete relevant source tree for coverage discovery: entrypoints; builders/registries; data and batch assembly; system forward path; objectives/assignment/loss/backward/update; inference/post-processing/evaluation/export/deployment; configs and runtime branches. Distinguish `discovered` files from files actually read.

## 2. Choose runtime scenarios

Create one `RUN-` path per relevant scenario, for example `RUN-train`, `RUN-infer`, `RUN-eval`, `RUN-export`, or `RUN-deploy`. Import order, file order, and directory order are not runtime paths. If execution evidence is unavailable, label the route `static trace` and record the command/hook/debugger/log that would verify it.

## 3. Build auditable call and dependency graphs

Represent every teachable node with one stable NODE ID:

| Order | Scenario | Node ID | Caller | Current symbol | Callees | Input/output | Evidence | Branch | Status | Reason/impact/revisit/acceptance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Create nodes at useful teaching boundaries, normally one class, method, function, factory, objective, or post-processing stage. Mark branches `main`, `branch`, `deferred`, or `out-of-scope`.

NODE status is exactly one of:

`discovered`, `planned`, `active`, `traced`, `verified`, `blocked-prerequisite`, `deferred`, `skipped`, `stale`.

Never use mixed status text. `deferred`/`skipped` requires reason, learning/coverage impact, revisit condition, and learner acceptance. Summary ranges may not replace individual rows. Count Steps, micro Steps, and NODEs separately.

For every core NODE, identify concepts required first. If a dependency is missing, mark the micro Step and NODE `blocked-prerequisite`, insert a backfill micro Step, preserve the original continuation NODE, and do not promote downstream completion.

## 4. Generate dynamic micro Steps

Step 3 records scenario maps, NODE coverage, concept dependencies, and proposed order. Step 4.x follows that graph. Each micro Step covers one primary NODE. Large nodes may be split by meaningful internal stages, never merely line count.

A NODE is ready to leave only after the semantic completion gate and durable knowledge transaction pass. A learner must locate it from the caller, state its role, reconstruct an input/output or Shape/state boundary, identify its downstream consumer, and address the largest uncertainty.

## 5. Main-line and interaction control

Maintain:

```text
Current scenario:
Current Step / micro Step:
Current NODE:
Completed NODEs:
Side-question IDs:
Exact continuation NODE:
Interaction state:
Pending learner response:
```

Side questions, corrections, and recall answers preserve the exact continuation NODE. Their completion enters `AWAITING_QUESTIONS_OR_CONTINUE` and stops. Only a fresh `继续` from that state may enter the continuation NODE; consume it once.

If teaching is interrupted, resume the unfinished field or verification in the current micro Step. Never infer `done` from a later session, a new Step number, or a summary.

## 6. Visual strategy

Choose the smallest clear representation:

1. short linear chain for one simple path;
2. Markdown table for NODE mappings, Shape/state changes, or branch comparisons;
3. Mermaid for three or more dependent layers, train/eval forks, or state transitions;
4. ASCII only for a very short alignment-stable sketch.

Label diagrams with RUN/NODE IDs and keep them readable in ordinary Markdown. Avoid large shaded character art or diagrams dependent on fragile monospace alignment.

## 7. Reconstruct architecture after tracing

After the relevant nodes are understood, reconstruct scenario data flow, ownership/boundaries, shared versus scenario-specific nodes, transformations, training-only/inference-only parts, and paper/document mapping. If reconstruction exposes a missing core NODE, insert a backfill micro Step instead of hiding the gap in a summary.
