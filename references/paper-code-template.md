# Paper-Code Mapping Template

Use this after the relevant runtime nodes have been traced. Do not map a paper concept to an unseen or merely inferred implementation.

## 1. Sources

- Paper title and source:
- Sections, figures, formulas, or tables actually inspected:
- Repository revision:
- Code files, symbols, configs, and runtime evidence inspected:
- Important missing evidence:

## 2. Mapping

| Paper concept | Paper evidence | Runtime node / code location | Implementation detail | Status |
| --- | --- | --- | --- | --- |
|  |  |  |  | Match / Simplified / Changed / Missing / Unclear |

## 3. Differences and impact

For each important difference:

- 论文描述:
- 当前实现:
- 可能原因:
- Learning impact:
- Reproduction impact:
- Evidence needed:

## 4. Formula-to-tensor mapping

- Formula and variables:
- Code tensors and shapes:
- Reduction / normalization:
- Numerical stability:
- Training-only or inference-only location:

## 5. Related methods

Add only comparisons that clarify the implementation:

- same-task alternative;
- same-bottleneck method;
- analogous idea;
- composable module and its compatibility risk.

## 6. Research questions

- Which implementation choice could change metrics?
- Which paper detail is insufficient for reproduction?
- What ablation would isolate the claimed mechanism?
- What evidence would falsify the current mapping?
