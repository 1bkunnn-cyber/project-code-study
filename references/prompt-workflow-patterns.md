# Prompt Workflow Research and Abstraction

This reference records reusable patterns extracted from public workflow and
code-learning projects. It is not a dependency and does not authorize copying
project-specific prompts.

## Patterns adopted

| Source pattern | General abstraction | project-code-study use |
| --- | --- | --- |
| Socratic prediction, active recall, graduated hints, spaced review | Test the learner before revealing; increase scaffolding only when needed | prompts 6–8; `question-protocol.md`; durable K evidence |
| Understand → Act → Validate agent loop | Every action has a read phase, an execution phase, and a verification phase | prompts 1, 3, 11, 16; preflight and receipts |
| Discovery → Alignment → Design → Refinement | Resolve goal and evidence scope before route generation | prompts 1, 2, 14 |
| Preflight, required/optional triggers, failure stop, structured outputs | Decide whether a phase applies, stop on required failure, and return artifacts/status | prompt router and prompts 11, 17, 18 |
| Plan review checkpoints and explicit consent gates | Do not silently transition from a draft/plan to execution/finalization | prompts 15–16; readiness/finalizer |
| Hierarchical always-loaded agent instructions | Keep a small stable contract loaded and defer detail to scoped resources | continuity memory and host-enforcement boundary |

## What is intentionally not copied

- No project-specific function, framework, Q-ID, or example answer is encoded.
- User prompts do not ask the learner to maintain Q-ID, QA/LOG, receipts,
  pause tokens, or readiness fields manually.
- Prompts do not replace the machine state machine; they only select a user
  intent and provide task-local context.
- Prompts do not claim that a host will enforce a tool call. A host-level hook
  is required for a hard delivery gate.

## Research sources

- `learn-codebase`: Socratic prediction, active recall, graduated scaffolding,
  learning journal, and session-end choices —
  <https://github.com/ktaletsk/learn-codebase/blob/main/SKILL.md>
- Microsoft VS Code agent loop and planning —
  <https://github.com/microsoft/vscode-docs/blob/main/docs/copilot/concepts/agents.md>
- GitHub Copilot onboarding prompt —
  <https://docs.github.com/en/copilot/tutorials/customization-library/prompt-files/onboarding-plan>
- GitHub Awesome Copilot agent orchestration —
  <https://github.com/github/awesome-copilot/blob/main/instructions/agents.instructions.md>
- Agent.md hierarchical instruction structure —
  <https://github.com/agentmd/agent.md>
- Superpowers plan execution and review checkpoints —
  <https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md>
