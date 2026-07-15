---
document_type: project-code-study-ledger
schema_version: "4.0"
project_name: "{{PROJECT_NAME}}"
project_path: "{{PROJECT_PATH_OR_URL}}"
qa_path: "PROJECT_STUDY_QA.md"
branch: "{{BRANCH_OR_UNKNOWN}}"
commit: "{{COMMIT_OR_UNKNOWN}}"
created_at: "{{CREATED_AT}}"
updated_at: "{{UPDATED_AT}}"
current_step: "0"
current_micro_step: "0.1"
current_scenario: "map"
current_node: "待确认"
study_mode: "new"
write_authorized: "yes"
---

<!--
PROJECT CODE STUDY LEDGER CONTRACT — schema 4.0

1. This file stores compact state, route, evidence, mastery, corrections, experiments, reviews, milestones, and sessions.
2. Detailed questions, answers, learner reflections, and feedback belong in PROJECT_STUDY_QA.md; keep compact IDs here.
3. Preserve heading order, table columns, stable IDs, user content, and stale/correction history.
4. Prefer small patches. Never store full conversations, hidden reasoning, credentials, or irrelevant private data.
5. A write is successful only after changed rows are read back.
-->

# {{PROJECT_NAME}} 源码学习记录

> 用于恢复主线、追踪真实理解、维护动态调用路线和管理证据。它不是聊天转录，也不是最终学习笔记。

## 阅读导航

| 想了解什么 | 首先阅读 |
| --- | --- |
| 当前学到哪里、如何继续 | 1. 当前状态与主线锚点 |
| 建议学习顺序和调用链 | 3. 动态学习路线 |
| 每个微 Step 学到了什么 | 4. Step 知识卡与掌握度 |
| 结论依据 | 5. 证据索引 |
| 未解决事项和修正 | 6–7 |
| 用户问答 | 8. 问题索引，再按 Q-ID 查看 `PROJECT_STUDY_QA.md` |
| 实验、对比和创新延伸 | 9–10 |
| 复习、里程碑和会话 | 11–14 |

## 状态规范

| 对象 | 允许值 |
| --- | --- |
| Step / 微 Step | `planned` / `active` / `blocked-prerequisite` / `review` / `done` / `skipped` / `stale` |
| 节点 | `discovered` / `queued` / `active` / `traced` / `deferred` / `out-of-scope` / `stale` |
| 掌握度 | `unseen` / `introduced` / `explainable` / `traceable` / `applied` / `verified` / `revisit` |
| 证据等级 | `E0` / `E1` / `E2` / `E3` |
| 置信度 | `high` / `medium` / `low` |
| 问题 | `open` / `answered` / `retest-due` / `closed` / `stale` |
| 会话结果 | `advanced` / `reviewed` / `blocked` / `interrupted` / `finalized` |

---

## 1. 当前状态与主线锚点

> 保持在 60 秒内可读完。支线问题不得悄悄改变“继续位置”。

| 字段 | 当前值 |
| --- | --- |
| 学习模式 | `new` |
| 目标结果 | `{{TARGET_OUTCOME}}` |
| 当前场景 | `map` |
| 当前 Step / 微 Step | `0 / 0.1` |
| 当前节点 | `待确认` |
| 已完成主链节点 | `无` |
| 当前支线问题 | `无` |
| 精确继续位置 | `完成项目证据盘点` |
| 当前阻塞 / 前置缺口 | `待确认` |
| 到期复习 | `无` |
| 用户当前最关心的问题 | `{{USER_CURRENT_CONCERN}}` |

### 1.1 恢复摘要

<!-- 最多 8 条，只保留当前仍有效的信息。 -->

- 项目问题与主要输出：待确认
- 已确认入口 / 场景：待确认
- 已理解的关键节点：无
- 已能独立追踪的调用 / Shape：无
- 当前模糊或错误的理解：待确认
- 缺失的关键证据：待确认
- 最近一次重要变化：首次创建
- 精确继续位置：完成项目证据盘点

### 1.2 唯一主行动

| 下一行动 | 为什么现在价值最高 | 完成证据 | 状态 |
| --- | --- | --- | --- |
| 完成 Step 0 项目地图 | 建立证据和运行场景边界 | 能定位代表性入口 | `active` |

---

## 2. 学习契约

| 项目 | 内容 |
| --- | --- |
| 学习者背景 | `{{LEARNER_BACKGROUND}}` |
| 已掌握前置知识 | `{{PREREQUISITES}}` |
| 学习动机 | `{{MOTIVATION}}` |
| 成功证明 | `{{SUCCESS_DELIVERABLE}}` |
| 单次 / 总时间 | `{{AVAILABLE_TIME}}` |
| 期望讲解方式 | `{{EXPLANATION_STYLE}}` |
| 允许运行实验 | `{{RUNTIME_PERMISSION}}` |
| 允许联网或论文检索 | `{{NETWORK_PERMISSION}}` |
| 允许修改项目源码 | `{{CODE_MODIFICATION_PERMISSION}}` |
| 明确不学的范围 | `{{OUT_OF_SCOPE}}` |

---

## 3. 动态学习路线

> Step 3 先建立场景调用图；Step 4.x 根据源码动态生成。不要预设项目一定包含 Backbone、Transformer 或固定数量的核心模块。

### 3.1 路线骨架

| Step | 主题 | 状态 | 完成标准 | 当前行为证据 | 下一决策 |
| --- | --- | --- | --- | --- | --- |
| 0 | 项目地图与证据边界 | `active` | 能定位代表性入口和证据范围 | 待学习 | 继续 |
| 1 | 任务背景、相关方法与问题定义 | `planned` | 能解释任务、动机及至少一个有效对比 | 待学习 | 待定 |
| 2 | 代表性输入与数据路径 | `planned` | 能追踪一个输入进入主执行路径 | 待学习 | 待定 |
| 3 | 运行场景、调用图与概念依赖 | `planned` | 形成训练/推理等场景的节点顺序 | 待学习 | 待定 |
| 4.x | 动态源码微 Step | `planned` | 逐节点通过定位、调用和数据边界验证 | 待生成 | 由 Step 3 生成 |
| 5 | 完整架构重建与论文代码映射 | `planned` | 能从已学节点重建系统 | 待学习 | 待定 |
| 6+ | 目标函数、训练、推理、评估与复现 | `planned` | 按项目目标生成完成标准 | 待生成 | 动态调整 |
| 9 | 全局覆盖与盲点审计 | `planned` | 核心节点、依赖和问题缺口已审计 | 待学习 | 待定 |
| 10 | 综合复盘与研究延伸 | `planned` | 能提出有证据的批判与实验 | 待学习 | 待定 |

### 3.2 运行场景

| Scenario ID | 场景 | 入口 / 命令 | 目标输出 | 静态或运行验证 | 状态 |
| --- | --- | --- | --- | --- | --- |

### 3.3 调用节点与微 Step 顺序

| 顺序 | 场景 | 微 Step | Node ID | 调用者 | 当前类 / 函数 | 下游节点 | 输入 / 输出 | 前置依赖 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### 3.4 路线调整记录

| 日期 | 调整 | 原因 / 证据 | 用户确认 | 影响 |
| --- | --- | --- | --- | --- |

---

## 4. Step 知识卡与掌握度

### 4.1 Step / 微 Step 知识卡

| Step | Node ID | 核心结论 | 调用 / Shape 边界 | 证据 ID | 修正 ID | 状态 |
| --- | --- | --- | --- | --- | --- | --- |

### 4.2 掌握度地图

| ID | 概念或能力 | 重要性 | 掌握度 | 行为证据 | 自信度 1-5 | 最近测试 | 下次复习 |
| --- | --- | --- | --- | --- | --- | --- | --- |

---

## 5. 证据索引

| ID | 类型 | 定位 | 版本 / 页码 | 实际检查内容 | 支持对象 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |

说明：发现文件不等于阅读文件，README 主张不等于运行验证，搜索摘要不能代替原始来源。

---

## 6. 开放事项

| ID | 类型 | 事项 | 是否阻塞 | 需要的证据 | 下一动作 | 目标 Step / Node | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |

---

## 7. 误区、纠正与规范表述

| ID | 原表述 / 误解 | 问题 | 规范修正表述 | 证据 | 影响范围 | 重测问题 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |

旧表述需标记 `stale`；最终文档只使用仍有效的规范表述。

---

## 8. 问题索引

> 完整问题和回答在 `PROJECT_STUDY_QA.md`。这里保留导航和学习影响。

| Q ID | Step / Node | 问题摘要 | Parent Q | 状态 | 是否阻塞 | 修正 / 证据 ID | 下一动作 |
| --- | --- | --- | --- | --- | --- | --- | --- |

---

## 9. 实验、命令与失败尝试

| ID | 日期 | 假设 / 目的 | 命令或改动 | 结果 | 证据产物 | 解释 | 下一动作 |
| --- | --- | --- | --- | --- | --- | --- | --- |

结果：`not-run` / `pass` / `fail` / `partial`。失败不得改写为成功。

---

## 10. 来源冲突、相关方法与组合延伸

### 10.1 论文、代码与来源冲突

| ID | 主张 | 来源 A | 来源 B | 当前规范判断 | 置信度 | 验证动作 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |

### 10.2 相关方法与模块组合

| CMP ID | 层级 | 对比 / 模块 | 共享问题或思想 | 关键差异 / 不兼容 | 可验证假设 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |

层级：`same-task` / `same-bottleneck` / `analogous-idea` / `composable-module`。

---

## 11. 复习队列

| 到期时间 | 知识 / 问题 ID | 到期原因 | 复习形式 | 结果 | 重新安排 |
| --- | --- | --- | --- | --- | --- |

复习形式：`explain` / `trace` / `predict` / `debug` / `modify`。

---

## 12. 维护状态

| 项目 | 当前值 |
| --- | --- |
| 最近一次写入回读验证 | `尚未执行` |
| 最近一次重复 / 过期检查 | `尚未执行` |
| Q&A 路径 | `PROJECT_STUDY_QA.md` |
| 建议归档 | `no` |
| 用户授权归档 | `no` |
| 可进入最终总结的材料 | `无` |
| 明确不进入最终总结的材料 | `无` |

---

## 13. 里程碑总结

<!-- 仅在有意义的阶段完成后新增。 -->

---

## 14. 会话日志

| Session ID | 日期 | Step / Node | 模式 / 时长 | 本次目标 | 学习与问题 IDs | 行为证据 | 状态变化 | 会话结果 | 唯一下一行动 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

---

## 15. 用户心得摘要

> 用户原文在 `PROJECT_STUDY_QA.md`。这里只保留 ID、学习信号和 AI 调整。

| NOTE ID | 日期 | Step / Node | 学习信号摘要 | AI 调整 | 状态 |
| --- | --- | --- | --- | --- | --- |

---

## 16. 用户反馈摘要

| FB ID | 日期 | Step / Node | 类型 | 反馈摘要 | 评分 1-5 | AI 调整与下一行动 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
