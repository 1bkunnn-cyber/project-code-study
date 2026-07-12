---
document_type: project-code-study-ledger
schema_version: "3.0"
project_name: "{{PROJECT_NAME}}"
project_path: "{{PROJECT_PATH_OR_URL}}"
branch: "{{BRANCH_OR_UNKNOWN}}"
commit: "{{COMMIT_OR_UNKNOWN}}"
created_at: "{{CREATED_AT}}"
updated_at: "{{UPDATED_AT}}"
current_step: "0"
study_mode: "new"
write_authorized: "yes"
---

<!--
PROJECT CODE STUDY LEDGER CONTRACT

1. This file is copied from assets/PROJECT_STUDY_LOG.template.md.
2. Keep schema_version, H2 section names, section order, table columns, ID prefixes, and status enums unchanged.
3. Update sections 1-13 in place. Keep section 14 as the final H2 and append session entries only there.
4. Do not delete empty sections. Use "待确认", "无", or "不适用（原因）" instead of inventing facts.
5. Record demonstrated learning separately from self-confidence.
6. Do not store hidden reasoning, secrets, credentials, full chat transcripts, or irrelevant personal details.
7. Prefer small patches. Preserve user edits and mark old claims stale instead of silently rewriting history.
-->

# {{PROJECT_NAME}} 源码学习记录

> 本文档是项目学习过程的工作记忆，用于恢复上下文、追踪真实理解、管理证据与误区，并决定下一次最值得学习的内容。它不是聊天转录，也不是最终学习笔记。

## 阅读导航

| 想了解什么 | 首先阅读 |
| --- | --- |
| 现在学到哪里 | 1. 当前状态 |
| 是否真正掌握 | 4. 掌握度地图 |
| 结论来自哪里 | 5. 证据索引 |
| 还有什么没解决 | 6. 开放事项 |
| 曾经理解错什么 | 7. 误区与纠正 |
| 下次复习什么 | 11. 复习队列 |
| 每次学习发生了什么 | 14. 会话日志 |

## 状态规范

| 对象 | 允许值 |
| --- | --- |
| Step | `planned` / `active` / `review` / `blocked` / `done` / `skipped` / `stale` |
| 掌握度 | `unseen` / `introduced` / `explainable` / `traceable` / `applied` / `verified` / `revisit` |
| 证据等级 | `E0` 无项目证据 / `E1` 直接源码或文档 / `E2` 多来源推断 / `E3` 运行或实验验证 |
| 置信度 | `high` / `medium` / `low` |
| 会话结果 | `advanced` / `reviewed` / `blocked` / `interrupted` / `finalized` |

---

## 1. 当前状态

> 这是每次恢复学习时的首要入口。保持简短、最新、可在 60 秒内读完。

| 字段 | 当前值 |
| --- | --- |
| 学习模式 | `new` |
| 目标结果 | `{{TARGET_OUTCOME}}` |
| 当前 Step | `0` |
| 本次时间预算 | `{{SESSION_BUDGET}}` |
| 上次有效学习 | `尚未开始` |
| 距上次学习 | `不适用` |
| 当前阻塞 | `待确认` |
| 现在到期的复习 | `无` |
| 最大学习风险 | `待确认` |
| AI 最没把握的重要判断 | `待确认` |
| 用户当前最关心的问题 | `{{USER_CURRENT_CONCERN}}` |

### 1.1 恢复摘要

<!-- 最多 8 条。只写当前仍有效的信息。 -->

- 项目解决的问题：待确认
- 主要执行入口：待确认
- 用户已经能独立解释：无
- 用户已经能完成源码或 Shape 追踪：无
- 当前仍模糊或错误的理解：待确认
- 缺失的关键证据：待确认
- 自上次会话以来的变化：首次创建
- 下一步：完成项目证据盘点

### 1.2 唯一主行动

| 下一行动 | 为什么现在价值最高 | 完成证据 | 状态 |
| --- | --- | --- | --- |
| 完成 Step 0 项目地图 | 建立后续源码学习的证据边界 | 能定位入口并口述主流程 | `active` |

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

## 3. 学习路线

> Step 完成必须有行为证据。不要用阅读次数或完成百分比代替理解。

| Step | 主题 | 状态 | 完成标准 | 当前行为证据 | 下一决策 |
| --- | --- | --- | --- | --- | --- |
| 0 | 项目地图与证据边界 | `active` | 能定位入口并描述主流程 | 待学习 | 继续 |
| 1 | 任务背景与论文问题 | `planned` | 能解释任务、动机和论文主张 | 待学习 | 待定 |
| 2 | 数据与预处理 | `planned` | 能追踪一个样本进入 Batch 的过程与 Shape | 待学习 | 待定 |
| 3 | 整体架构 | `planned` | 能重建模块图和主要接口 | 待学习 | 待定 |
| 4 | 核心模块源码 | `planned` | 能解释并追踪关键模块 | 待学习 | 待定 |
| 5 | 论文到代码映射 | `planned` | 能指出已验证的一致和差异 | 待学习 | 待定 |
| 6 | Loss、后处理与指标 | `planned` | 能连接公式、Tensor、代码和指标 | 待学习 | 待定 |
| 7 | 训练循环与配置 | `planned` | 能追踪一次迭代和配置解析 | 待学习 | 待定 |
| 8 | 推理、部署与复现 | `planned` | 能运行或准确描述已验证的复现路径 | 待学习 | 待定 |
| 9 | 全局审计与盲点 | `planned` | 已按价值排序重要盲点和不确定项 | 待学习 | 待定 |
| 10 | 研究生级综合复盘 | `planned` | 能批判、修改并设计有证据的实验 | 待学习 | 待定 |

### 3.1 路线调整记录

| 日期 | 调整 | 原因 | 用户确认 | 影响 |
| --- | --- | --- | --- | --- |

---

## 4. 掌握度地图

> 自信度记录主观感受；掌握度只依据解释、追踪、预测、调试、修改或实验表现更新。

| ID | 概念或能力 | 重要性 | 掌握度 | 行为证据 | 自信度 1-5 | 最近测试 | 下次复习 |
| --- | --- | --- | --- | --- | --- | --- | --- |

---

## 5. 证据索引

> 同一来源只登记一次，其他章节使用 `SRC-xxx` 引用。

| ID | 类型 | 定位 | 版本 / 页码 | 实际检查内容 | 支持对象 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |

说明：README 属于文档证据，不等于运行验证；搜索摘要仅用于发现来源，不能代替原始代码或论文。

---

## 6. 开放事项

> 每个未解决事项必须包含下一动作。当前最高价值事项同步到 1.2。

| ID | 类型 | 事项 | 是否阻塞 | 需要的证据 | 下一动作 | 目标 Step | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |

ID 类型：`Q-xxx` 用户问题、`U-xxx` AI 不确定项、`R-xxx` 复现风险。

---

## 7. 误区与纠正

> 解释过不等于纠正完成。必须在后续用不同形式重测。

| ID | 观察到的误解 | 如何发现 | 正确模型 | 证据 | 重测问题 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |

状态：`observed` / `corrected` / `retest-due` / `resolved`。

---

## 8. 用户问题

> 保留真实意图，压缩表达，不复制完整对话。

| ID | Step | 问题 | 简短回答 | 证据 ID | 是否改变旧理解 | 最终笔记 |
| --- | --- | --- | --- | --- | --- | --- |

---

## 9. 实验、命令与失败尝试

> 只记录具有学习、验证、复现或防止重复失败价值的操作。

| ID | 日期 | 假设 / 目的 | 命令或改动 | 结果 | 证据产物 | 解释 | 下一动作 |
| --- | --- | --- | --- | --- | --- | --- | --- |

结果：`not-run` / `pass` / `fail` / `partial`。失败记录不得改写为成功。

---

## 10. 论文、代码与来源冲突

| ID | 主张 | 来源 A | 来源 B | 当前判断 | 置信度 | 验证动作 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |

状态：`open` / `resolved` / `accepted-ambiguity`。

---

## 11. 复习队列

| 到期时间 | 知识 ID | 到期原因 | 复习形式 | 结果 | 重新安排 |
| --- | --- | --- | --- | --- | --- |

复习形式：`explain` / `trace` / `predict` / `debug` / `modify`。

---

## 12. 维护状态

| 项目 | 当前值 |
| --- | --- |
| 最近一次重复 / 过期检查 | `尚未执行` |
| 仍被引用的已关闭事项 | `无` |
| 建议归档 | `no` |
| 用户授权归档 | `no` |
| 归档路径 | `PROJECT_STUDY_LOG_ARCHIVE.md` |
| 可进入最终总结的材料 | `无` |
| 明确不进入最终总结的材料 | `无` |

---

## 13. 里程碑总结

> 只在完成一个有意义的学习阶段后新增，不要在每次回答后生成。

<!--
### Milestone <名称 / Step 范围>

- 稳定理解：
- 关键证据 ID：
- 已掌握的调用 / Shape 路径：
- 论文与代码关系：
- 用户心智模型的变化：
- 剩余开放事项 ID：
- 可复用的最终笔记材料：
-->

---

## 14. 会话日志

> 本节必须是文件最后一个 H2。每次有效学习只在文件末尾追加一条记录；阻塞或中断也要如实记录。

<!--
### Session <N> — <YYYY-MM-DD>

| 项目 | 内容 |
| --- | --- |
| 模式与时长 | quick / standard / deep，<minutes> |
| 检查的仓库版本 |  |
| 用户本次目标 |  |
| 新内容前的复习 |  |
| 检查的来源 | SRC-... |
| 完成的学习 |  |
| 用户行为证据 | 能解释 / 追踪 / 预测 / 应用 / 未能回忆的内容 |
| 观察或重测的误区 | M-... |
| 新增或回答的问题 | Q-... |
| 尝试的实验 | EXP-... |
| 状态变化 | Step 和掌握度变化 |
| 会话结果 | advanced / reviewed / blocked / interrupted / finalized |
| 唯一下一行动 |  |
| 建议返回时间 |  |
-->
