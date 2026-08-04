# Project Code Study v6 机制设计

## 目标

把 `project-code-study` 从“依赖模型遵守提示词的学习记录协议”升级为“本地、零基础设施、可恢复、可审计的项目学习发布系统”。最终产物必须是能脱离聊天独立学习源码的手册，而不是 Step 摘要索引。

## 设计边界

- 保持本地文件为事实来源，不引入数据库、向量服务或云记忆。
- 不自动保存原始聊天；只保存经过分类、授权和去重的 durable memory。
- 不修改被学习项目源码或既有学习记录；真实样本只用于只读审计。
- 控制脚本不能假装拥有宿主没有提供的 hook。宿主未执行控制入口时，系统只能报告 `advisory/not-run`，不能声称 `saved`、`validated` 或 `complete`。
- 保留 v5.5 的真实调用链、单 NODE、continuation、pending intents、fresh continue、retest、唯一 ID、correction、consent、draft isolation、readiness repair、research copy isolation 和证据边界。

## 架构

### 1. 事件与状态

每条用户输入先形成不可复用的 `input_event_id`。intent splitter 输出有序 intent：

```text
INPUT_RECEIVED
→ INTENTS_ALLOCATED
→ RESPONSE_STAGED
→ ARTIFACTS_STAGED
→ VALIDATING
→ COLD_START
→ COMMITTED
```

任一状态、hash、handoff 或 validator 不一致都进入 `REPAIR_REQUIRED`。`continue` 必须绑定当前 input event；消费后写入 `consumed_continue_event_ids`，不能跨问题或跨 handoff 重放。

### 2. 统一发布事务

事务使用发布 WAL 和最终 commit marker，而不虚称多文件操作系统级原子性：

1. QA/LOG、memory 和 document 先各自通过既有原子写入入口落盘。
2. 对同一落盘版本运行 QA、LOG、memory、document 和 cold-start 检查。
3. 计算四类产物 hash，写 `PREPARED` journal。
4. commit 前重新计算 hash；任一漂移把 WAL 标为 `ABORTED`。
5. 全部一致后写 `COMMITTED` receipt，再将 WAL 标记为 committed。
6. 崩溃恢复以 receipt hash 和 prepared hash 对账；没有 commit marker 时禁止成功 claim。

只有 `COMMITTED` receipt 能授权持久化和正式文档 claim。receipt 形成 hash chain。

### 3. QA 深度合同

validator 不再使用统一字符数阈值：

- `concept`：定义、项目语境、类比、反例、相邻概念区别、自测。
- `code`：真实 fenced snippet、精确行号、逐行解释、输入输出、调用者、返回值、最小例子。
- `shape`：输入 Shape、每层公式、通道来源、分支合并、输出验证。
- `metric`：TP/FP/FN、公式、来源、阈值、项目字段、评判标准、误区。
- `review`：覆盖矩阵、遗漏、证据等级、下一动作。
- `correction`：原结论、规范结论、影响范围、传播检查、回归测试。

`runtime`、`paper`、`visual` 等旧类型映射到上述合同或组合合同，避免破坏已有记录读取能力。

### 4. 长期 memory 与 handoff

memory 生命周期为：

```text
candidate → approved → saved
          ↘ rejected
saved → stale
```

触发器只产生 candidate：

- 明确长期教学偏好；
- correction；
- 对输出、文档或路线的 durable 质量反馈；
- Step 完成后的 durable learning rule；
- 压缩前 handoff。

普通一次性问题不触发。拒绝记录只保留 ID、状态、hash 和原因，不保留被拒绝的原始聊天。handoff 包含主线锚点、完成 NODE、未完成问题、pending intents、retest、最近 correction、证据、artifact hash 和唯一下一行动。

### 5. 最终学习手册

每个完成 Step 对应一个独立教材章节，并具备 20 项强制内容。源码引用使用：

```text
release-bound repository revision + relative path + start/end line + exact fenced excerpt
```

validator 校验 excerpt 与指定 repo root 的源码行段一致，release receipt 再绑定 repository revision；禁止“详见聊天”“同上”和循环引用。重要 QA 必须被吸收为正文，而不是只留下索引。

专项 profile：

- Step 4.x：`_do_train()`、`model(batch)`、`DetectionModel.forward()`、`v8DetectionLoss`、AMP、梯度累积、EMA、optimizer、epoch 收尾、验证与保存；完整 `[8,3,640,640]` YOLOv8n Shape；Conv/C2f/SPPF/Upsample/Concat/Detect；`parse_model()`。
- Step 6：TP/FP/FN、IoU、AP、mAP、`results.csv`、可视化、评估源码。
- Step 10：缝合、SE、baseline、消融、公平对照与创新验证。

### 6. 冷启动

冷启动分两层：

- deterministic contract：章节、源码、练习、答案、证据和 QA 覆盖的机器检查；
- real-host evaluation：新模型只读正式候选文档回答抽样解释和练习，结果写独立 report。

`static-pass` 不等于 `host-pass`。需要真实 cold-start 的发布若没有 host report，必须保持 `not-run/blocked`。

### 7. 宿主边界

启动时生成 capability manifest：

- `transaction_entrypoint`
- `pre_response_hook`
- `cold_start_host`
- `real_compaction_hook`

缺失能力必须进入 `advisory` 或 `not-run`。response claim guard 校验 exact response hash、claim 类型和对应 `COMMITTED` receipt。

## 致谢与参考项目

本设计感谢并参考以下真实项目的公开思想；本仓库不复制其代码或协议文本：

- [Engramory](https://github.com/tinqiao-oss/engramory)：小型、typed、可审计的 Markdown memory 与 bounded index。
- [Mem0](https://github.com/mem0ai/mem0)：memory 生命周期、历史和多层记忆。
- [Letta / MemGPT](https://github.com/letta-ai/letta)：working/core memory 与持久状态。
- [Zep Graphiti](https://github.com/getzep/graphiti)：temporal validity、episode provenance 和 stale history。
- [LangGraph](https://github.com/langchain-ai/langgraph)：checkpoint、interrupt、durable resume。
- [OpenHands](https://github.com/OpenHands/OpenHands)：持久事件、create-or-resume 和版本固定。
- [SWE-agent](https://github.com/SWE-agent/SWE-agent)：可复现 trajectory 与执行/评估分离。
- [Aider](https://github.com/Aider-AI/aider)：revision-aware repository map。
- [learn-codebase](https://github.com/ktaletsk/learn-codebase)：苏格拉底提问、prediction、active recall 与学习日志。
- [PocketFlow Tutorial Codebase Knowledge](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge)：从核心抽象和交互生成初学者教程。
- [RepoAgent](https://github.com/OpenBMB/RepoAgent)：AST、调用关系和增量文档。
- [CodeTour](https://github.com/microsoft/codetour)：文件/行号锚定的可重放学习路线。
- [DeepWiki-Open](https://github.com/AsyncFuncAI/deepwiki-open)：可导航知识结构。
- [MathTutorBench](https://github.com/eth-lre/mathtutorbench) 与 [EducationQ](https://arxiv.org/abs/2504.14928)：teacher-grounded rubric 和多轮教学评估。

明确不采用：云记忆、默认向量数据库、自动保存全部聊天、无来源的 RAG 结论、依赖多 Agent 的主状态机，以及不能覆盖 Bash/MCP/外部编辑器却宣称全局强制的 hook。

## 验收

- 新 v6 gold fixture 必须通过全部 strict publication checks。
- 当前行人检测样本保持不变，并应被新 document publication validator 拒绝，理由至少包括真实 cold-start `not-run`、UNIT 教材深度不足和关键 QA 未吸收。
- 所有失败路径不得产生 `COMMITTED` receipt 或允许正式 claim。
- 真实 Claude/Codex、真实压缩、多模型和 pre-response hook 分别报告，不互相替代。
