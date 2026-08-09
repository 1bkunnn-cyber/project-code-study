# Project Code Study v6.2 标准交互与多问题事务设计

日期：2026-08-09
状态：待用户审阅
目标版本：6.2.0

## 1. 设计结论

v6.2 不再把 `references/user-prompts.md` 当作 19 个需要用户选择和复制的
操作模板。正式交互收敛为一个学习循环、一条启动提示词、六种内部意图模式和
按模式变化的响应合同：

```text
定位 → 学习 → 检验 → 沉淀 → 等待
```

用户只表达目标、问题、回答或继续意图。Skill 负责把自然语言规范化为内部
事件，控制脚本负责 ID、状态、事务和门禁。用户可以一次提出任意数量的问题；
每个实质问题必须在回答前完成 intake 登记，并在回答后通过独立 QA/LOG 事务
保存完整规范答案。

## 2. 当前基线问题

只读审计得到以下事实：

- `references/user-prompts.md` 有 19 个编号入口、23 个提示词代码块，约
  5,887 个字符；它要求用户先理解 Skill 内部流程才能选择模板。
- 用户提示词重复 `preflight`、receipt、retest、状态枚举和记录责任，和
  `SKILL.md` 职责重叠。
- `assets/NODE_TEACHING_CONTRACT.md` 对所有 NODE 强制同一八段结构；
  `validate_teaching_response.py` 还对非 tensor NODE 强制具体 Shape。
- `study_events.split_intents()` 主要按换行和分号拆分，不能验证复杂自然语言中
  所有问题是否得到覆盖。
- `project_study_transaction.commit_question()` 一次只能写一个问题，没有批量
  intake、可恢复问题队列或批次结算状态。
- 现有用户提示词测试主要检查关键词、标题和代码块数量，没有验证自然语言路由、
  多问题登记、逐题持久化和模式化响应。

## 3. 外部项目对比与采用边界

| 来源 | 可借鉴思想 | v6.2 采用方式 | 不采用内容 |
| --- | --- | --- | --- |
| [learn-codebase](https://github.com/ktaletsk/learn-codebase) | 一次启用，之后自然对话；主动回忆和学习日志 | 用户入口保持极短，教学过程由 Skill 主动驱动 | 不采用其较弱的事务和证据边界 |
| [GitHub Copilot customization](https://docs.github.com/en/copilot/reference/customization-cheat-sheet) | persistent instructions、prompt files、skills、hooks 职责分离 | Prompt 只表达一次性意图；Skill 保存工作流；脚本/hook 执行硬门禁 | 不依赖任一 IDE 专属 prompt/handoff 格式 |
| [Claude Code Skills](https://code.claude.com/docs/en/slash-commands) | 自动或显式触发；Skill 内容持续生效；按需加载支持资源 | 一条显式启动方式加自然语言自动路由；核心协议保持短且长期有效 | 不把 Claude 专属 invocation 字段当作跨宿主保证 |
| [Anthropic skill-creator](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/skill-creator/skills/skill-creator/SKILL.md) | metadata → SKILL.md → reference 的渐进披露 | SKILL.md 保存稳定循环；模式合同和诊断细节按需加载 | 不把所有模式继续堆在主 SKILL.md |
| [Superpowers](https://github.com/obra/superpowers) | 阶段触发、硬门禁、设计/执行/验证分离 | 每个内部模式有明确进入条件和唯一合法退出 | 不引入与教学无关的开发流程 |
| [Awesome Copilot](https://github.com/github/awesome-copilot/blob/main/instructions/agents.instructions.md) | action-oriented handoff、少量相关下一步、最小上下文 | 正常输出只显示一个唯一下一动作；诊断时才展开内部状态 | 不依赖 VS Code handoff 按钮 |

只独立实现公开的结构思想，不复制上述项目的提示词、代码或协议文本。许可证、
活跃度和既有采用判断继续记录在 `GITHUB_RESEARCH_AND_ACKNOWLEDGEMENTS.md`。

## 4. 目标与非目标

### 4.1 目标

1. 用户不查模板也能稳定进入正确学习流程。
2. 所有输入都规范化为可验证、不可重放的 intent envelope。
3. 单条消息中的 0..N 个问题全部保留原始顺序和来源片段。
4. 每个实质问题都有唯一 Q-ID、QA intake、完整答案、独立 answer TX 和状态。
5. 任一未登记、未回答、未保存或 retest-due 的问题阻断主线推进。
6. 不同响应模式使用不同正向合同，避免统一八段模板造成机械扩写。
7. 正常教学隐藏事务噪声，但不隐藏失败、not-run 或证据边界。
8. 保留 v6.1 的状态机、memory、correction、readiness、receipt 和文档门禁。

### 4.2 非目标

- 不增加向量库、数据库、模型 SDK 或云服务。
- 不把任意聊天文本自动保存为长期 memory。
- 不把自然语言分类结果当成已持久化事实。
- 不承诺在单个模型响应中完整回答无限数量的问题。
- 不让提示词代替 allocator、validator、receipt 或宿主 hook。
- 不引入宿主专属 slash command、handoff 按钮或 UI 作为唯一入口。

## 5. 四层协同架构

```text
L1 用户意图层
   自然语言或一条标准启动提示词
        ↓
L2 意图规范化层
   INPUT event → ordered intents → validated envelope
        ↓
L3 协议执行层
   interaction state + question queue + QA/LOG/memory transactions
        ↓
L4 响应呈现层
   mode-specific body + compact status strip + one next action
```

职责边界：

| 层 | 负责 | 不负责 |
| --- | --- | --- |
| 用户输入 | 目标、问题、学习反馈、回答、继续或结束意图 | Q/TX 分配、状态枚举、receipt |
| 意图规范化 | 拆分、分类、顺序、source span、是否请求推进 | 回答内容、持久化成功声明 |
| 协议执行 | 状态转移、问题登记/回答事务、retest、恢复 | 教学表现形式 |
| 响应呈现 | 当前模式所需的学习内容和诚实状态 | 改写权威状态 |

## 6. 标准内部模式

| Mode | 典型输入 | 主要行为 | 合法退出 |
| --- | --- | --- | --- |
| `START` | “带我学习这个项目” | 建立合同、证据边界、路线和 Step 0 | 等待问题或新的继续 |
| `LEARN` | “继续”“讲当前 loss” | 只教学一个 NODE | recall 或等待 |
| `ASK` | 一个或多个问题 | 登记全部问题，逐题回答和保存 | 原 recall/等待/最终问题状态 |
| `ASSESS` | 用户的回忆题或 retest 回答 | 评价、完整答案、必要时新 retest | 等待；不得同轮推进 |
| `RECOVER` | “接着上次学” | 验证 handoff/LOG/QA/hash，恢复唯一位置 | 原记录状态或 repair |
| `CLOSE` | 暂停、问题关闭、生成手册 | 同步、readiness、consent 或 publication | paused/repair/consent |
| `REPAIR` | 状态、记录、receipt 或宿主异常 | 停止教学并修复不一致 | 验证后的原状态 |

这些是内部模式。用户无需写 `模式：ASK`。显式模式语法只作为诊断和测试接口。

## 7. Intent envelope

### 7.1 输入事件

每条用户消息先创建不可重放的输入事件：

```json
{
  "schema_version": "6.2",
  "input_event_id": "INPUT-0042",
  "input_hash": "sha256:...",
  "received_state": "AWAITING_QUESTIONS_OR_CONTINUE",
  "raw_text_hash": "sha256:...",
  "intents": []
}
```

原始聊天内容不复制到长期 memory。需要恢复的 pending intent 只保存最小必要
问题原意、source span hash、状态和 ID。

### 7.2 每个 intent

```json
{
  "intent_id": "INPUT-0042-I03",
  "kind": "question",
  "source_order": 3,
  "source_span": [48, 76],
  "source_text_hash": "sha256:...",
  "target": "NODE-loss",
  "parent_intent_id": null,
  "question_id": "Q-103",
  "status": "registered"
}
```

允许的 `kind` 至少包括 `start`、`learn`、`question`、`recall_answer`、
`correction`、`quality_feedback`、`continue`、`recover`、`close` 和 `repair`。

### 7.3 拆分不变量

- 意图按原文位置排序，`source_order` 连续且唯一。
- source span 不重叠、不越界；每个意图可回溯到同一 INPUT event。
- 显式编号、项目符号和分号是强分隔信号，但不是唯一信号。
- 一个句子包含两个可独立回答的问题时允许拆成两个 Q。
- 同一个问题中的前提、例子和限定条件不能被误拆成不同 Q。
- 无法确定是否独立时，登记一个 `clarification-required` intent，询问一个
  澄清问题；不得猜测并丢失另一种解释。
- `continue` 永远在所有问题、纠正、feedback 和 recall intent 之后处理；只要
  本 INPUT event 含实质问题，该 continue 就标记 `expired-by-question`，不得推进。
- validator 校验 envelope 的结构、顺序、span、hash 和覆盖声明；模型负责语义
  拆分，但没有通过 validator 的拆分不能更新权威状态。

## 8. 任意数量问题的两阶段事务

### 8.1 为什么不用“一次回答完再统一写入”

当用户一次提出很多问题时，统一在最后写入会产生三个风险：上下文中途耗尽、
某一题失败导致已回答内容无 durable record、恢复时不知道哪些问题已经关闭。
因此采用“批次 intake + 逐题 answer commit”。

### 8.2 阶段 A：Question intake transaction

拆分验证通过后，在开始回答前执行一个 intake TX：

1. 为所有 substantive question 按原顺序分配连续且唯一的 Q-ID；
2. 在 `PROJECT_STUDY_QA.md` 写入每个 Q 的问题原意、Parent Q、当前锚点、
   source event/intent、状态 `open` 和 `answer_status: pending`；
3. 在 LOG 写入紧凑问题索引、ordered pending queue 和不变的 continuation NODE；
4. 精确回读每个 Q-ID 与 intent 映射；
5. 运行 strict cross-file validator；
6. 只有 intake receipt 通过后才能开始声称这些问题已登记。

开放问题允许答案字段明确为 `not-answered-yet`，但不得使用假答案或
`详见聊天`。publication readiness 必须拒绝任何 `answer_status: pending`。

### 8.3 阶段 B：Per-question answer transaction

按照 pending queue 逐题执行：

1. 将一个 Q 切换为 `answering`；
2. 生成适配 Q 类型的完整规范答案和证据边界；
3. 更新同一个 QA detail，不创建重复 Q；
4. 写入 LOG 状态、retest/correction/K-card 影响和相同 answer TX；
5. 精确回读 QA 与 LOG；
6. strict validation 通过后标记 `answered/closed` 或 `retest-due`；
7. 产生只绑定该 Q answer revision 的 receipt；
8. 再处理队列中的下一个 Q。

每个问题拥有一个 intake TX 和一个或多个 answer/retest TX。Q-ID 始终稳定。

### 8.4 有界显示、无界队列

数据模型不设置问题数量上限。单次聊天响应默认最多完整展示 3 个问题的答案，
但 intake 必须先登记全部问题。超过显示窗口的 Q 保持 `open/pending`，响应末尾
报告剩余数量和唯一下一动作“继续回答问题队列”，不能把它解释为主线继续。

显示窗口是呈现限制，不是保存限制，也不允许丢弃、合并或降级后续问题。
用户可明确要求一次只回答 1 个或调整窗口；该偏好可成为 memory candidate，
不能未经批准直接保存为长期 memory。

### 8.5 部分失败

假设 Q-101、Q-102 已保存，Q-103 validator 失败：

```text
Q-101 saved
Q-102 saved
Q-103 unsaved-partial
Q-104..Q-109 registered/pending
mainline advance = blocked
unique next action = repair Q-103 answer transaction
```

不得回滚或伪装已验证的 Q-101/Q-102，也不得跳过 Q-103 继续 Q-104。修复后从
Q-103 恢复。批次只有在所有 Q 关闭或被用户明确接受为 deferred 时才 settlement
complete。

### 8.6 Follow-up 和 Parent Q

- 针对已存在问题追问不同原因、例子、路径或含义时创建新 Q-ID。
- 新 Q 的 `Parent Q` 指向被追问问题。
- 如果一条消息同时追问多个旧 Q，每个新问题分别绑定正确 parent。
- 只是要求重述同一答案且没有新意图时，可作为同 Q 的 explanation revision，
  但必须保留 revision TX；不得覆盖历史答案而无记录。

## 9. 用户提示词设计

### 9.1 唯一标准启动提示词

```text
请使用 $project-code-study 带我学习当前项目。
目标是 <学习目标>。
请从真实运行调用链建立路线，按照“定位—学习—检验—沉淀—等待”的标准循环进行。
```

项目路径、基础、重点场景和深度只在用户已给出时提取；真正缺失且会改变路线的
信息才逐项询问。不得要求用户先填写完整配置表。

### 9.2 后续交互

用户直接使用自然语言：

```text
继续。
这个函数为什么返回三个尺度？
我有五个问题：……
这是我对回忆题的回答：……
接着上次学。
先暂停，保存可恢复位置。
```

`references/user-prompts.md` 改为：

1. 一条标准启动提示词；
2. 一页标准学习循环说明；
3. 六类自然语言示例；
4. 一个多问题示例；
5. 高级诊断附录。

不再要求从 19 个模板中选择。

## 10. 模式化响应合同

所有正常响应只有三个外层区域：

```text
定位栏 → 模式主体 → 闭环栏
```

### 10.1 定位栏

```text
当前：Step 4.2 · RUN-train · NODE-loss
本轮：回答问题队列 Q-101..Q-103，不推进主线
```

### 10.2 模式主体

| Profile | 必需内容 |
| --- | --- |
| `start` | 学习目标、证据边界、路线摘要、Step 0 行动 |
| `node-teaching` | 本 NODE 问题、调用链、适用证据槽、核心解释、错误、自测 |
| `question-answer` | Q-ID/问题、直接结论、完整解释、真实证据、主线关系 |
| `recall-assessment` | 用户答案理解、判定、正确/缺失、完整答案、retest |
| `recovery` | 恢复事实、hash/状态差异、唯一位置 |
| `repair` | 失败点、已写/未写、修复结果、唯一动作 |
| `close` | readiness、blocker、consent 或 publication 边界 |

“适用证据槽”由 NODE/Q 类型决定：

- tensor/shape：输入 Shape、逐层变换、通道来源、输出验证；
- source/code：精选真实代码、调用者、返回值、执行顺序；
- config/state：字段、来源、状态变化和消费者，不强制伪造 Shape；
- math/metric：公式、变量、阈值、项目字段和误区；
- conceptual：定义、项目语境、类比、反例、相邻概念；
- correction/review：影响矩阵、传播、证据等级和回归测试。

### 10.3 闭环栏

```text
问题：3/7 已回答；Q-104 为下一题
记录：intake 已验证；Q-101..Q-103 answer TX 已验证
主线：保持 NODE-loss，不允许推进
下一步：继续回答 Q-104
```

正常情况下不显示 receipt hash、完整 pending JSON 或内部 interaction enum。
失败、诊断或用户主动请求时展开。没有机器证据时只能显示“未执行/未验证”。

## 11. 状态机变化

增加或明确以下状态：

```text
REGISTERING_QUESTION_BATCH
ANSWERING_QUESTION_QUEUE
QUESTION_BATCH_REPAIR
AWAITING_QUESTIONS_OR_CONTINUE
```

核心转移：

```text
user input with N questions
  → REGISTERING_QUESTION_BATCH
  → intake saved
  → ANSWERING_QUESTION_QUEUE
  → per-Q answer saved/retest
  → all settled
  → return_state captured at intake
```

如果 intake 前状态是 `AWAITING_RECALL`，所有支线问题处理后回到
`AWAITING_RECALL`；如果是 `FINAL_QUESTION_PHASE`，回到 final phase；普通主线
问题回到 `AWAITING_QUESTIONS_OR_CONTINUE`。`return_state` 在 intake receipt 中
绑定，模型不能事后猜测。

## 12. 计划修改边界

设计获批后预计：

- 修改 `SKILL.md`：收敛用户入口，加入标准循环和多问题不变量；
- 重写 `references/user-prompts.md`；
- 新建 `references/interaction-mode-protocol.md`；
- 更新 `references/question-protocol.md`、`learning-ledger-protocol.md` 和
  `teaching-output-contract.md`；
- 新建 `assets/INPUT_INTENT_ENVELOPE.template.json`；
- 修改 `study_events.py`：验证 source span、ordered intent 和 return state；
- 修改 `project_study_transaction.py`：question intake 和 per-Q answer update；
- 修改 `interaction_state.py`：问题队列状态与恢复；
- 将 `validate_teaching_response.py` 改为 profile-aware validator；
- 更新 LOG/QA 模板和 strict validator，使 open intake 与 completed answer 可区分；
- 新增行为级测试并更新 README、CHANGELOG、调研致谢和实施报告。

不修改用户学习项目样本；只执行只读回归和 hash 对比。

## 13. TDD 与验证设计

实现必须逐项 RED → GREEN：

1. 一条消息含 0、1、3、20 个显式问题；
2. 未编号的多个自然语言问题；
3. 一个复杂问题含多个限定条件但不能被误拆；
4. 多问题 + correction + quality feedback + continue；
5. 多问题 + recall answer，返回原 recall 状态；
6. intake 写入全部 Q，尚未回答时 publication 被阻断；
7. 每题独立 answer TX 和唯一 Q/TX；
8. 第 N 题失败时前 N-1 题保持 verified，后续保持 pending；
9. follow-up 正确绑定不同 Parent Q；
10. 问题队列跨 handoff/compaction 恢复；
11. 旧 continue 不跨问题批次；
12. 非 tensor NODE 不强制 Shape；tensor NODE 缺 Shape 仍失败；
13. 七种 response profile 的正/负 fixture；
14. 正常响应不泄漏完整内部 envelope/receipt hash；
15. 宿主没有 control tool 时禁止 saved/validated/complete；
16. 旧 schema 的只读迁移测试；
17. 全部现有单元和对抗回归；
18. 至少一次真实宿主多问题对话；未运行则明确 `not-run`。

由于当前会话不能在未获授权时创建测试 subagent，fresh-agent prompt pressure
test 将作为独立宿主测试项；本地实现仍使用确定性单元测试先行。不能用静态
fixture 代替真实宿主结果。

## 14. 迁移与兼容

- 现有 schema 4.1 LOG/QA 保持可读。
- 新建记录使用 4.2（具体版本在实现计划中锁定）。
- 4.1 的单 Q 事务继续可用；只有 4.2 支持 question batch intake。
- 不静默迁移已有学习项目；迁移需要用户授权、备份和严格校验。
- schema 2.1 正式手册协议保持不变，但 readiness 必须识别 pending answer。
- Claude/Codex/Copilot 不支持的 hook 能力继续显示 `advisory/not-run`。

## 15. 隐私、证据和失败边界

- 不把完整聊天复制到 memory、LOG 或最终文档。
- QA 保存问题原意所需的最小文本；input/source span 使用 hash 绑定。
- 问题数量大不构成降低答案深度或跳过 QA 的理由。
- 模型回答完成不等于 QA 保存完成。
- intake receipt 不证明 answer saved；answer receipt 不证明整个 batch settled。
- 任何 queue/hash/return-state 不一致进入 `QUESTION_BATCH_REPAIR` 或
  `REPAIR_REQUIRED`。
- 只有所有问题关闭、retest 通过、pending intent 为空时才允许 fresh continue。

## 16. 验收标准

v6.2 只有同时满足以下条件才算完成：

1. 新用户只用一条启动提示词即可进入完整流程；
2. 后续自然语言可稳定映射到内部模式；
3. 任意数量的问题全部登记且每题有独立 Q-ID；
4. 每个已回答问题在 QA 中有完整、可独立阅读的答案；
5. 中途失败和上下文压缩后能从精确 Q 恢复；
6. 提问不会移动或丢失主线/recall/final return state；
7. 模式化输出比统一八段模板更短，但语义质量 gate 不降低；
8. v6.1 的 fail-closed、memory、receipt、correction 和 publication 不变量全部通过；
9. README 能让用户在一页内理解标准模式；
10. 测试和真实宿主边界被如实报告。

## 17. 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 自然语言拆分不可能完全确定 | source span + coverage validator；歧义进入单一澄清，不猜测 |
| 一次问题过多导致响应过长 | 全量 intake、默认 3 题显示窗口、可恢复 pending queue |
| intake 写入 open Q 被误认为已回答 | 单独 `answer_status`、不同 receipt、publication gate |
| 每题独立事务增加 I/O | 保持正确性优先；后续只优化 staging，不合并成功声明 |
| 内部状态隐藏后用户难以审计 | 正常显示紧凑状态栏；诊断模式可展开全部机器状态 |
| 模式化合同过于宽松 | 每个 profile 有类型化必需槽和负向 fixture |
| 宿主不执行 router/guard | 禁止正向状态声明，显示 advisory/not-run |

## 18. 致谢

感谢 learn-codebase、GitHub Copilot/awesome-copilot、Claude Code Skills、
Anthropic skill-creator 和 Superpowers 的维护者公开相关设计。v6.2 只借鉴用户
入口分层、渐进披露、阶段触发和 handoff 等思想；没有复制上游提示词、协议或
实现。本项目与上述项目无隶属、赞助或背书关系。
