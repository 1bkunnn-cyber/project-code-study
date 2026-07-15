# Project Code Study

<div align="center">

**Learn a repository from its real runtime paths—not from a generic architecture outline.**<br>
**沿真实运行路径学习项目，而不是套用通用架构目录。**

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-111827)](https://agentskills.io/)
[![Version](https://img.shields.io/badge/version-4.2.0-2563EB)](SKILL.md)
[![Claude](https://img.shields.io/badge/Claude-supported-D97706)](https://claude.ai/)
[![Codex](https://img.shields.io/badge/Codex-supported-10A37F)](https://openai.com/codex/)
[![GitHub stars](https://img.shields.io/github/stars/1bkunnn-cyber/project-code-study?style=flat)](https://github.com/1bkunnn-cyber/project-code-study/stargazers)
[![License](https://img.shields.io/github/license/1bkunnn-cyber/project-code-study)](LICENSE)

**Language / 语言：** [简体中文](#简体中文) · [English](#english)

</div>

---

<a id="简体中文"></a>

<details open>
<summary><strong>简体中文</strong></summary>

## 功能概览

`project-code-study` 是面向 Claude Code、Codex 及其他 Agent Skills 宿主的证据驱动源码学习工作流。它不是 Python 包，也不是逐行翻译源码的提示词；它会先扫描项目并还原训练、推理、评估等真实运行路径，再将源码学习拆成一次一个调用节点、类或函数的微 Step。

学习过程由两个持久化 Markdown 文件维护。主日志保存路线、状态、证据和修正索引，Q&A 文件保存用户的提问、追问、完整答案与教学反馈。全部学习和提问结束后，主 Skill 会征得用户明确同意，再调用仓库内的伴生 Skill 生成一份可追溯的最终学习文档。

### 你能获得什么

| 能力 | 具体行为 |
| --- | --- |
| 项目专属路线 | 扫描当前仓库，按真实场景生成调用图和概念依赖，不硬套 Backbone / Transformer / Head 等固定目录 |
| 运行时调用链教学 | 从入口沿实际调用关系推进，而不是按文件名、import 或目录顺序讲解 |
| 微 Step 学习 | 源码阶段动态拆成 `Step 4.x`，每次只学习一个调用节点、类或函数 |
| 多场景覆盖 | 分开追踪 `train`、`infer`、`eval`，并在项目适用时覆盖 `export`、`deploy` 等路径 |
| 掌握度验证 | 使用主动回忆、源码追踪、Shape 推演、修改预测等任务验证理解 |
| 问答闭环 | 每个实质性问题和追加追问获得稳定 ID；无论用户答对与否都提供完整参考答案和证据 |
| 规范修正 | 保存旧表述、规范表述、修正依据和影响范围，防止后续文档重新使用已被纠正的说法 |
| 主线锚点 | 支线语法问题回答完毕后，明确告诉用户回到哪个运行节点继续学习 |
| 对比与延伸 | 对比同任务方法、同瓶颈方法、跨领域相似思想以及可组合模块 |
| 模块组合审查 | 从接口、Shape、目标函数、稳定性、成本、已有工作和消融设计判断“缝合”是否成立 |
| 可恢复学习记忆 | 日常只加载热状态和相关记录，减少长会话中的上下文膨胀 |
| 最终学习文档 | 所有 Step 和问题关闭后，经用户同意生成 `PROJECT_STUDY_DOCUMENT.md`；每个已完成 Step 都映射到可独立重新学习的知识单元，并保留重要提问与规范答案 |

## 双 Skill 架构

仓库包含两个职责明确的 Skill：

1. [`project-code-study`](SKILL.md)：负责项目扫描、路线生成、逐步教学、问答记录、修正和掌握度审计。
2. [`project-study-document`](skills/project-study-document/SKILL.md)：只在学习结束、问题关闭且用户明确同意后，将已有证据综合成最终 Markdown 学习文档。

伴生 Skill 由主 Skill 在满足结束门槛后显式交接，不参与日常教学，也不会因为用户沉默而自动生成文档。

## 它解决了哪些问题

| 常见问题 | 处理方式 |
| --- | --- |
| 固定套用通用模型目录 | 先扫描当前仓库，再为真实运行场景生成项目专属路线 |
| 一开始就讲完整架构，模块关系停留在名词层面 | 先按调用顺序学完核心节点，再从已掌握节点重建整体架构 |
| 一个 Step 同时塞入很多类和函数 | 动态拆成微 Step；一次只处理一个节点、类或函数 |
| 只讲 `model.forward()`，遗漏匹配器、目标函数或后处理 | 分别建立训练、推理、评估等场景调用图并执行覆盖审计 |
| 用户回答后只得到“基本正确” | 始终给出判断、正确部分、缺失部分、完整答案、证据和状态影响 |
| 追加追问和新问题没有写入记录 | 每个实质性问题持续写入 Q&A，并在主日志维护索引和状态 |
| 支线问题打断主线，用户需要向上翻找 | 保存唯一主线锚点；回答支线后直接给出精确恢复位置 |
| 模型修正了说法，但最终总结仍使用旧结论 | 使用 correction/stale 状态追踪修正，最终文档只采用最新规范表述 |
| 一个日志越来越长，每轮都完整读取 | 将状态索引与高增长问答分离，默认只读取热状态和相关 ID |
| 学完以后只有聊天记录，没有可复习材料 | 经用户同意生成结构化、可验证、包含重要提问的单个 Markdown 文档 |

## 工作流程

```text
仓库、论文与运行证据
        ↓
Step 0：项目地图、学习目标与证据边界
        ↓
Step 1–2：任务背景、相关方法、代表性输入与数据路径
        ↓
Step 3：识别运行场景，建立调用图与概念依赖
        ↓
Step 4.x：严格按真实调用顺序，一次学习一个节点
        ↓
主动回忆 / 源码追踪 / Shape 推演 / 修改预测
        ↓
Step 5：从已掌握节点重建完整架构并映射论文
        ↓
Step 6+：目标函数、训练、推理、评估、复现与实验
        ↓
覆盖审计、相关方法比较、模块组合与研究延伸
        ↓
确认用户没有更多问题 → 询问是否生成最终学习文档
```

路线编号是可调整的骨架，不是对所有项目都相同的课程表。实际 Step 数量与顺序取决于仓库入口、运行场景、概念依赖和用户目标。

### 按运行时顺序，而不是文件顺序

Skill 先扫描相关源码以避免漏项，再按当前节点选择性读取文件。教学顺序来自入口在具体场景中的真实调用关系，而不是目录、import 或源码排版顺序。

例如，只参与训练目标计算的模块应进入训练场景的 objective/loss 路径，而不是被塞进前向传播；不是独立函数、但属于后续节点必要前置知识的概念，则会作为依赖微 Step 插入路线。

### 一次只学习一个节点

每个源码微 Step 至少说明：

- 当前运行场景及其在全局路线中的位置；
- 上游调用者、当前符号与下游节点；
- 文件、类、函数或配置的精确位置；
- 关键参数、非直观语法、输入输出 Shape 和局部逻辑；
- 设计动机、工程风险以及对下一个节点的影响；
- 当前证据、未确认事项和可验证的掌握任务。

“模型讲过”“用户看过”或“日志写过”都不自动等于掌握。只有完成相应验证任务后才推进。

## 持久化学习记忆

### `PROJECT_STUDY_LOG.md`

主日志是紧凑的状态与索引层，保存：

- 当前 Step、场景、节点、精确继续位置和唯一下一行动；
- 项目专属调用路线、概念依赖、节点状态和掌握证据；
- 源码、论文与运行证据；开放问题、误区和规范修正；
- 问题索引、实验、比较、复习队列、里程碑和会话摘要。

### `PROJECT_STUDY_QA.md`

Q&A 文件保存高增长的交互详情：

- 新问题、追加追问和语法问题；
- 主动回忆作答、评价和完整参考答案；
- 学习心得、教学反馈和路线调整；
- 与节点、证据、误区和修正 ID 的关联。

正常继续学习时只读取主日志热状态及当前任务关联的问答记录；完整历史只在审计、迁移或最终综合时读取。每次有效写入后必须回读验证，失败则明确标记 `unsaved`。

## 提问、作答与修正闭环

每个实质性问题都获得稳定的 `Q-` ID。用户回答主动回忆题后，无论是否正确，都必须依次得到：

```text
判断
→ 正确部分
→ 缺失或错误部分
→ 完整参考答案
→ 源码 / 论文 / 运行证据
→ 对旧结论和掌握状态的影响
→ 保存回执与下一行动
```

当用户提问促使模型修正先前说法时，记录同时保存原表述、规范表述、依据、影响范围以及旧内容是否 stale。后续讲解和最终学习文档只能使用最新的规范表述。

## 对比、延伸与模块组合

比较对象不限于“同任务的另一个模型”，而是按学习和研究价值选择：

1. **同任务方法**：比较同一评价目标下的建模和工程取舍；
2. **同瓶颈方法**：比较如何处理相同限制、误差来源或优化难点；
3. **相似思想**：寻找其他任务或领域中的同构机制；
4. **可组合模块**：分析模块是否值得集成以及如何验证。

“缝合”不会被自动包装成创新。组合分析至少检查接口与 Shape、目标函数、优化稳定性、运行成本、已有工作、消融设计和性能归因，并区分工程集成与研究贡献。

## 最终 Markdown 学习文档

学习结束采用两段式确认：

1. 所有计划 Step 和审计完成后，先询问用户是否还有问题；只要用户继续提问，就继续回答并记录。
2. 用户明确表示没有更多问题后，才询问是否生成 `PROJECT_STUDY_DOCUMENT.md`。

只有用户明确同意才会生成。伴生 Skill 会完整读取学习日志与 Q&A、重新核验关键结论，并生成一份能够脱离原对话重新学习的综合性文档，而不是聊天转录。

文档会为每个已完成 Step 和微 Step 保留知识覆盖行，并将其映射到一个或多个 `UNIT-` 复习单元。复习单元不能只有一句总结，必须包含前置知识、完整讲解、运行位置、源码与证据、输入输出/Shape/公式、设计取舍、重要提问与修正、自测和参考答案。多个紧密相关的 Step 可以共用一个单元以减少重复，但不能省略任何 Step 的独有知识。默认内容包括：

- 项目任务、证据范围和学习成果；
- 全部 Step 的知识覆盖索引和可独立重新学习的知识单元；
- 训练、推理、评估等真实调用链；
- 按运行关系和概念依赖组织的核心源码节点；
- 数据、Shape、目标函数、训练、推理和评估；
- 论文—代码映射、相关方法和模块组合；
- 真正改变理解的重要用户提问及规范答案；
- 误区、修正、失败、局限、未解决事项和后续行动；
- 源码、论文、运行记录和学习产物索引。

重要问题按学习影响筛选，例如：纠正了旧结论、暴露关键误区、涉及核心运行节点、连接公式与实现、影响复现、促成方法比较或被用户反复强调。最终文档区分稳定结论与待验证解释，并保留失败和局限。

## 安装

克隆仓库：

```bash
git clone https://github.com/1bkunnn-cyber/project-code-study.git
```

将完整的 `project-code-study` 目录复制或链接到宿主支持的 Skill 目录。常见位置：

```text
Claude Code 用户级：~/.claude/skills/project-code-study
Codex 用户级：      ~/.codex/skills/project-code-study
项目级：            <project>/<host-skill-directory>/project-code-study
```

具体发现路径和调用语法以当前宿主为准。请保留仓库内的 `skills/project-study-document` 子目录，主 Skill 在结束阶段会显式读取该伴生 Skill。

## 快速开始

### 建立学习任务

```text
请使用 $project-code-study 带我学习这个项目。
项目：<本地路径或 GitHub URL>
目标：<读懂 / 复现 / 修改 / 研究扩展>
基础：<Python、框架、数学和领域基础>

请先确认学习记录权限，扫描相关源码并生成运行场景路线；本轮只完成 Step 0。
```

### 从精确位置继续

```text
请使用 $project-code-study 继续主线，从 PROJECT_STUDY_LOG.md 的主线学习锚点开始。本轮只学习一个运行节点。
```

### 提出支线问题

```text
这是当前节点的支线问题：<问题>
请完整回答并记录 Q-ID；最后告诉我应回到主线的哪个节点。
```

### 重建不合理的路线

```text
请重新扫描相关源码，分别建立训练、推理和评估调用图，列出概念依赖，并把源码阶段重排成一次一个节点的微 Step。先展示路线，不开始讲解。
```

更多可复制提示见 [`references/user-prompts.md`](references/user-prompts.md)。

## 输出、结构与校验

### 主要输出文件

| 文件 | 作用 |
| --- | --- |
| `PROJECT_STUDY_LOG.md` | schema 4.0；紧凑的路线、状态、证据、修正和索引 |
| `PROJECT_STUDY_QA.md` | schema 1.0；完整问题、追问、答案、反馈和关联记录 |
| `PROJECT_STUDY_DOCUMENT.md` | schema 1.1；经用户同意后生成、覆盖每个 Step 知识的最终学习文档 |

旧 `PROJECT_STUDY_LOG.md` schema 3.1 仍可校验。迁移旧日志必须先获得用户授权并保留备份，不能静默覆盖原记录。

旧版最终学习文档 schema 1.0 仍可进行结构校验；新生成文档使用 schema 1.1，并要求通过源日志对账来证明所有已完成 Step 均已覆盖。

### 仓库结构

| 路径 | 职责 |
| --- | --- |
| [`SKILL.md`](SKILL.md) | 主 Skill 的触发范围、边界和工作流 |
| [`assets/PROJECT_STUDY_LOG.template.md`](assets/PROJECT_STUDY_LOG.template.md) | 主日志 schema 4.0 模板 |
| [`assets/PROJECT_STUDY_QA.template.md`](assets/PROJECT_STUDY_QA.template.md) | Q&A schema 1.0 模板 |
| [`references/runtime-trace-protocol.md`](references/runtime-trace-protocol.md) | 场景调用图、概念依赖和动态微 Step |
| [`references/learning-ledger-protocol.md`](references/learning-ledger-protocol.md) | 双文档创建、读取、写入、压缩和迁移 |
| [`references/question-protocol.md`](references/question-protocol.md) | 提问、追问、主动回忆和规范修正 |
| [`references/comparison-extension-protocol.md`](references/comparison-extension-protocol.md) | 相关方法、相似思想与模块组合分析 |
| [`references/quality-rubric.md`](references/quality-rubric.md) | 证据、路线、掌握和完成门槛 |
| [`scripts/validate_learning_ledger.py`](scripts/validate_learning_ledger.py) | 校验主日志、Q&A 和旧版日志 |
| [`skills/project-study-document/SKILL.md`](skills/project-study-document/SKILL.md) | 伴生学习文档 Skill |
| [`skills/project-study-document/assets/PROJECT_STUDY_DOCUMENT.template.md`](skills/project-study-document/assets/PROJECT_STUDY_DOCUMENT.template.md) | 最终文档 schema 1.1 模板 |
| [`skills/project-study-document/scripts/validate_study_document.py`](skills/project-study-document/scripts/validate_study_document.py) | 校验最终学习文档 |

### 校验模板

```powershell
python scripts/validate_learning_ledger.py assets/PROJECT_STUDY_LOG.template.md --template
python scripts/validate_learning_ledger.py assets/PROJECT_STUDY_QA.template.md --template
python skills/project-study-document/scripts/validate_study_document.py skills/project-study-document/assets/PROJECT_STUDY_DOCUMENT.template.md --template
```

### 校验生成后的学习文档

schema 1.1 必须同时提供源学习日志。验证器会对账所有 `done` / `skipped` Step、检查 `UNIT-` 复习单元映射，并拒绝未覆盖 Step、缺失源日志或内容过薄的复习单元：

```powershell
python skills/project-study-document/scripts/validate_study_document.py PROJECT_STUDY_DOCUMENT.md --ledger PROJECT_STUDY_LOG.md
```

## 适用目标与证据边界

| 目标 | 可验证结果 |
| --- | --- |
| 读懂 | 能从入口追踪关键路径并解释节点参数、调用、Shape 与设计作用 |
| 复现 | 能补齐环境、数据、配置、命令、随机性和评估协议 |
| 修改 | 能预测替换模块、参数或目标函数的影响并设计验证 |
| 研究扩展 | 能比较论文与实现，提出有对照、有消融、可证伪的改进问题 |

Skill 不承诺自动运行任意仓库、替代实验验证或凭空补齐缺失材料。它明确区分：

- `已确认`：当前材料直接支持；
- `可推断`：由现有证据推导，但可能被新证据推翻；
- `背景知识`：领域常识，不代表当前仓库必然如此实现；
- `待验证`：缺少足够证据。

未读取的实现细节不得凭模型记忆补全；论文主张、当前代码、运行结果和背景知识必须分开；记录中不保存完整聊天、隐藏推理、凭据或无关隐私；文件写入、命令、联网和源码修改始终受用户授权与宿主权限约束。

## License

MIT，参见 [`LICENSE`](LICENSE)。

</details>

---

<a id="english"></a>

<details>
<summary><strong>English</strong></summary>

## Overview

`project-code-study` is an evidence-grounded source-code learning workflow for Claude Code, Codex, and other Agent Skills hosts. It is not a Python package or a prompt that merely translates code line by line. It scans a repository, reconstructs real runtime paths such as training, inference, and evaluation, and then divides source study into micro-steps that cover one call node, class, or function at a time.

Two persistent Markdown files preserve the learning process. The main ledger stores the route, state, evidence, and correction index; the Q&A file stores learner questions, follow-ups, complete answers, and teaching feedback. After every learning step and question has been closed, the main skill asks for explicit consent before handing the evidence to a bundled companion skill that creates a traceable final study document.

### What it provides

| Capability | Behavior |
| --- | --- |
| Repository-specific route | Scans the current repository and builds scenario call graphs and conceptual dependencies instead of forcing a generic Backbone / Transformer / Head outline |
| Runtime-path teaching | Follows actual calls from an entry point rather than filenames, imports, or directory order |
| Micro-step study | Expands the source phase into dynamic `Step 4.x` units, each covering one call node, class, or function |
| Multi-scenario coverage | Traces `train`, `infer`, and `eval` separately, plus `export` and `deploy` when they exist |
| Mastery verification | Uses active recall, source tracing, shape derivation, and change prediction to test understanding |
| Question closure | Gives every substantive question and follow-up a stable ID and always provides a complete reference answer with evidence |
| Canonical corrections | Stores the old wording, corrected wording, rationale, and impact so stale claims do not reappear later |
| Mainline anchor | Returns the learner to the exact runtime node after answering a side question |
| Comparison and extension | Compares same-task methods, same-bottleneck methods, analogous ideas, and composable modules |
| Composition review | Evaluates module “stitching” through interfaces, shapes, objectives, stability, cost, prior work, and ablations |
| Recoverable memory | Loads only hot state and linked records during normal study to control long-context growth |
| Final study document | After all steps and questions close, generates `PROJECT_STUDY_DOCUMENT.md` with consent; every completed Step maps to a standalone relearning unit, with high-impact learner questions preserved |

## Two-skill architecture

The repository contains two skills with separate responsibilities:

1. [`project-code-study`](SKILL.md) scans the project, creates the route, teaches one node at a time, records questions and corrections, and audits mastery.
2. [`project-study-document`](skills/project-study-document/SKILL.md) runs only after study is complete, questions are closed, and the learner explicitly agrees. It synthesizes the accumulated evidence into a final Markdown document.

The main skill explicitly hands off to the companion after the completion gates pass. The companion does not participate in daily teaching and never treats silence as consent to generate a document.

## Problems addressed

| Common failure | How the workflow handles it |
| --- | --- |
| Applying the same generic architecture outline to every model | Scans the repository first and generates a route from its real runtime scenarios |
| Explaining the full architecture before the modules are understood | Teaches runtime nodes first, then reconstructs the architecture from mastered components |
| Packing many classes and functions into one step | Creates dynamic micro-steps with one node, class, or function per unit |
| Covering only `model.forward()` and missing matchers, objectives, or post-processing | Builds separate scenario graphs and performs a coverage audit |
| Replying “mostly correct” without teaching the missing answer | Always returns a judgment, correct parts, gaps, full answer, evidence, and state impact |
| Losing follow-up questions after the first exchange | Persists every substantive question in Q&A and keeps its status indexed in the main ledger |
| Losing the main lesson after syntax detours | Maintains one precise mainline anchor and reports where to resume |
| Correcting a claim in chat but reusing the stale claim in the final notes | Tracks corrections and stale status; later teaching and synthesis use canonical wording only |
| Reloading an ever-growing monolithic log every turn | Separates compact state from high-growth Q&A and reads only relevant records by default |
| Ending with a chat transcript instead of reusable learning material | Generates one structured, evidence-indexed Markdown document after explicit consent |

## Workflow

```text
Repository, paper, and runtime evidence
        ↓
Step 0: project map, learning goal, and evidence boundary
        ↓
Steps 1–2: task background, related methods, representative input, and data path
        ↓
Step 3: identify runtime scenarios, call graphs, and conceptual dependencies
        ↓
Step 4.x: learn one node at a time in real call order
        ↓
Active recall / source tracing / shape derivation / change prediction
        ↓
Step 5: reconstruct the complete architecture from mastered nodes and map it to the paper
        ↓
Step 6+: objectives, training, inference, evaluation, reproduction, and experiments
        ↓
Coverage audit, method comparison, module composition, and research extensions
        ↓
Confirm that no questions remain → ask whether to generate the final study document
```

Step numbers are an adaptable scaffold, not a universal syllabus. The actual count and order depend on repository entry points, runtime scenarios, conceptual dependencies, and learner goals.

### Runtime order, not file order

The skill first scans the relevant source for coverage, then selectively reads what the current node requires. Teaching order follows calls from a concrete scenario entry point rather than directory order, import order, or source layout.

For example, a module used only to calculate a training objective belongs on the objective/loss path, not inside the model forward path. A concept that is not a callable symbol but is required to understand the next node becomes a dependency micro-step.

### One node at a time

Each source micro-step identifies at least:

- the active runtime scenario and the node’s place in the route;
- upstream caller, current symbol, and downstream node;
- exact file, class, function, or configuration location;
- key parameters, non-obvious syntax, input/output shapes, and local logic;
- design motivation, engineering risks, and impact on the next node;
- current evidence, unresolved items, and a verifiable mastery task.

An explanation being delivered, viewed, or written to the ledger does not prove mastery. Progress occurs only after the relevant verification gate is satisfied.

## Persistent learning memory

### `PROJECT_STUDY_LOG.md`

The main ledger is a compact state and index layer containing:

- current step, scenario, node, exact resume point, and one next action;
- repository-specific routes, conceptual dependencies, node states, and mastery evidence;
- source, paper, and runtime evidence; open questions, misconceptions, and canonical corrections;
- indexes for questions, experiments, comparisons, reviews, milestones, and session summaries.

### `PROJECT_STUDY_QA.md`

The Q&A file stores high-growth interaction details:

- new questions, follow-ups, and syntax questions;
- active-recall answers, evaluations, and complete reference answers;
- learner insights, teaching feedback, and route adjustments;
- links to node, evidence, misconception, and correction IDs.

Normal continuation reads only the main ledger’s hot state and the Q&A records linked to the current task. Full history is loaded only for audits, migration, or final synthesis. Every successful write is read back for verification; a failed write is reported as `unsaved`.

## Question, answer, and correction loop

Every substantive question receives a stable `Q-` ID. After a learner answers an active-recall question, the workflow provides the following whether the answer was correct or not:

```text
Judgment
→ Correct parts
→ Missing or incorrect parts
→ Complete reference answer
→ Source / paper / runtime evidence
→ Impact on previous claims and mastery state
→ Save receipt and next action
```

When a learner question causes an earlier explanation to be corrected, the record stores the original wording, canonical wording, evidence, impact scope, and stale status. Future teaching and the final study document use the latest canonical wording only.

## Comparisons, extensions, and module composition

Comparisons are not limited to another model for the same task. They are selected by learning and research value:

1. **Same-task methods** compare modeling and engineering trade-offs under the same evaluation goal.
2. **Same-bottleneck methods** compare solutions to the same limitation, error source, or optimization problem.
3. **Analogous ideas** identify structurally similar mechanisms in other tasks or domains.
4. **Composable modules** examine whether two components should be integrated and how to validate the result.

Module “stitching” is not automatically presented as innovation. Composition analysis checks interfaces and shapes, objectives, optimization stability, runtime cost, prior work, ablation design, and performance attribution, while separating engineering integration from research contribution.

## Final Markdown study document

Completion uses a two-stage handshake:

1. After all planned steps and audits pass, the workflow first asks whether the learner has more questions. It continues answering and recording them for as long as needed.
2. Only after the learner explicitly says there are no more questions does it ask whether to generate `PROJECT_STUDY_DOCUMENT.md`.

Generation requires explicit consent. The companion skill then reads the full ledger and Q&A history, revalidates key claims, and creates a standalone relearning resource rather than a transcript.

Every completed Step and micro-step receives a coverage row and maps to one or more `UNIT-` relearning units. A unit cannot be only a one-line takeaway: it must contain prerequisites, a complete explanation, runtime position, source and evidence, inputs/outputs/shapes/formulas, design trade-offs, important questions and corrections, a self-check, and a reference answer. Closely related Steps may share a unit to avoid repetition, but knowledge unique to any Step cannot be omitted. Default content includes:

- project task, evidence scope, and learning outcomes;
- complete Step knowledge coverage and standalone relearning units;
- real call paths for training, inference, evaluation, and other applicable scenarios;
- core source nodes organized by runtime and conceptual dependencies;
- data, shapes, objectives, training, inference, and evaluation;
- paper-to-code mapping, related methods, and module composition;
- important learner questions that materially changed understanding, with canonical answers;
- misconceptions, corrections, failures, limitations, unresolved items, and next actions;
- indexes for source, papers, runtime records, and learning artifacts.

Important questions are selected by learning impact—for example, questions that corrected a conclusion, exposed a misconception, involved a core runtime node, linked mathematics to implementation, affected reproduction, enabled a comparison, or were repeatedly emphasized. The document separates stable conclusions from tentative interpretations and preserves failures and limitations.

## Installation

Clone the repository:

```bash
git clone https://github.com/1bkunnn-cyber/project-code-study.git
```

Copy or link the complete `project-code-study` directory into a skill directory supported by your host. Common locations include:

```text
Claude Code user scope: ~/.claude/skills/project-code-study
Codex user scope:       ~/.codex/skills/project-code-study
Project scope:          <project>/<host-skill-directory>/project-code-study
```

Discovery paths and invocation syntax depend on the host. Keep the bundled `skills/project-study-document` directory intact; the main skill reads it explicitly during the final handoff.

## Quick start

### Start a study task

```text
Use $project-code-study to teach me this project.
Project: <local path or GitHub URL>
Goal: <understand / reproduce / modify / research extension>
Background: <Python, framework, mathematics, and domain knowledge>

First confirm permission for persistent study records, scan the relevant source,
and generate the runtime-scenario route. Complete only Step 0 in this turn.
```

### Resume from the exact point

```text
Use $project-code-study to resume the main route from the mainline anchor in
PROJECT_STUDY_LOG.md. Teach only one runtime node in this turn.
```

### Ask a side question

```text
This is a side question for the current node: <question>
Answer it completely, save its Q-ID, and tell me exactly which mainline node to resume.
```

### Rebuild a weak route

```text
Rescan the relevant source, build separate training, inference, and evaluation call graphs,
list conceptual dependencies, and reorder the source phase into one-node micro-steps.
Show the route first without beginning the lesson.
```

More copyable prompts are available in [`references/user-prompts.md`](references/user-prompts.md).

## Outputs, structure, and validation

### Main output files

| File | Purpose |
| --- | --- |
| `PROJECT_STUDY_LOG.md` | Schema 4.0 compact route, state, evidence, correction, and index ledger |
| `PROJECT_STUDY_QA.md` | Schema 1.0 full questions, follow-ups, answers, feedback, and links |
| `PROJECT_STUDY_DOCUMENT.md` | Schema 1.1 final study document with complete Step knowledge coverage, generated after explicit consent |

Legacy `PROJECT_STUDY_LOG.md` schema 3.1 remains valid. Migration requires learner authorization and a backup; the original record must not be silently overwritten.

Legacy final study documents using schema 1.0 remain structurally valid. Newly generated documents use schema 1.1 and must be audited against the source ledger to prove that every completed Step is covered.

### Repository structure

| Path | Responsibility |
| --- | --- |
| [`SKILL.md`](SKILL.md) | Main skill triggers, boundaries, and workflow |
| [`assets/PROJECT_STUDY_LOG.template.md`](assets/PROJECT_STUDY_LOG.template.md) | Main ledger schema 4.0 template |
| [`assets/PROJECT_STUDY_QA.template.md`](assets/PROJECT_STUDY_QA.template.md) | Q&A schema 1.0 template |
| [`references/runtime-trace-protocol.md`](references/runtime-trace-protocol.md) | Scenario call graphs, conceptual dependencies, and dynamic micro-steps |
| [`references/learning-ledger-protocol.md`](references/learning-ledger-protocol.md) | Two-file creation, reading, writing, compaction, and migration |
| [`references/question-protocol.md`](references/question-protocol.md) | Questions, follow-ups, active recall, and canonical corrections |
| [`references/comparison-extension-protocol.md`](references/comparison-extension-protocol.md) | Related methods, analogous ideas, and module composition |
| [`references/quality-rubric.md`](references/quality-rubric.md) | Evidence, route, mastery, and completion gates |
| [`scripts/validate_learning_ledger.py`](scripts/validate_learning_ledger.py) | Main ledger, Q&A, and legacy-ledger validator |
| [`skills/project-study-document/SKILL.md`](skills/project-study-document/SKILL.md) | Companion final-document skill |
| [`skills/project-study-document/assets/PROJECT_STUDY_DOCUMENT.template.md`](skills/project-study-document/assets/PROJECT_STUDY_DOCUMENT.template.md) | Final document schema 1.1 template |
| [`skills/project-study-document/scripts/validate_study_document.py`](skills/project-study-document/scripts/validate_study_document.py) | Final study document validator |

### Validate bundled templates

```powershell
python scripts/validate_learning_ledger.py assets/PROJECT_STUDY_LOG.template.md --template
python scripts/validate_learning_ledger.py assets/PROJECT_STUDY_QA.template.md --template
python skills/project-study-document/scripts/validate_study_document.py skills/project-study-document/assets/PROJECT_STUDY_DOCUMENT.template.md --template
```

### Validate a generated study document

Schema 1.1 requires the source learning ledger. The validator reconciles every `done` / `skipped` Step, checks `UNIT-` relearning-unit mappings, and rejects uncovered Steps, a missing ledger, or units that are too thin to support relearning:

```powershell
python skills/project-study-document/scripts/validate_study_document.py PROJECT_STUDY_DOCUMENT.md --ledger PROJECT_STUDY_LOG.md
```

## Goals and evidence boundaries

| Goal | Verifiable outcome |
| --- | --- |
| Understand | Trace a key path from its entry point and explain node parameters, calls, shapes, and design role |
| Reproduce | Account for environment, data, configuration, commands, randomness, and evaluation protocol |
| Modify | Predict the effect of replacing a module, parameter, or objective and design a validation |
| Research extension | Compare paper and implementation and propose controlled, ablatable, falsifiable improvements |

The skill does not promise to execute every repository automatically, replace empirical validation, or invent missing materials. It distinguishes:

- `confirmed`: directly supported by current evidence;
- `inferred`: derived from current evidence but falsifiable by new evidence;
- `background`: domain knowledge that may not describe this repository;
- `unverified`: insufficient evidence.

Unread implementation details must not be filled in from model memory. Paper claims, current code, runtime results, and background knowledge remain separate. Study records do not store full chats, hidden reasoning, credentials, or irrelevant private data. File writes, commands, network access, and source changes remain subject to user authorization and host permissions.

## License

MIT. See [`LICENSE`](LICENSE).

</details>
