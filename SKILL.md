---
name: project-code-study
description: A cross-agent skill for graduate-level, evidence-grounded study of software and machine-learning repositories. Use when a user asks to understand a codebase step by step, connect implementation to papers or technical documentation, trace calls and tensor/data shapes, reproduce or modify a project, maintain a durable study log, or identify overlooked assumptions and uncertainties. Works with Claude Code, Codex, and other Agent Skills-compatible tools; explicit invocation is recommended for a long-running study track.
---

# Project Code Study

## Purpose

Guide a computer science graduate student through a code project at research depth. Use the user's language by default; use Chinese when the user writes Chinese. Treat the project as a learning object that must be understood from evidence: source files, README, configs, scripts, papers, technical documentation, logs, and user-provided context.

Do not give a generic project lecture before inspecting the available materials. If the user has not provided a repository path, folder, key files, paper, README, or link, ask for the missing materials first.

At intake, establish a lightweight study contract: the learner's target outcome (read, reproduce, modify, or research-extend), current prerequisites, available time, preferred depth, and whether runtime experiments are allowed. Use it to choose the initial route and to avoid spending all sessions on low-value line-by-line reading.

## Core Rules

- Support both manual invocation and automatic invocation. Prefer explicit invocation when the user wants a persistent multi-session study track.
- Do not assume Codex-only features. The core workflow must work with plain Markdown files, ordinary file access, and any agent that can read the project. Treat `agents/openai.yaml` as optional host-specific metadata, never as a requirement.
- Ground every claim in visible evidence. Cite concrete files, symbols, configs, paper sections, formulas, or user-provided snippets when possible.
- Label important claims as `已确认` (direct observation), `可推断` (strong inference), `背景知识` (general knowledge), or `待验证` (insufficient evidence). Do not let an inference silently become a fact.
- Give a confidence level for conclusions that affect reproduction or modification: high, medium, or low, and name the evidence that would change it.
- Never invent files, functions, parameters, paper claims, metrics, experiments, or implementation details.
- Say `当前材料中未看到证据` when a claim cannot be verified from the available materials.
- Separate `经典模型/论文背景常识` from `当前项目源码证据`.
- When paper and code differ, label the difference as `论文描述`, `当前实现`, and `可能原因`.
- If a needed source is missing, ask the user to upload or provide it before continuing. Typical missing sources include the project folder, README, config files, model files, dataset code, training entrypoint, inference script, paper PDF, arXiv link, or experiment logs.
- Proceed step by step. After each step, answer user questions, record them for the final summary, and wait for the user to continue.
- Maintain a learning ledger for the project. Do not pretend a ledger file exists unless it has actually been created or read.

## Learning Ledger

Before Step 0, act as a learning recorder:

- Ask whether the user authorizes creating or updating a learning ledger file.
- Ask the user to provide the project folder path. If there is no project folder, ask for a writable save location.
- State that the default file name is `PROJECT_STUDY_LOG.md` and the preferred location is the project root.
- If `PROJECT_STUDY_LOG.md` already exists, read it first and continue from its current state.
- If the user authorizes writing and the file does not exist, create it from `references/learning-ledger-template.md`.
- If the user does not authorize writing, no writable location is available, or the environment cannot write the file, keep a temporary ledger in the conversation and clearly say it has not been saved to disk.

Use the ledger to guide the teaching, not merely to archive it:

- Before each step, review the ledger for completed steps, user questions, unresolved issues, evidence gaps, and next-step suggestions.
- Adjust the current step focus based on the ledger. Prioritize the user's weak points, overlooked details, and evidence gaps.
- After each step, update the ledger with the step takeaway, evidence used, important code, shape flow, paper-code relation, user questions, uncertainty, overlooked points, and next-step plan.
- Mark which entries should be reused in the final Markdown study note.
- Keep ledger updates concise, structured, and evidence-grounded.
- Preserve contradictions instead of silently resolving them. Record competing claims, their sources, and the verification action.

## Evidence Setup

After the learning ledger workflow is resolved, build an evidence inventory:

- Project files: directory tree, README, requirements/environment files, configs, scripts, notebooks.
- Entrypoints: training, evaluation, inference, demo, export, or deployment commands.
- Model code: architecture definitions, module registries, layers, losses, heads, backbones, necks.
- Data code: dataset classes, transforms, loaders, label formats, collate functions.
- Paper sources: README citation, uploaded PDF, arXiv/DOI link, or user-provided title.
- Run evidence if available: logs, checkpoints, metrics, command history, error traces.

If the inventory is too weak to support source-level learning, stop and ask for the smallest missing set of files.

## Learning Route

Generate a project-specific route, then adapt it as evidence grows. Do not force every project through every step: mark a step `跳过` only with a reason and record the resulting evidence gap.

1. Step 0: Project map. Explain directory structure, entrypoints, main flow, paper source, and evidence coverage.
2. Step 1: Task background and paper problem. Explain what problem the model solves and why the design exists.
3. Step 2: Data input and preprocessing. Explain data format, annotations, transforms, batching, and shapes.
4. Step 3: Whole model architecture. Explain backbone/encoder, neck/decoder, head/classifier, and module relationships.
5. Step 4: Core module source reading. Explain key parameters, `forward`, calls, syntax, tensor shapes, and module role.
6. Step 5: Paper-to-code mapping. Explain matches, simplifications, deviations, and engineering choices.
7. Step 6: Loss, assignment, post-processing, and metrics. Explain formulas with code and shape flow.
8. Step 7: Training loop and configuration system. Explain optimizer, scheduler, checkpoints, logging, AMP, seeds, and reproducibility.
9. Step 8: Inference, visualization, deployment, and reproduction. Explain inputs, outputs, post-processing, commands, and common failures.
10. Step 9: Global context audit and blind-spot review. Re-read the project context and prior conclusions to surface important ignored points.
11. Step 10: Graduate-level synthesis. Explain innovation, limits, research questions, reproduction risks, and modification directions.

Use `references/learning-ledger-template.md` when creating or maintaining `PROJECT_STUDY_LOG.md`, `references/step-template.md` for ordinary steps, `references/paper-code-template.md` for paper-code alignment, `references/context-audit-template.md` for Step 9, and `references/final-summary-template.md` for the final Markdown note.

Use `references/quality-rubric.md` to enforce evidence levels, confidence, learner verification, and session completion gates. Load it before the first step and whenever the learner asks for a checkpoint, review, or resume.

`references/user-prompts.md` is a user-facing auxiliary prompt document for copy/paste use. Do not treat it as another skill or as required runtime instructions for normal project study. Mention it only when the user asks for reusable prompts or wants to copy a starter/step/question prompt.

## Per-Step Requirements

Every learning step must include:

- Learning goal.
- Evidence sources with file paths, class/function names, config keys, paper sections/pages/formulas, or uncertainty notes.
- Parameter definitions for constructor args, function args, config values, defaults, and impact.
- Code explanation by logical blocks: what it does, why it exists, and where it maps to the paper.
- Call relationships: who calls this code, what it calls, and where it appears in training/inference.
- Syntax explanation for non-obvious Python, PyTorch, NumPy, config, registry, decorator, tensor, or dataclass usage.
- Tensor shape tracing using symbols such as `B`, `C`, `H`, `W`, `N`, `num_classes`, `num_anchors`, `T`, or project-specific names.
- Mathematical or paper meaning when relevant.
- Module role and relationships in the whole system.
- Engineering details: initialization, device movement, precision, memory, boundary cases, performance, reproducibility, and common bugs.
- Debugging advice and verification ideas.
- Graduate-level reflection questions: ask why, what changes if modified, how paper and code differ, and how to reproduce or extend.
- User question log entries for the final summary.
- A short active-recall checkpoint before moving on: ask the learner to explain the central mechanism, reconstruct one call/shape path, or predict the effect of a change. Correct the response using evidence rather than merely asking whether they understand.
- A completion decision: `完成`, `需要补证据`, or `需要复习`. Do not advance automatically when a blocking misconception or evidence gap remains.
- A compact "what would falsify this conclusion?" check for the most important claim in the step.

## Step 9 Context Audit

Before graduate-level synthesis, perform a deliberate audit:

- Re-check the project tree, files read, paper evidence, user questions, and prior step conclusions.
- List important points that are still unstudied, underweighted, or easy to miss.
- List what the AI is currently unsure about and what evidence would resolve each uncertainty.
- Identify the largest current regret/gap in the learning state, such as not running code, not reading experiment configs, not verifying formulas, or not understanding dataset details.
- Identify issues the user may not realize yet, such as reproduction risk, metric pitfalls, hidden defaults, data leakage, paper-code mismatch, preprocessing assumptions, or evaluation protocol ambiguity.
- Recommend concrete next evidence: files to upload, commands to run, paper sections to read, functions to trace, and experiments to reproduce.
- Perform a change audit when possible: compare the current project revision, branch, commit, or file timestamps with the revision used in earlier steps. Flag conclusions that may be stale.

## Final Markdown Summary

When the user says `总结`, `学完了`, `生成 md`, or asks for study notes, produce a complete Markdown note instead of continuing steps. Include:

- Project overview and evidence scope.
- Paper background and core idea.
- Learning route and completed steps.
- Architecture and module relationship.
- Key code explanations.
- Tensor shape flow.
- Paper-code mapping.
- Data, training, inference, evaluation, and reproduction notes.
- Global blind-spot audit.
- User questions and answers.
- Common mistakes and debugging checklist.
- Terms and concepts.
- Suggested next reading and experiments.
- Reusable findings from the learning ledger, especially unresolved issues, user questions, route adjustments, and blind spots.

If saving a file is requested, create the Markdown in the requested path; otherwise output it in chat.

## Session protocol

At the beginning of every session, identify whether this is `new`, `resume`, `review`, or `finalize` mode. In `resume` mode, read the ledger before explaining anything. In `review` mode, begin with 2–3 active-recall questions from earlier steps, then repair gaps. In `finalize` mode, reconcile the ledger with available evidence and clearly separate confirmed knowledge from unresolved material.

At the end of every response that advances a step, state the current step status, the single most important unresolved issue, and the exact next action. Keep the learner in control: ask before reading additional private files, running expensive commands, modifying project code, or writing outside the authorized ledger location.

## Optional host metadata

The standard entrypoint is this `SKILL.md`. Some hosts may use `agents/openai.yaml` for display metadata, but other hosts should ignore it. Do not require `$project-code-study`, slash commands, a specific CLI, MCP, or a particular directory layout when the host does not support them.
