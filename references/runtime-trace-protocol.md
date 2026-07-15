# Runtime Trace Protocol

Use this protocol to generate Step 3 and the dynamic Step 4.x route from repository evidence.

## 1. Scan first, teach selectively

Inspect or index the complete relevant source tree before declaring the core route. The purpose is coverage discovery, not loading every file into the response or context.

Build an inventory of:

- executable entrypoints and commands;
- factories/builders/registries;
- data preparation and batch assembly;
- model or system forward path;
- objectives, assignment, losses, backward/update;
- inference, post-processing, evaluation, export, and deployment;
- configuration and runtime branches.

Record files that were only discovered separately from files actually read.

## 2. Choose runtime scenarios

Execution order is scenario-dependent. Create one `RUN-` path per relevant scenario, such as:

- `RUN-train`
- `RUN-infer`
- `RUN-eval`
- `RUN-export`
- `RUN-deploy`

Do not call import order or file order a runtime call path. If runtime evidence is unavailable, label the path `static trace` and state what command, debugger, hook, or log would verify it.

## 3. Build the call graph

Represent each teachable node with a stable `NODE-` ID.

| Order | Scenario | Node ID | Caller | Current symbol | Callees | Input / output | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Create nodes at a useful teaching boundary: usually one class, method, function, factory, objective, or post-processing stage. Avoid making every utility call a separate lesson unless it affects understanding.

Mark branches explicitly:

- `main`: required representative path;
- `branch`: alternate runtime behavior;
- `deferred`: useful but not currently required;
- `out-of-scope`: excluded with a reason.

## 4. Build a concept dependency graph

For every core node, identify concepts that must be understood first. Examples include a data representation before a transform, a learnable query before decoder use, or model predictions before matching and loss.

If a prerequisite is missing:

1. mark the current micro Step `blocked-prerequisite`;
2. insert a backfill micro Step before continuing;
3. preserve the original next node;
4. do not mark later Steps complete based on exposure.

## 5. Generate dynamic micro Steps

Step 3 produces the scenario map, node coverage, and proposed order. Step 4.x follows that order.

Each micro Step must cover only one primary node. A node is ready to leave when the learner can:

- locate it from its caller;
- state its local role;
- reconstruct one input/output or shape boundary;
- identify its next runtime consumer;
- name the largest remaining uncertainty.

Large nodes may be split by meaningful internal stages, but do not split merely by line count.

## 6. Maintain the main-line anchor

After every teaching answer and every side question, maintain:

```text
Current scenario:
Current Step / micro Step:
Current node:
Completed nodes:
Side-question IDs:
Exact continuation node:
```

When the learner says `继续`, resume from the exact continuation node. Do not require them to scroll back through syntax questions or prior explanations.

## 7. Reconstruct architecture after tracing

The detailed architecture explanation comes after the relevant nodes are understood. Reconstruct:

- scenario-level end-to-end data flow;
- module ownership and boundaries;
- shared versus scenario-specific nodes;
- tensor/data transformations;
- training-only and inference-only components;
- paper or documentation mapping.

This reconstruction can reveal missing nodes. Insert backfill micro Steps instead of hiding the gap in a summary.
