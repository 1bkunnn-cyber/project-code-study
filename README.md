# Project Code Study

<div align="center">

**Learn a repository from its real runtime paths—not from a generic architecture outline.**<br>
**沿真实运行路径学习项目，而不是套用通用架构目录。**

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-111827)](https://agentskills.io/)
[![Version](https://img.shields.io/badge/version-5.0.0-2563EB)](SKILL.md)
[![Claude](https://img.shields.io/badge/Claude-supported-D97706)](https://claude.ai/)
[![Codex](https://img.shields.io/badge/Codex-supported-10A37F)](https://openai.com/codex/)
[![GitHub stars](https://img.shields.io/github/stars/1bkunnn-cyber/project-code-study?style=flat)](https://github.com/1bkunnn-cyber/project-code-study/stargazers)
[![License](https://img.shields.io/github/license/1bkunnn-cyber/project-code-study)](LICENSE)

[简体中文](#简体中文) · [English](#english)

</div>

---

<a id="简体中文"></a>

## 简体中文

`project-code-study` 是面向 Claude Code、Codex 和其他 Agent Skills 宿主的证据驱动源码学习工作流。它先扫描项目并建立训练、推理、评估等真实运行路径，再按调用关系一次学习一个 `RUN/NODE`，同时把路线、证据、问答、修正和掌握行为持久化为可审计的 Markdown 记录。

5.0 版本重点修复了长期学习中的真实性与控制流问题：保存回执必须经过跨文件回读与严格校验；回答问题后必须暂停；每个节点只有一个状态；`done` 必须有可重新学习的知识卡；最终文档必须先通过不可绕过的 readiness gate。

### 核心保证

| 保证 | 5.0 行为 |
| --- | --- |
| 项目专属路线 | 从实际入口、运行场景和概念依赖生成路线，不硬套 Backbone/Transformer/Head |
| 一次一个节点 | 源码阶段每轮只教学一个类、函数、目标函数或后处理节点 |
| 显式交互状态 | 主动回忆、支线问答、等待继续、最终审计和文档同意都有明确状态 |
| 单次继续令牌 | 只有等待状态中收到的新 `继续` 才能推进；问答前的旧指令不会再次生效 |
| 独立 Q&A | 每个实质性问题和追问都有 Q-ID、完整规范答案、证据、主线锚点和事务 ID |
| 真实保存回执 | LOG/QA 写入、精确回读、跨文件对账和 strict validator 全部通过后才能返回 `saved` |
| 唯一 NODE 状态 | 仅允许枚举值；跳过/延后必须记录原因、影响、重访条件和学习者接受情况 |
| 语义完成门槛 | 讲过不等于掌握；`done` 需要行为验证、完整参考答案、durable K 卡和成功事务 |
| 修正全局生效 | M/C 保存旧说法、规范说法、证据、影响和 stale pattern；最终化扫描旧措辞 |
| 最终化 fail-closed | 路线、场景、NODE、问题、K 卡、修正、用户关闭问题阶段和同意全部通过才能生成正式文档 |
| 独立重学 UNIT | 每个完成 Step 映射到可脱离聊天重新学习的 UNIT，并具有唯一 ID 和显式 anchor |
| 可执行回归 | 状态机、记录校验、readiness 和最终文档均有 Python 校验器与 T-01～T-16 测试 |

## 双 Skill 架构

1. [`project-code-study`](SKILL.md) 负责项目扫描、动态路线、逐节点教学、问答、修正、证据与持久化。
2. [`project-study-document`](skills/project-study-document/SKILL.md) 只在 readiness 通过且用户明确同意后，生成最终学习文档。

伴生 Skill 不参与日常教学。路线未闭合时，它只返回 readiness report；用户明确要求阶段性产物时，也只能生成 `status: incomplete-draft`。

## 工作流

```text
仓库 / 论文 / 配置 / 运行证据
  -> Step 0：项目地图与证据边界
  -> Step 1–2：问题背景、相关方法、代表性输入与数据路径
  -> Step 3：RUN 场景、NODE 调用图与概念依赖
  -> Step 4.x：按真实调用顺序，一次学习一个 NODE
  -> 主动回忆 / 调用追踪 / Shape 或状态推演 / 修改预测
  -> Step 5：从已理解节点重建架构与论文—代码映射
  -> Step 6+：目标函数、训练、推理、评估、复现和实验
  -> 覆盖、问题、修正与 stale 审计
  -> 明确关闭问题阶段
  -> readiness pass
  -> 明确同意
  -> PROJECT_STUDY_DOCUMENT.md
```

Step 编号只是可调整骨架。实际路线由项目入口、运行分支、概念前置和学习目标决定。

### 问答后的状态控制

教学结束进入等待；用户回答主动回忆或提出支线问题后，Skill 必须给出完整答案并保存，然后停在 `AWAITING_QUESTIONS_OR_CONTINUE`。同一回复不得开始下一个 NODE。状态转换的可执行参考位于 [`scripts/interaction_state.py`](scripts/interaction_state.py)。

### 跨文件事务

```text
分配 TX-ID
  -> 写 Q&A 详情和索引
  -> 精确回读 Q/Parent/完整答案/状态/锚点/TX
  -> 写 LOG 热状态、索引、K 卡、路线、session 与 TX
  -> 精确回读 current/next/interaction/Q/TX
  -> LOG/QA 对账
  -> strict validator
  -> 全部通过才是 saved
```

部分成功返回 `unsaved-partial`，并保留紧凑 delta；修复记录一致性是唯一下一行动，不能继续教学。

## 持久化文件

| 文件 | Schema | 作用 |
| --- | --- | --- |
| `PROJECT_STUDY_LOG.md` | 4.1 | 权威热状态、RUN/NODE 路线、证据、掌握度、K 卡、M/C、实验、事务和 session |
| `PROJECT_STUDY_QA.md` | 1.1 | 完整问题、追问、主动回忆答案、证据、反馈、锚点和事务回执 |
| `PROJECT_STUDY_DOCUMENT.md` | 1.2 | readiness 与用户同意后生成的独立重学文档 |

兼容读取仍支持 LOG schema 4.0/3.1、Q&A schema 1.0 和最终文档 schema 1.0/1.1。严格语义与跨文件校验要求新 schema；迁移旧记录必须获得授权并保留备份。

## 微 Step 与 durable K 卡

每个微 Step 至少说明场景、调用者、当前符号、下游、源码位置、执行顺序、输入输出/Shape/状态、设计原因、证据和未验证边界。标记 `done` 前还必须保存完整 K 卡：

- prerequisites 与 learning objective；
- runtime position 与 complete explanation；
- source locations 与 inputs/outputs/Shapes/states；
- rationale、alternatives、trade-offs 和 failure modes；
- important Q、canonical M/C 与 evidence status；
- self-check、完整 reference answer、next connection 和行为掌握证据；
- 成功的 TX-ID。

## 最终化 Readiness Gate

正式生成前运行：

```powershell
python scripts/validate_finalization_bundle.py `
  --ledger PROJECT_STUDY_LOG.md `
  --qa PROJECT_STUDY_QA.md
```

必须同时满足：路线和必要场景最终化、核心 NODE 无缺口、没有 open/retest 问题、没有待回应用户输入、没有未解决修正或 stale 提升、每个 done Step 有 durable K 卡、Q&A 无隐藏聊天依赖、问题阶段已明确关闭、用户已明确同意、LOG/QA strict 校验为零错误。

## 最终文档写入流程

最终文档不再通过尾部追加或无边界字符串替换“补齐”。伴生 Skill 会先在内存建立唯一 Step/UNIT 映射，再一次性渲染临时同目录文件：

1. `validation_status: pending` 执行 preflight；
2. 零错误后只改为 `validated`；
3. 执行最终校验；
4. 回读 frontmatter、目录、UNIT/anchor、Q/M/C、证据和下一行动；
5. 原子替换正式目标。

每个 UNIT 必须能在没有原聊天的情况下重新教授目标、RUN/NODE 位置、源码执行顺序、I/O/Shape/状态、设计取舍、重要问题、规范修正、自测答案、下一节点和未验证边界。

## 安装

```bash
git clone https://github.com/1bkunnn-cyber/project-code-study.git
```

将完整目录复制或链接到宿主支持的 Skill 目录，例如：

```text
Claude Code 用户级：~/.claude/skills/project-code-study
Codex 用户级：      ~/.codex/skills/project-code-study
项目级：            <project>/<host-skill-directory>/project-code-study
```

请保留 `skills/project-study-document` 子目录。

## 快速开始

```text
请使用 $project-code-study 带我学习当前项目。
目标：<读懂 / 复现 / 修改 / 研究扩展>
基础：<一句话>
本轮先确认记录权限、证据边界和项目专属路线，只完成 Step 0。
```

继续时只需：

```text
继续主线。本轮只学习精确继续位置对应的一个 NODE。
```

直接提出支线问题即可。Q-ID、保存、暂停和主线锚点是 Skill 内部保证，不需要用户反复粘贴控制提示。恢复与诊断示例见 [`references/user-prompts.md`](references/user-prompts.md)。

## 校验与测试

### 模板结构

```powershell
python scripts/validate_learning_ledger.py assets/PROJECT_STUDY_LOG.template.md --template
python scripts/validate_learning_ledger.py assets/PROJECT_STUDY_QA.template.md --template
python skills/project-study-document/scripts/validate_study_document.py `
  skills/project-study-document/assets/PROJECT_STUDY_DOCUMENT.template.md --template
```

### 实际 LOG/QA 严格校验

```powershell
python scripts/validate_learning_ledger.py PROJECT_STUDY_LOG.md `
  --strict --qa PROJECT_STUDY_QA.md
```

### 最终文档双阶段校验

```powershell
python skills/project-study-document/scripts/validate_study_document.py <temp.md> `
  --ledger PROJECT_STUDY_LOG.md --qa PROJECT_STUDY_QA.md --preflight

python skills/project-study-document/scripts/validate_study_document.py PROJECT_STUDY_DOCUMENT.md `
  --ledger PROJECT_STUDY_LOG.md --qa PROJECT_STUDY_QA.md
```

### T-01～T-16 回归

```powershell
python -m unittest discover -s tests -v
```

测试覆盖事务部分失败、连续追问、问答后暂停、旧继续令牌失效、中断节点、NODE 枚举、未完成路线阻断、隐藏聊天依赖、重复 UNIT/anchor、占位句、stale correction、伪 `validated`、Step/NODE 分离、冷启动静态代理、无控制长提示和图示策略。

> 冷启动静态代理只能证明 UNIT 结构与语义字段齐备。真实的新会话/跨模型重学测试必须单独记录为 `pass`、`fail` 或 `not-run`；未运行时不能宣称通过。

## 仓库结构

| 路径 | 职责 |
| --- | --- |
| [`SKILL.md`](SKILL.md) | 主 Skill 不变量、状态机、事务与工作流 |
| [`references/`](references) | 调用图、问答、记录、完成门槛、论文映射和诊断协议 |
| [`assets/PROJECT_STUDY_LOG.template.md`](assets/PROJECT_STUDY_LOG.template.md) | LOG schema 4.1 |
| [`assets/PROJECT_STUDY_QA.template.md`](assets/PROJECT_STUDY_QA.template.md) | Q&A schema 1.1 |
| [`scripts/interaction_state.py`](scripts/interaction_state.py) | 交互状态机可执行参考 |
| [`scripts/validate_learning_ledger.py`](scripts/validate_learning_ledger.py) | 结构、语义与 LOG/QA 对账 |
| [`scripts/validate_finalization_bundle.py`](scripts/validate_finalization_bundle.py) | fail-closed readiness manifest |
| [`skills/project-study-document/`](skills/project-study-document) | 最终文档伴生 Skill、schema 1.2 模板和 validator |
| [`tests/test_regressions.py`](tests/test_regressions.py) | T-01～T-16 可重复回归 |

## 证据与安全边界

Skill 区分 `已确认`、`可推断`、`背景知识` 和 `待验证`。发现文件不等于读过文件；建议命令不等于实际执行；论文主张不等于当前实现；聊天中的同意不等于掌握。

未读取的实现不得凭模型记忆补全。记录不保存完整聊天、隐藏推理、凭据或无关隐私。文件写入、命令、联网、下载和源码修改始终受用户授权与宿主权限约束。

---

<a id="english"></a>

## English

`project-code-study` is an evidence-grounded Agent Skill for learning a repository through its actual runtime scenarios and call nodes. Version 5.0 adds fail-closed persistence, an explicit interaction state machine, unique NODE states, standalone Q&A, durable knowledge cards, a readiness manifest, schema 1.2 relearning units, and executable T-01–T-16 regressions.

### Key behavior

- Build project-specific `RUN-` paths and `NODE-` graphs from repository evidence.
- Teach one runtime node per micro-step.
- Pause after recall or side-question closure; only a fresh, single-use continue event advances.
- Persist every substantive question with a complete standalone answer and one cross-file `TX-` ID.
- Report `saved` only after exact LOG/QA readback, reconciliation, and strict validation.
- Require behavior evidence and a complete durable `K-` card before `done`.
- Block formal document generation until route, scenarios, nodes, questions, corrections, knowledge cards, explicit question closure, and consent all pass.
- Generate unique, anchored relearning units that do not depend on chat history.

### Quick start

```text
Use $project-code-study to teach me the current repository.
Goal: <understand / reproduce / modify / research extension>
Background: <one sentence>
Confirm record permissions and build the project-specific route; complete only Step 0.
```

### Validation

```powershell
python scripts/validate_learning_ledger.py PROJECT_STUDY_LOG.md `
  --strict --qa PROJECT_STUDY_QA.md

python scripts/validate_finalization_bundle.py `
  --ledger PROJECT_STUDY_LOG.md --qa PROJECT_STUDY_QA.md

python -m unittest discover -s tests -v
```

Final schema 1.2 documents use a preflight pass with `validation_status: pending`, followed by a final pass after changing only that field to `validated`. Real cold-start/cross-model acceptance remains a separately recorded test; a static proxy is not reported as a real run.

## License

MIT. See [`LICENSE`](LICENSE).
