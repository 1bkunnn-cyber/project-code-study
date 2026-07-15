# Comparison and Extension Protocol

Use this protocol to deepen understanding and support research ideation without derailing the runtime-learning route.

## 1. Four comparison levels

Select at most a few high-value references from:

1. **Same task**: competing model or system families.
2. **Same bottleneck**: methods solving the same failure mode, cost, or data limitation.
3. **Analogous idea**: the same abstraction used in another task or domain.
4. **Composable module**: a component that might be integrated or "缝合" into the current project.

Name the exact version, paper, repository, or implementation when differences matter. Do not treat a family name such as “YOLO” as one immutable model.

## 2. Comparison card

For each selected comparison, record:

| Item | Current project | Comparison | Learning value |
| --- | --- | --- | --- |
| Problem formulation |  |  |  |
| Representation / interface |  |  |  |
| Training objective |  |  |  |
| Runtime behavior |  |  |  |
| Inductive bias |  |  |  |
| Engineering trade-off |  |  |  |
| Failure mode |  |  |  |

Then state the shared abstraction and the key incompatibility.

## 3. Module-composition test

Before recommending a composition, check:

- problem fit: does the module solve an observed bottleneck?
- interface fit: shapes, data types, coordinate systems, masks, and lifecycle;
- objective fit: losses, assignments, gradients, and supervision;
- optimization fit: initialization, scale, convergence, and stability;
- runtime cost: memory, latency, throughput, and deployment constraints;
- prior art: whether the combination already exists;
- attribution: which ablations isolate the source of improvement.

Classify the result as:

- engineering integration;
- adaptation with a new mechanism;
- research hypothesis requiring evidence;
- unsupported combination.

Combining modules is not automatically an innovation. Require a causal motivation and a falsifiable experiment.

## 4. Timing and scope

Add comparisons when they clarify the current node, expose an alternative, or support a concrete research question. Keep the main runtime node visible and return to it after the extension.

Store only compact comparison conclusions in the main ledger. Put detailed literature work in final notes or a dedicated research artifact when requested.
