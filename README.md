<div align="center">

# Project Code Study

### Evidence-grounded, graduate-level learning for real code repositories.

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-111827?style=for-the-badge)](https://agentskills.io/)
[![Claude](https://img.shields.io/badge/Claude-supported-D97706?style=for-the-badge)](https://claude.ai/)
[![Codex](https://img.shields.io/badge/Codex-supported-10A37F?style=for-the-badge)](https://openai.com/codex/)
[![GitHub stars](https://img.shields.io/github/stars/1bkunnn-cyber/project-code-study?style=for-the-badge)](https://github.com/1bkunnn-cyber/project-code-study/stargazers)

[中文](#中文) · [English](#english) · [Prompt Pack](references/user-prompts.md) · [Feedback Loop](#反馈闭环)

</div>

<details open>
<summary id="中文"><strong>中文介绍</strong></summary>

## 这是什么

`project-code-study` 是一个面向计算机专业研究生的通用 Agent Skill，用于系统学习 GitHub 上的深度学习、机器学习和 Python 项目。

它不只是让大模型“解释代码”，而是建立一条可持续的学习流程：读取真实项目证据，结合论文和运行结果，按 Step 推进，追踪调用关系与 Tensor Shape，检查用户是否真正理解，并把每次学习沉淀为固定格式的 Markdown 记录。

适合学习 FCN、U-Net、YOLO、Transformer、扩散模型、推荐系统，以及其他 PyTorch 或 Python 项目。

## 核心能力

| 学习需求 | Skill 提供的能力 |
| --- | --- |
| 认识整个项目 | 目录地图、入口脚本、训练/推理主流程和证据边界 |
| 精读关键源码 | 参数、语法、调用关系、Shape、数学动机和工程细节 |
| 连接论文与代码 | 论文描述、当前实现、工程改动和可能原因的对照 |
| 防止大模型幻觉 | 证据等级、置信度、缺失证据、冲突记录和版本检查 |
| 持续学习 | 固定模板的 `PROJECT_STUDY_LOG.md`、掌握度地图、复习队列和会话日志 |
| 根据用户反馈调整 | 用户心得、问题反馈、评分、AI 调整和下一行动形成闭环 |
| 最终复盘 | 生成包含代码、论文、Shape、实验、问题和盲点的 Markdown 知识库 |

## Quick Start

### 1. 安装

把整个文件夹放入你的 Agent Skills 目录：

```text
Claude Code:   ~/.claude/skills/project-code-study
Codex:         ~/.codex/skills/project-code-study
项目级安装:    <project>/.claude/skills/project-code-study
```

也可以在支持 Agent Skills 的工具中直接导入这个文件夹。

### 2. 复制提示词模板

给用户复制使用的提示词模板在这里：

[`references/user-prompts.md`](references/user-prompts.md)

它不是一个 skill，而是配合本 skill 使用的辅助提示词文档。建议用法：

| 场景 | 使用位置 |
| --- | --- |
| 第一次对话引入 skill | `Prompt 1. First Session` |
| 每次只推进一个学习 Step | `Prompt 2. Continue One Step` |
| 学习中追加追问 | `Prompt 3. Add A User Question` |
| 填写心得和反馈后让 AI 调整 | `Prompt 3A. Fill The Reflection And Feedback Areas` |
| 中断后恢复学习 | `Prompt 5. Resume After A Break` |
| 最终生成 Markdown 笔记 | `Prompt 8. Generate The Final Markdown Knowledge Base` |

### 3. 开始学习

```text
请使用 $project-code-study，带我以计算机专业研究生的深度学习这个项目。

项目路径或 GitHub 地址：<项目路径或链接>
论文 PDF、arXiv 或 DOI：<论文材料，没有可以写无>
我的目标：<读懂 / 复现 / 修改 / 研究扩展>
```

大模型会先询问是否授权创建或维护学习记录。获得授权后，它必须把固定模板复制到项目根目录：

```text
assets/PROJECT_STUDY_LOG.template.md
                    ↓ 原样复制
项目根目录/PROJECT_STUDY_LOG.md
```

复制完成后才初始化项目字段，避免不同项目产生不同格式的学习记录。

### 4. 继续学习

```text
请读取 PROJECT_STUDY_LOG.md，先处理尚未解决的用户反馈，再继续当前项目的下一个 Step。
只推进一个 Step，完成后先给我主动回忆问题，不要自动跳到下一个 Step。
```

## 反馈闭环

学习记录底部固定保留两个用户区域：第 15 节记录心得，第 16 节记录问题与反馈。AI 只能读取用户原文，并在指定列写入回应、状态和调整。

第 16 节是类似 Excel 的固定表格：

| Feedback ID | Step | 类型 | 用户问题或反馈 | 希望得到什么 | 评分 | 状态 | AI 调整与下一行动 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FB-001 | Step 2 | shape | 这里的尺寸变化没有看懂 | 想看完整追踪 | 2 | new |  |

大模型每次开始学习前，优先读取 `new`、`in-progress`、`retest-due`、评分低于 3 或重复出现的反馈，然后调整讲解速度、代码粒度、前置知识、Shape 图、论文背景、实践练习或复习问题。

## 学习路线

```text
Step 0   项目地图与证据边界
Step 1   任务背景与论文问题
Step 2   数据与预处理
Step 3   整体模型架构
Step 4   核心模块源码精读
Step 5   论文到代码映射
Step 6   Loss、后处理与评价指标
Step 7   训练循环与配置系统
Step 8   推理、部署与复现实验
Step 9   全局上下文审计与盲点发现
Step 10  研究生级综合复盘
```

## 证据和防幻觉

重要结论区分为 `已确认`、`可推断`、`背景知识` 和 `待验证`。没有证据时必须明确写 `当前材料中未看到证据`，不能编造源码、实验或论文结论，也不能假装调用不存在的 RAG 或向量库。

## 校验和结构

固定学习记录 schema 为 `3.1`，模板位于 [`assets/PROJECT_STUDY_LOG.template.md`](assets/PROJECT_STUDY_LOG.template.md)。校验命令：

```powershell
python D:\skills\project-code-study\scripts\validate_learning_ledger.py <项目根目录>\PROJECT_STUDY_LOG.md
```

## 贡献

欢迎提交真实学习案例、用户反馈机制改进、上下文丢失或幻觉问题，以及 Claude、Codex、Cursor 等宿主的兼容性测试。如果这个 Skill 帮助你读懂研究项目，欢迎点 Star。

</details>

<details>
<summary id="english"><strong>English</strong></summary>

## What Is It?

`project-code-study` is a cross-agent Agent Skill for graduate-level study of GitHub repositories, especially deep-learning, machine-learning, PyTorch, and Python projects.

It does more than explain code. It creates a durable learning workflow: inspect real evidence, connect papers to implementation, study one step at a time, trace calls and tensor shapes, test whether the learner can actually use the knowledge, and preserve the evolving study state in a stable Markdown ledger.

## Core Capabilities

| Learning need | What the skill provides |
| --- | --- |
| Understand the repository | Project map, entrypoints, train/inference flow, and evidence boundary |
| Read research code | Parameters, syntax, calls, tensor shapes, math, and engineering details |
| Connect paper and code | Paper description, current implementation, deviations, and possible reasons |
| Reduce hallucinations | Evidence levels, confidence, missing evidence, conflicts, and revision checks |
| Learn over time | A fixed `PROJECT_STUDY_LOG.md` template, mastery map, review queue, and session log |
| Adapt to the learner | User reflections, feedback, ratings, AI adjustments, and next actions |
| Finish with durable notes | A Markdown knowledge base covering code, paper, shapes, experiments, questions, and blind spots |

## Quick Start

### 1. Install

Copy the whole folder into your host's Agent Skills directory:

```text
Claude Code:    ~/.claude/skills/project-code-study
Codex:          ~/.codex/skills/project-code-study
Project-local:  <project>/.claude/skills/project-code-study
```

### 2. Copy The Prompt Pack

The copy-ready user prompt templates are here:

[`references/user-prompts.md`](references/user-prompts.md)

This file is not a skill. It is an auxiliary prompt pack designed to be used with this skill. Recommended entries:

| Scenario | Prompt to use |
| --- | --- |
| Start the first conversation with the skill | `Prompt 1. First Session` |
| Continue exactly one learning step | `Prompt 2. Continue One Step` |
| Ask an extra question during a step | `Prompt 3. Add A User Question` |
| Let the AI process reflection and feedback rows | `Prompt 3A. Fill The Reflection And Feedback Areas` |
| Resume after a break | `Prompt 5. Resume After A Break` |
| Generate the final Markdown knowledge base | `Prompt 8. Generate The Final Markdown Knowledge Base` |

### 3. Start a study track

```text
Use $project-code-study to guide me through this repository at graduate depth.

Project path or GitHub URL: <path or URL>
Paper PDF, arXiv, or DOI: <paper or none>
Target outcome: <understand / reproduce / modify / research-extend>
```

After asking for write authorization, the agent copies the canonical asset exactly:

```text
assets/PROJECT_STUDY_LOG.template.md
                    -> project-root/PROJECT_STUDY_LOG.md
```

Only after the copy does it initialize project-specific fields. Existing ledgers are never overwritten.

### 4. Continue

```text
Read PROJECT_STUDY_LOG.md, handle unresolved user feedback first, then continue one step.
Ask active-recall questions when the step is complete and wait for my answer.
```

## Feedback Loop

The bottom of every ledger contains two fixed user-owned areas: Section 15 for reflections and Section 16 for questions and feedback. The AI preserves the user's wording and only adds response, status, and adjustment fields.

Section 16 works like a lightweight spreadsheet:

| Feedback ID | Step | Type | User question or feedback | Desired response | Rating | Status | AI adjustment and next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FB-001 | Step 2 | shape | I cannot follow this dimension change | Show the full trace | 2 | new |  |

Before each session, the agent prioritizes `new`, `in-progress`, `retest-due`, low-rated, and recurring feedback. It changes the pace, code granularity, prerequisites, shape tracing, paper context, practice task, or review format.

## Learning Route

```text
Step 0   Project map and evidence boundary
Step 1   Task background and paper problem
Step 2   Data and preprocessing
Step 3   Overall architecture
Step 4   Core source reading
Step 5   Paper-to-code mapping
Step 6   Loss, post-processing, and metrics
Step 7   Training loop and configuration
Step 8   Inference, deployment, and reproduction
Step 9   Global context audit and blind spots
Step 10  Graduate-level synthesis
```

## Evidence and Anti-Hallucination Rules

Important claims are separated into `Confirmed`, `Inferred`, `Background`, and `Unverified`. When evidence is missing, the agent must say so explicitly. It must not invent files, functions, parameters, results, or paper claims, and it must not pretend to query a RAG database or paper library that the host did not provide.

## Validation

The fixed ledger schema is `3.1`:

```bash
python scripts/validate_learning_ledger.py <project-root>/PROJECT_STUDY_LOG.md
```

The validator checks the schema, fixed headings, table columns, feedback areas, and uninitialized placeholders.

## Contributing

Contributions are welcome: tested study cases, feedback-loop improvements, cross-host compatibility reports, and concrete hallucination or context-loss fixes. If this skill helps you understand a research repository, starring it helps other students find the workflow.

</details>

## License

No license has been selected yet. Add one before public redistribution if you want to define reuse terms.

## Repository

[GitHub](https://github.com/1bkunnn-cyber/project-code-study) · [Issues](https://github.com/1bkunnn-cyber/project-code-study/issues)
