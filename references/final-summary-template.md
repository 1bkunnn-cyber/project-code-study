# Compact / Legacy Markdown Summary Template

This template is not the consent-gated final learning document and must never be labelled `complete` or `validated`. Formal finalization belongs to `skills/project-study-document` after a passing readiness manifest.

Use the linked `PROJECT_STUDY_LOG.md` and `PROJECT_STUDY_QA.md` as primary memory, then verify important claims against source/paper/runtime evidence.

Before writing:

1. resolve `SRC-`, `Q-`, `M-`, `C-`, `EXP-`, and `CMP-` references;
2. use canonical corrected wording and exclude known stale statements;
3. distinguish demonstrated mastery from exposure;
4. audit scenario/node coverage and missing prerequisites;
5. state unsaved or unavailable evidence.

# <Project Name> 源码学习笔记

## 1. 项目与证据范围

- Goal, revision, entrypoints, scenarios, evidence inspected, and missing evidence.

## 2. 任务、论文与相关方法

- Problem formulation, design motivation, key paper claims, and bounded comparisons.

## 3. 动态学习路线与掌握证据

| Step / micro Step | Scenario / Node | Status | Demonstrated evidence | Key takeaway |
| --- | --- | --- | --- | --- |

## 4. 运行时调用图

- Training/inference/evaluation paths, shared nodes, branches, and exact source symbols.
- Prefer a short linear chain, a mapping table, or Mermaid labelled with RUN/NODE IDs. Use ASCII only for a very short alignment-stable sketch.

## 5. 核心节点源码精读

For each important node: caller, source, inputs/outputs, shapes, logic, design role, downstream use, and risks.

## 6. 完整架构重建

- Reconstruct the system only from traced nodes; identify training-only and inference-only components.

## 7. 数据、目标函数、训练、推理与评估

- Representative data path, objectives/assignment/loss, optimization/config, post-processing, metrics, and reproduction evidence.

## 8. 论文—代码映射

| Paper concept | Paper evidence | Code evidence | Status | Reproduction impact |
| --- | --- | --- | --- | --- |

## 9. 用户问答与规范修正

- Include high-value Q&A from the Q&A file and a correction table.

| Correction ID | Original issue | Canonical wording | Evidence | Affected conclusions |
| --- | --- | --- | --- | --- |

## 10. 相关模型、相似思想与模块组合

- Same-task, same-bottleneck, analogous-idea, and composable-module findings; distinguish integration from innovation.

## 11. 实验、失败、调试与复现清单

- Preserve failed attempts and unresolved risks.

## 12. 全局盲点与未解决事项

- Missing nodes, unmet dependencies, uncertainties, stale claims, metric traps, and evidence actions.

## 13. 后续路线

- Reviews, experiments, ablations, modifications, papers, and one highest-value next action.

## 14. 主动回忆题

Create questions from demonstrated weak points and unresolved transfers, not generic trivia.
