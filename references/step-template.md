# Step Template

Use this template for Step 0-8 and Step 10 unless a more specific template applies.

## Step X: <title>

### 1. 本 Step 学习目标

- Explain what the user should understand after this step.
- State why this step matters for reading, reproducing, or modifying the project.

### 2. 证据来源

- Code: `<path>` -> `<class/function/config key>`
- Paper: `<section/page/formula>` or `当前材料中未看到证据`
- Runtime evidence: `<log/command/output>` or `当前材料中未看到证据`
- Unverified assumptions: list separately and do not present them as facts.

### 3. 参数定义

For each important parameter:

- Name:
- Location:
- Type / shape:
- Default:
- Meaning:
- Affects:
- Evidence:

### 4. 代码讲解

Explain by logical blocks, not line spam:

- Block:
- What it does:
- Why it exists:
- Paper connection:
- Important syntax:
- Edge cases:

### 5. 调用关系

- Upstream caller:
- Current module/function:
- Downstream calls:
- Training-time path:
- Inference-time path:
- Config or registry path:

### 6. 语法讲解

Explain non-obvious syntax only:

- PyTorch module behavior such as `nn.Module`, `forward`, buffers, hooks, `ModuleList`, `Sequential`.
- Tensor operations such as `view`, `reshape`, `permute`, `transpose`, `contiguous`, `cat`, `stack`, indexing, broadcasting.
- Python patterns such as decorators, inheritance, dataclasses, argparse, dynamic imports, registries, context managers.
- Config patterns such as YAML inheritance, override order, factory creation, or default merging.

### 7. 张量形状变化

Use a compact table.

| Stage | Code / Operation | Shape | Meaning |
| --- | --- | --- | --- |
| Input |  |  |  |
| Intermediate |  |  |  |
| Output |  |  |  |

If the exact shape depends on config or data, say what is known and what needs evidence.

### 8. 模块作用与模块关系

- Local role:
- Relationship to previous modules:
- Relationship to later modules:
- Relationship to paper architecture:
- What would break or change if this module were modified:

### 9. 数学 / 论文含义

- Formula or concept:
- Code implementation:
- Difference between paper and code:
- Intuition:
- Limitation:

### 10. 工程细节与调试

- Initialization:
- Device / dtype / AMP:
- Memory or speed concerns:
- Randomness / reproducibility:
- Common bugs:
- How to verify:

### 11. 研究生复盘问题

Ask 3-6 questions. Include at least:

- Why is this design used instead of an alternative?
- What changes if a key parameter/module is modified?
- Does the code exactly implement the paper?
- What evidence is still missing?

### 12. 用户问题记录

Record user questions from this step as:

- Q:
- A:
- Evidence:
- Whether it should appear in final notes:
