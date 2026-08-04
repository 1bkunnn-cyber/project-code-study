# GitHub 调研、采用决策与致谢

审计日期：2026-08-04。仓库存在性、`archived`、`pushed_at` 和 GitHub
检测到的 SPDX 许可证通过 GitHub 官方仓库/API 复核。活跃度只描述审计日
观察：高＝近 30 天有 push；中＝近 180 天有 push；低＝超过 180 天无 push。
许可证为 `未检测到` 时不推定可复制。本 Skill 只独立实现公开思想，没有复制
下列项目的源代码、提示词或协议文本。

## 调研表

| 项目 | 核心思想与实现方式 | 许可证 | 活跃度 | 对本 Skill 的结论 |
| --- | --- | --- | --- | --- |
| [Engramory](https://github.com/tinqiao-oss/engramory) | typed Markdown memory、bounded index、单事实文件、doctor | MIT | 高；未归档 | **可直接借鉴机制思想**：采用 bounded 本地索引、typed candidate 和 doctor；致谢。 |
| [Mem0](https://github.com/mem0ai/mem0) | 多层 memory、add/update/delete/history 生命周期，常配向量检索 | Apache-2.0 | 高；未归档 | **只借鉴生命周期**；不引入云服务、向量库或自动保存聊天。 |
| [Letta / MemGPT](https://github.com/letta-ai/letta) | core/working/archival memory 与持久 agent state | Apache-2.0 | 高；未归档 | **只借鉴 working/durable 分层**；完整 server/runtime 不适合零依赖 Skill。 |
| [Zep Graphiti](https://github.com/getzep/graphiti) | episode provenance、时序有效性、失效边、图检索 | Apache-2.0 | 高；未归档 | **只借鉴 provenance/stale 思想**；图数据库与自动抽取不采用。 |
| [LangGraph](https://github.com/langchain-ai/langgraph) | checkpoint、interrupt、durable resume、显式 graph state | MIT | 高；未归档 | **可直接借鉴机制思想**：显式状态、handoff、hash drift→repair；不引入框架依赖。 |
| [OpenHands](https://github.com/OpenHands/OpenHands) | 事件流、session create/resume、运行版本和执行结果分离 | MIT | 高；未归档 | **只借鉴事件/恢复思想**；sandbox/runtime 不嵌入 Skill。 |
| [SWE-agent](https://github.com/SWE-agent/SWE-agent) | 可复现 trajectory、环境执行与评分分离 | MIT | 高；未归档 | **只借鉴 evaluation separation**；不采用其 agent runtime。 |
| [Aider](https://github.com/Aider-AI/aider) | revision-aware repo map、git diff/commit 驱动的源码上下文 | Apache-2.0 | 中；未归档 | **只借鉴 revision/source lock**；不复制 repo-map 算法。 |
| [AutoGen](https://github.com/microsoft/autogen) | agent/message/runtime state 与多 Agent 编排 | CC-BY-4.0 | 中；未归档 | **不适合作为依赖**：多 Agent runtime 扩大状态面，和本地单主线 fail-closed 冲突。 |
| [CrewAI](https://github.com/crewAIInc/crewAI) | flow/crew state、任务编排、持久 execution | MIT | 高；未归档 | **不适合作为依赖**：角色编排不能替代唯一权威状态与 receipt。 |
| [learn-codebase](https://github.com/ktaletsk/learn-codebase) | 苏格拉底提问、prediction、active recall、学习日志 | MIT | 中；未归档 | **可直接借鉴教学思想**：采用回忆、评价、retest；致谢。 |
| [PocketFlow Tutorial Codebase Knowledge](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge) | 从核心抽象、关系与调用流生成初学者教程 | MIT | 中；未归档 | **可直接借鉴文档思想**：教材按调用依赖组织；生成器/runtime 不引入。 |
| [RepoAgent](https://github.com/OpenBMB/RepoAgent) | AST/调用关系、仓库级文档、增量更新 | Apache-2.0 | 低；未归档 | **只借鉴 source-grounded/incremental 思想**；AST 全量生成超出通用 Skill 边界。 |
| [CodeTour](https://github.com/microsoft/codetour) | 文件/行号锚点组成可重放源码路线 | MIT | 中；未归档 | **可直接借鉴机制思想**：路径+精确行段+snippet 校验；不复制 tour schema。 |
| [DeepWiki-Open](https://github.com/AsyncFuncAI/deepwiki-open) | 仓库知识库、结构导航、关系图 | MIT | 高；未归档 | **只借鉴可导航知识结构**；云检索和自动 wiki 不能证明教学深度。 |
| [MathTutorBench](https://github.com/eth-lre/mathtutorbench) | 教学能力任务、teacher-grounded scoring、错误定位与 scaffolding | 未检测到 | 高；未归档 | **只借鉴 rubric/evaluation 思想**；无明确许可证，不复制代码或数据。 |
| [EducationQ](https://arxiv.org/abs/2504.14928) | 教育型对话质量维度与评估 | 论文，以出版条款为准 | 论文 | **只借鉴评估维度**；不导入数据或量表原文。 |

## 实际采用

1. Engramory 的 bounded/typed 本地记忆，重做为
   `candidate/approved/saved/rejected/stale`，拒绝内容脱敏。
2. LangGraph/OpenHands 的 checkpoint、event、resume 思想，重做为不可重放
   input event、完整 handoff 和 `REPAIR_REQUIRED`。
3. SWE-agent 的执行与评估分离，重做为 static validator、real-host、
   real-compaction 和 multi-model 四类独立结果。
4. CodeTour/Aider/RepoAgent 的 revision/path/call relation 思想，重做为锁定
   revision、精确行段和源码片段一致性校验。
5. learn-codebase、PocketFlow 教程和 MathTutorBench 的教学思想，重做为
   NODE 短合同、分类型 QA 深度合同、逐 Step 教材章节和冷启动练习。

## 明确拒绝

- 不引入默认向量数据库、图数据库、云 memory 或外部账号。
- 不保存完整聊天，不把一次性问题自动写入长期 memory。
- 不让多 Agent runtime 成为权威状态机。
- 不把自动生成的 wiki、摘要、repository map 当作源码证据或学习完成证明。
- 不采用会削弱证据等级、用户 consent、fail-closed、research 副本隔离或
  隐私边界的外部方案。

感谢上述维护者、研究者和贡献者公开这些项目与思想。本仓库与它们无隶属、
赞助或背书关系；第三方权利和许可证归各自权利人所有。
