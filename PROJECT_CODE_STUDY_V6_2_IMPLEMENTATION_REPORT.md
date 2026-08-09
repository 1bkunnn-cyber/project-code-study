# Project Code Study v6.2 实施报告

日期：2026-08-09  
分支：`codex/skill-reliability-v5`

## 1. 结果摘要

v6.2 将“提示词目录”和 Skill 内部机制收敛为同一套模式：用户只需一个启动提示，之后自然提问、回答回忆、纠正、暂停或继续；内部固定执行 `定位 → 学习 → 检验 → 沉淀 → 等待`，并按 `START/LEARN/ASK/ASSESS/RECOVER/CLOSE/REPAIR` 选择响应合同。

本次核心不是文案替换，而是新增了 source-bound intent envelope、任意数量问题的两阶段事务、问题队列状态机、精确 return-state/handoff、QA/LOG 4.2/1.2 和 profile/content-aware response validator。

## 2. GitHub/官方文档调研与采用

| 参考项目/文档 | 采用的思想 | 决策 |
| --- | --- | --- |
| [learn-codebase](https://github.com/ktaletsk/learn-codebase) | 一次调用后自然苏格拉底式追问、主动回忆 | 直接借鉴教学交互思想；未复制提示词 |
| [GitHub Copilot customization](https://docs.github.com/en/copilot/customizing-copilot/about-customizing-github-copilot-chat-responses) | instructions、prompt、Skill、hook 职责分离 | 采用职责边界；宿主未执行 hook 时仍 fail-closed |
| [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) | Skill 调用与上下文加载边界 | 采用自然入口与显式 handoff；不假设压缩后自动恢复 |
| [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) | 渐进披露：短主体、按需 reference/script | 采用短响应合同和 scoped protocol；未复制模板 |
| [Superpowers](https://github.com/obra/superpowers) | phase trigger、hard gate、验证后声明 | 采用 intake-before-answer、repair-only、claim gate |
| [awesome-copilot](https://github.com/github/awesome-copilot) | 简洁 handoff、结构化行动边界 | 采用一个入口和唯一下一行动；未复制内容 |

完整仓库、许可证、活跃程度、适用性和拒绝项见 [GITHUB_RESEARCH_AND_ACKNOWLEDGEMENTS.md](GITHUB_RESEARCH_AND_ACKNOWLEDGEMENTS.md)。感谢上述维护者和贡献者公开这些思想；本仓库没有复制其源代码、提示词或协议。

## 3. 修改文件

| 类别 | 文件 |
| --- | --- |
| Skill/用户入口 | `SKILL.md`、`references/user-prompts.md`、`references/interaction-mode-protocol.md` |
| 交互与教学协议 | `references/prompt-workflow-patterns.md`、`references/question-protocol.md`、`references/learning-ledger-protocol.md`、`references/teaching-output-contract.md`、`assets/NODE_TEACHING_CONTRACT.md` |
| 状态/事务机制 | `scripts/study_events.py`、`scripts/interaction_state.py`、`scripts/project_study_transaction.py` |
| schema/validator | `assets/PROJECT_STUDY_LOG.template.md`、`assets/PROJECT_STUDY_QA.template.md`、`assets/PROJECT_STUDY_HANDOFF.template.json`、`scripts/validate_learning_ledger.py`、`scripts/validate_teaching_response.py`、`scripts/validate_skill_structure.py` |
| 测试 | `tests/test_interaction_modes_v62.py`、`tests/test_question_batch_v62.py` 及相关回归 fixture/contract 测试 |
| 发布文档 | `README.md`、`CHANGELOG.md`、`GITHUB_RESEARCH_AND_ACKNOWLEDGEMENTS.md`、v6.2 design/plan、本报告 |

## 4. 保留的好设计

- 真实运行调用链、一次一个 RUN/NODE、动态 Step/micro-Step/NODE 路线。
- 主线锚点、continuation NODE、支线后精确恢复和旧 continue 单次消费。
- pending intents、retest gate、Q/M/C/TX 唯一性和 correction 传播。
- QA/LOG/receipt 事务、not-run 证据边界和禁止虚假 saved/validated/complete。
- memory consent、candidate 生命周期、拒绝脱敏、hash handoff 和 fail-closed。
- 正式文档 consent/readiness/cold-start/release receipt，以及 schema 2.1 紧凑逐 Step 手册。
- research_stitching 与主项目隔离；宿主控制工具未调用不归因于项目内容。

## 5. 新机制

### 5.1 Intent envelope

schema 6.2 保存 INPUT ID、raw hash、received state，以及每个 intent 的顺序、精确 source span/hash、类型、target、parent、Q binding 和状态。确定性 splitter 支持编号、换行、分号和多个问号，没有问题数量上限；复杂单问题不会因内部“以及”被机械拆开。question/correction 会让同一 input 的 continue 变为 `expired-by-question`。

### 5.2 任意问题两阶段事务

`register_question_batch()` 在任何回答前为全部问题分配 Q-ID，并原子写入 QA/LOG pending 队列，生成 `question-intake` receipt。`answer_question()` 只更新一个已登记 Q-ID，使用独立 TX/receipt。第 N 题失败不会回滚此前成功题，也不会误消费后续 pending 题；追问创建新 Q 并保存 Parent Q。

### 5.3 状态与恢复

新增 `REGISTERING_QUESTION_BATCH`、`ANSWERING_QUESTION_QUEUE`、`QUESTION_BATCH_REPAIR`。队列捕获原 interaction state；全部回答后恢复该状态，而不是固定回普通等待。handoff 新增 active INPUT、完整 Q 队列、current Q 和 return state，hash 漂移仍进入 `REPAIR_REQUIRED`。

### 5.4 响应合同

响应 validator 按 profile 选择必要章节，并独立按 `content_kind` 检查证据。tensor 必须有具体 Shape，code 必须有 fenced source，metric 必须有显式公式；config/state 不再为满足模板编造数字 Shape。所有 profile 仍核对五个位置字段和 QA/receipt 状态。

### 5.5 QA 深度与 schema

生成模板升级为 LOG 4.2 / QA 1.2，新增 input/intent/answer-status/queue/return-state 字段。pending 记录可作为严格工作状态，但 publication 必须阻断；answered 后才执行 concept/code/shape/metric/review/correction 的类型深度合同。旧 4.1/1.1 样本仍可 strict 读取，不能获得 v6.2 queue 字段能力。

## 6. 提示词与 README 变化

旧 19 模板目录改为一个启动提示、自然日常输入和默认隐藏的高级诊断附录。README 同步说明七模式、任意问题 intake/answer、QA/LOG/memory/document 边界、receipt、紧凑手册、测试命令、宿主限制和实际采用的外部思想。

`PROJECT_STUDY_DOCUMENT.md` 的目标保持 v6.1 已确认的“可翻阅 Step 手册”：8 个紧凑槽位、精选源码、快速索引、shared deep dive、profile 预算和定位/解释/应用 cold-start；v6.2 没有把它扩回全文教材或聊天/源码复制品。

## 7. 修改前后对应关系

| 修改前问题 | v6.2 对应机制 |
| --- | --- |
| 提示词与 Skill 重复、用户承担内部术语 | 单启动提示 + 七模式内部 router |
| 一次多问只证明“能 split”，不能证明全保存 | 全量 intake transaction + 每 Q answer transaction |
| 问题数量与编号形式不确定 | source-bound envelope；0/1/3/20 和非编号测试 |
| 某题失败可能污染整批 | 每 Q 独立 TX；N 题失败隔离 |
| 支线结束固定回普通等待 | 捕获并恢复 exact return state |
| 所有响应机械八段且强制 Shape | profile + content_kind 双维合同 |
| prompt 文案声称工具会执行 | host capability/claim guard 继续 fail-closed |
| 压缩后问题队列可能丢失 | handoff 保存 INPUT、queue、current Q、return state |

## 8. 测试结果

| 项目 | 结果 |
| --- | --- |
| 全部 unittest/regression | 116 total：115 pass，1 skip；skip 为真实宿主 golden conversation，明确 not-run |
| Skill 静态结构与 Python parse | pass |
| LOG 4.2 / QA 1.2 模板解析 | pass |
| Intent 0/1/多问/20 问/source hash/旧 continue | pass |
| 全量 intake、逐题 answer、Nth failure、Parent Q、envelope tamper、publication pending gate | pass |
| 真实 strict validator 驱动的 intake/answer 与 AWAITING_RECALL 恢复 | pass |
| mixed intents、retest、旧 continue、ID 唯一性、receipt hash | pass |
| memory lifecycle/refusal/doctor、handoff/hash drift | pass；授权真实样本 memory doctor 通过 |
| schema 2.1 document validator/cold-start/compactness/source budget | fixture tests pass |
| 授权真实样本 LOG/QA strict | pass（旧 4.1/1.1 兼容路径） |
| 授权真实样本文档 validator | 正确 blocked：仍有 `Q-100`、`Q-101` open；未修改样本 |
| Codex host control-path smoke | pass：自然 3 问全部登记、response contract 通过、第一题 strict answer 保存、2 题 pending |
| 授权学习样本只读保护 | pass：审计报告、QA、LOG、DOCUMENT、MEMORY、指定 Claude JSONL 的前后 SHA-256 完全一致；research_stitching 未执行写命令 |

## 9. Not-run 与限制

- Claude 真实 learner golden conversation：not-run。
- 多模型教学一致性：not-run。
- 真实上下文压缩事件与跨会话自动恢复：not-run。
- Claude/Codex pre-response hook 强制调用：not-run；当前仅本地 validator/claim guard 与 Codex shell control-path smoke。
- 真实 cold-start 新模型只读最终文档：not-run；本地 schema 2.1 proxy/报告 validator 通过不能替代它。

## 10. 风险

- 确定性 splitter 不声称解决所有中文语义歧义；复杂未编号混合句需要模型提出 spans，再由 validator 约束。
- Markdown 双文件事务依赖同目录临时文件和 fail-closed 恢复，不等同于数据库级跨文件原子提交。
- “每轮最多展示三题”是响应策略，不是宿主 scheduler；持久化队列本身无 N 限制。
- 4.1/1.1 可 strict 读取但不具备新队列字段；迁移必须得到用户授权。
- Skill 文本不能安装宿主 hook；没有实际 hook/receipt 时仍禁止成功声明。
