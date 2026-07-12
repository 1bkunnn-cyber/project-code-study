# Project Code Study

> A Codex skill for graduate-level source-code study with paper-code alignment, evidence-grounded explanations, step-by-step learning, and a persistent learning ledger.

`project-code-study` 是一个面向计算机专业研究生的 Codex skill，用来系统学习 GitHub 上的深度学习/机器学习项目，例如 FCN、UNet、YOLO、Transformer、推荐系统或其他 PyTorch 项目。

它的目标不是“泛泛讲一下项目”，而是让大模型在真实代码、论文、配置和运行证据的约束下，像源码阅读导师 + 学习记录员一样，带你逐步读懂项目。

## Highlights

- **研究生级源码讲解**：覆盖参数、代码逻辑、调用关系、语法、shape 变化、模块作用、模块关系和工程细节。
- **论文与代码对照**：区分论文描述、当前实现、工程化改动和可能原因。
- **强防幻觉规则**：没有看到证据时必须说明 `当前材料中未看到证据`，不能编造文件、函数、参数、实验或论文结论。
- **Step-by-step 学习路线**：从项目地图、论文问题、数据流、模型结构到训练、推理、审计和复盘。
- **学习记录员机制**：维护 `PROJECT_STUDY_LOG.md`，记录学习过程、问题、遗漏点、不确定事项和下一步调整。
- **最终 Markdown 笔记**：学完后生成可复习的知识库式源码学习笔记。
- **用户辅助提示词**：提供可复制的开场、追问、继续学习、盲点审计和最终总结提示词。

## When To Use

Use this skill when you want to:

- follow a GitHub project to learn deep-learning or ML engineering;
- understand how a paper is implemented in code;
- read a training/inference pipeline systematically;
- trace tensor shapes through model modules;
- turn scattered Q&A into durable Markdown notes;
- force the model to stay evidence-based instead of hallucinating implementation details.

The skill is designed for explicit invocation:

```text
Use $project-code-study to guide me through this project source code at graduate depth.
```

## Learning Workflow

The skill uses a staged route and adapts it to the actual project.

| Step | Focus |
| --- | --- |
| 0 | Project map: files, entrypoints, evidence scope |
| 1 | Task background and paper problem |
| 2 | Data input and preprocessing |
| 3 | Whole model architecture |
| 4 | Core module source reading |
| 5 | Paper-to-code mapping |
| 6 | Loss, assignment, post-processing, metrics |
| 7 | Training loop and configuration system |
| 8 | Inference, visualization, deployment, reproduction |
| 9 | Global context audit and blind-spot review |
| 10 | Graduate-level synthesis |

Each step asks the model to explain:

- learning goal and evidence source;
- class/function/config parameters;
- code blocks and syntax;
- upstream/downstream calls;
- tensor shape flow;
- paper/math meaning;
- module role and relationships;
- engineering details and debugging advice;
- overlooked points and next-step adjustments.

## Learning Ledger

Before Step 0, the skill asks whether it may create or update:

```text
PROJECT_STUDY_LOG.md
```

The preferred location is the project root. If writing is not authorized or not possible, the model must keep a temporary in-chat ledger and clearly say it has not been saved.

The ledger records:

- project status and evidence inventory;
- completed steps and route changes;
- important code and shape-flow conclusions;
- user questions and answers;
- AI uncertainty and missing evidence;
- user-overlooked points;
- next-step learning suggestions;
- reusable material for the final Markdown summary.

This makes the skill behave less like a one-off explainer and more like a learning-process manager.

## Repository Structure

```text
project-code-study/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── references/
    ├── context-audit-template.md
    ├── final-summary-template.md
    ├── learning-ledger-template.md
    ├── paper-code-template.md
    ├── step-template.md
    └── user-prompts.md
```

## Reference Files

| File | Purpose |
| --- | --- |
| `SKILL.md` | Core skill instructions and behavior rules |
| `references/step-template.md` | Standard deep explanation template for each learning step |
| `references/paper-code-template.md` | Paper-to-code mapping template |
| `references/context-audit-template.md` | Step 9 blind-spot audit template |
| `references/learning-ledger-template.md` | Template for `PROJECT_STUDY_LOG.md` |
| `references/final-summary-template.md` | Final Markdown study-note template |
| `references/user-prompts.md` | User-facing copy/paste prompt pack, not a skill |
| `agents/openai.yaml` | Codex UI metadata and invocation policy |

## Quick Start

1. Put this folder under your Codex skills directory, for example:

   ```text
   D:\skills\project-code-study
   ```

2. Start a new conversation and invoke the skill:

   ```text
   请使用 $project-code-study 帮我以计算机专业研究生的深度学习这个项目源码。
   ```

3. Provide the project folder, README, paper PDF/link, and any training or inference commands you already know.

4. Let the skill create or maintain `PROJECT_STUDY_LOG.md` so later steps can build on prior learning instead of losing context.

For richer starter prompts, see:

```text
references/user-prompts.md
```

## Example Starter Prompt

```text
请使用 $project-code-study 帮我以计算机专业研究生的深度学习这个项目源码。

请先询问我是否授权你在项目文件夹中创建/维护 PROJECT_STUDY_LOG.md。
然后基于真实项目文件、README、配置、训练/推理入口、模型代码、数据处理代码和论文证据，生成 step-by-step 学习路线。

每个 step 都要覆盖参数定义、代码讲解、调用关系、语法讲解、shape 变化、模块作用、模块关系、论文对应、工程细节、易错点和下一步建议。
没有证据时请明确说：当前材料中未看到证据。

项目路径/链接：<project path or GitHub URL>
论文：<paper PDF/arXiv/DOI>
```

## Design Principles

- **Evidence first**: inspect files before explaining.
- **No fake certainty**: uncertainty is recorded, not hidden.
- **Paper-code alignment**: classic model knowledge is separated from current implementation evidence.
- **Step discipline**: one step at a time, with questions recorded.
- **Context continuity**: the learning ledger steers later explanations.
- **Graduate depth**: focus on understanding, reproduction, modification, and critique.

## Validation

Validate the skill with the Codex skill creator validator:

```powershell
$env:PYTHONUTF8='1'
python C:\Users\Administrator\.codex\skills\.system\skill-creator\scripts\quick_validate.py D:\skills\project-code-study
```

Expected result:

```text
Skill is valid!
```

## License

No license has been selected yet. Add one before publishing publicly if you want others to reuse or redistribute this skill.
