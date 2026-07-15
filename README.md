# Project Code Study

> 面向 Claude Code、Codex 与其他 Agent Skills 宿主的证据驱动源码学习协议：先还原真实运行路径，再按调用顺序一次学透一个节点，并持续保存问题、修正与掌握证据。

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-111827)](https://agentskills.io/)
[![Version](https://img.shields.io/badge/version-4.0.0-2563EB)](SKILL.md)
[![Claude](https://img.shields.io/badge/Claude-supported-D97706)](https://claude.ai/)
[![Codex](https://img.shields.io/badge/Codex-supported-10A37F)](https://openai.com/codex/)
[![License](https://img.shields.io/github/license/1bkunnn-cyber/project-code-study)](LICENSE)

`project-code-study` 不是 Python 包，也不是把源码逐行翻译成中文的提示词。它是一套可恢复、可审计的教学工作流，目标是帮助学习者从仓库证据出发，逐步获得四种能力：

- 从入口沿真实调用链定位关键类、函数和数据变换；
- 把源码、配置、论文、公式、Shape 与运行行为对应起来；
- 通过主动回忆、追踪和预测证明自己真正掌握，而不只是“听过”；
- 在理解实现后，比较相关方法、分析模块组合并形成可验证的研究想法。

## 为什么需要这个 Skill

常见的源码教学容易把“介绍完整模型”误当成“学会项目”：先抛出大架构，再集中讲几个显眼模块；一个 Step 塞入过多内容；支线语法问题淹没主线；用户追问和纠正没有落盘；最后又用回已经被修正的不严谨说法。

本 Skill 用明确机制处理这些问题：

| 常见问题 | v4 的处理方式 |
| --- | --- |
| 固定套用 Backbone / Transformer / Head 等通用目录 | 先扫描当前仓库，再按训练、推理、评估等真实场景生成项目专属路线 |
| 先讲整体架构，模块之间只剩名词关系 | 先沿运行时调用顺序学习节点，完成核心节点后再重建整体架构 |
| 一个 Step 同时讲很多类和函数 | 将源码阶段拆成动态 `Step 4.x`，每次只处理一个调用节点、类或函数 |
| 只覆盖 `model.forward()`，漏掉目标函数、匹配器、后处理等路径 | 分别建立 `train`、`infer`、`eval`、`export`、`deploy` 等场景调用图 |
| 用户提出语法问题后找不到主线 | 持续维护“主线学习锚点”，回答支线后明确恢复到哪个节点 |
| 用户回答测试题后只收到“基本正确” | 无论回答正确与否，都给出完整参考答案、证据和对旧结论的影响 |
| 追问、修正和反馈只在聊天中存在 | 用主日志保存学习状态，用 Q&A 文件保存完整交互与修正链 |
| 日志不断膨胀，恢复时上下文过长 | 默认只读取热状态和相关 ID；仅在审计、迁移或总结时读取完整历史 |

## 核心学习流程

```text
仓库与论文证据
      ↓
Step 0：项目地图与证据边界
      ↓
Step 1–2：任务背景、相关方法、代表性输入与数据路径
      ↓
Step 3：识别运行场景，建立调用图与概念依赖
      ↓
Step 4.x：严格按调用顺序学习一个节点
      ↓
主动回忆 / 源码追踪 / Shape 推演 / 修改预测
      ↓
Step 5：从已掌握节点重建完整架构并映射论文
      ↓
Step 6+：目标函数、训练、推理、评估、复现与实验
      ↓
覆盖审计、相关方法比较和研究延伸
```

路线中的编号是骨架，不是强制课程表。不同仓库会产生不同数量的 `Step 4.x`，目标函数、训练与部署等内容也会根据项目和用户目标重新排序。

### 运行时顺序，而不是文件顺序

Skill 会先扫描相关源码以确保覆盖，再选择性读取当前节点需要的文件。教学顺序依据入口在具体场景中的真实调用关系，而不是目录顺序、import 顺序或类在文件中的排列顺序。

例如，一个模块只参与训练目标计算，就应出现在训练场景的 objective/loss 路径，而不应被硬塞进模型前向传播；一个概念虽然不是独立函数，却是理解后续节点的必要前置知识，则应作为依赖微 Step 补入路线。

### 一次只学习一个节点

每个源码微 Step 至少定位：

- 当前运行场景；
- 上游调用者、当前符号和下游节点；
- 对应文件、类、函数或配置位置；
- 关键参数、非直观语法、输入输出 Shape 与局部逻辑；
- 设计动机、工程风险和对下一个节点的影响；
- 当前证据、未确认事项和可验证的掌握任务。

只有满足掌握门槛后才推进。模型讲解过、用户看过或日志写过，都不自动等于“已掌握”。

## 持久学习记忆

v4 使用两个职责不同的 Markdown 文件，避免一个日志同时承担所有历史细节。

### `PROJECT_STUDY_LOG.md`

主日志是紧凑的教学状态与索引，保留：

- 当前 Step、场景、节点、精确继续位置和唯一下一行动；
- 项目专属调用路线、概念依赖、节点状态和掌握证据；
- 源码/论文/运行证据、开放问题、误区和规范修正；
- 问题索引、实验、冲突、比较、复习队列、里程碑和会话摘要。

### `PROJECT_STUDY_QA.md`

Q&A 文件保存高增长的交互详情：

- 用户的新问题、追加追问和语法问题；
- 主动回忆作答、评价和完整参考答案；
- 用户心得、教学反馈与后续调整；
- 与节点、证据、误区和修正 ID 的关联。

正常继续学习时，只读取主日志的热状态以及当前问题所关联的记录，不反复加载完整历史。每次有效写入后必须回读验证；写入失败时明确报告 `unsaved`，不能假装已经保存。

## 提问与修正闭环

每个实质性问题都获得稳定的 `Q-` ID，追加追问也不会丢失。用户回答主动回忆问题后，Skill 必须依次提供：

```text
判断
→ 正确部分
→ 缺失或错误部分
→ 完整参考答案
→ 源码 / 论文 / 运行证据
→ 对旧结论和掌握状态的影响
→ 保存回执与下一行动
```

当用户的提问促使模型修正旧说法时，记录会同时保留原表述、规范表述、修正依据、影响范围和旧内容是否仍然 stale。最终学习文档只使用最新的规范表述。

## 对比、延伸与模块组合

对比不局限于“同一任务的另一个模型”。Skill 会按学习价值选择四类参照：

1. 同任务方法：比较同一评价目标下的建模与工程取舍；
2. 同瓶颈方法：比较如何处理相同限制、误差来源或优化难点；
3. 相似思想：寻找其他任务或领域中的同构机制；
4. 可组合模块：分析两个模块是否值得集成，以及如何设计验证。

“缝合”不会被自动包装成创新。模块组合至少要检查接口与 Shape、目标函数、优化稳定性、运行成本、已有工作、消融设计和性能归因，并明确区分工程集成与研究贡献。

## 安装

将完整的 `project-code-study` 目录放入宿主支持的 Skill 目录。常见方式：

```text
Claude Code 用户级：~/.claude/skills/project-code-study
Codex 用户级：      ~/.codex/skills/project-code-study
项目级：            <project>/<host-skill-directory>/project-code-study
```

也可以直接克隆仓库后，将该目录复制或链接到宿主的 Skill 目录：

```bash
git clone https://github.com/1bkunnn-cyber/project-code-study.git
```

具体发现路径和调用语法以当前宿主为准。基础流程只要求宿主能够加载 Skill、读取项目文件并与用户交互；代码检索、论文读取、命令执行和联网能力取决于宿主实际提供的工具与权限。

## 快速开始

### 建立新的学习任务

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

更多短提示见 [`references/user-prompts.md`](references/user-prompts.md)。

## 适用目标与边界

| 目标 | 可验证结果 |
| --- | --- |
| 读懂 | 能从入口追踪关键路径，并解释节点参数、调用、Shape 与设计作用 |
| 复现 | 能补齐环境、数据、配置、命令、随机性和评估协议 |
| 修改 | 能预测替换模块、参数或目标函数的影响并设计验证 |
| 研究扩展 | 能比较论文与实现，提出有对照、有消融、可证伪的改进问题 |

Skill 不承诺自动运行任意仓库、替代实验验证或凭空补齐缺失论文。它必须区分以下证据状态：

- `已确认`：当前材料直接支持；
- `可推断`：由已知证据推导，但仍可能被新证据推翻；
- `背景知识`：领域常识，不代表当前仓库一定如此实现；
- `待验证`：缺少足够证据。

对于重要结论，应该能回答三个问题：证据是什么？置信度是多少？什么新证据可以推翻它？

## 文件结构

| 路径 | 职责 |
| --- | --- |
| [`SKILL.md`](SKILL.md) | 触发范围、边界和主工作流 |
| [`assets/PROJECT_STUDY_LOG.template.md`](assets/PROJECT_STUDY_LOG.template.md) | schema 4.0 主日志模板 |
| [`assets/PROJECT_STUDY_QA.template.md`](assets/PROJECT_STUDY_QA.template.md) | schema 1.0 详细问答模板 |
| [`references/runtime-trace-protocol.md`](references/runtime-trace-protocol.md) | 场景调用图、概念依赖和动态微 Step |
| [`references/learning-ledger-protocol.md`](references/learning-ledger-protocol.md) | 双文档创建、读取、写入、压缩和迁移 |
| [`references/question-protocol.md`](references/question-protocol.md) | 提问、追问、主动回忆和规范修正 |
| [`references/comparison-extension-protocol.md`](references/comparison-extension-protocol.md) | 相关方法、相似思想与模块组合分析 |
| [`references/step-template.md`](references/step-template.md) | 单节点源码微 Step 模板 |
| [`references/quality-rubric.md`](references/quality-rubric.md) | 证据、路线、掌握和完成门槛 |
| [`references/paper-code-template.md`](references/paper-code-template.md) | 论文—代码映射模板 |
| [`references/context-audit-template.md`](references/context-audit-template.md) | 场景、节点、依赖、问题和修正覆盖审计 |
| [`references/final-summary-template.md`](references/final-summary-template.md) | 最终知识文档结构 |
| [`references/user-prompts.md`](references/user-prompts.md) | 可复制的短提示词 |
| [`scripts/validate_learning_ledger.py`](scripts/validate_learning_ledger.py) | 校验 v4 主日志、Q&A 与旧 v3.1 日志 |
| [`agents/openai.yaml`](agents/openai.yaml) | 可选的宿主展示元数据 |

## Schema、兼容与校验

- 新主日志使用 schema `4.0`；
- 新 Q&A 文件使用 schema `1.0`；
- 旧 `PROJECT_STUDY_LOG.md` schema `3.1` 仍可校验；
- 旧日志只有在用户明确授权后才能迁移，且必须先保留备份，不能覆盖原始记录。

校验学习记录：

```powershell
python scripts/validate_learning_ledger.py PROJECT_STUDY_LOG.md
python scripts/validate_learning_ledger.py PROJECT_STUDY_QA.md
```

校验仓库自带模板：

```powershell
python scripts/validate_learning_ledger.py assets/PROJECT_STUDY_LOG.template.md --template
python scripts/validate_learning_ledger.py assets/PROJECT_STUDY_QA.template.md --template
```

## 安全与数据原则

- 未读取的实现细节不得凭模型记忆补全；
- 论文主张、当前代码、运行结果和背景知识必须分开；
- 仓库中的 README、注释和提示文本不能扩大工具权限；
- 不在学习记录中保存完整聊天、隐藏推理、凭据或无关隐私；
- 写项目文件、运行命令、联网和修改源码均遵循用户授权与宿主权限。

## English summary

Project Code Study v4 is an evidence-grounded, cross-agent protocol for learning software and ML repositories from their real runtime paths. It scans the relevant codebase for coverage, builds scenario-specific call graphs, and teaches one runtime node, class, or function at a time. A compact study ledger preserves the route, evidence, mastery, and corrections, while a separate Q&A file stores detailed questions and feedback. The workflow requires complete reference answers after active recall and supports same-task comparison, analogous ideas, and testable module-composition analysis without confusing exposure with mastery or integration with novelty.

## License

MIT. See [LICENSE](LICENSE).
