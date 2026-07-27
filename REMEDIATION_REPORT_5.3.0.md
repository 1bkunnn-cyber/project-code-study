# project-code-study 5.3.0 提示词工程修缮报告

## 目标

将 `references/user-prompts.md` 从分散的提示词列表升级为贴合 Skill 状态机、事务门禁和教学输出契约的完整用户意图路由器。

## 主要改动

| 缺口 | 修复 | 证据 |
| --- | --- | --- |
| 原提示词没有总流程 | 增加 `start/recover → preflight → route → one NODE → recall/question → transaction → waiting → fresh continue` 闭环 | `user-prompts.md` §0 |
| 启动、恢复和最终化之间缺少分支 | 增加启动、方式选择、恢复、暂停、问题关闭、正式化、草稿和宿主异常模板 | §1–§18 |
| 学习方式与状态机混淆 | 明确方式选择只改变呈现，不改变 RUN/NODE、Q、receipt 或推进规则 | §2 |
| 主动回忆模板过度笼统 | 明确复述、正确/错误/缺失/表达不足、证据边界、分级纠错和 retest | §6 |
| 复合问题和支线问题不成闭环 | 先拆分意图，再独立 Q-ID、完整 QA、批量展示但全部关闭前不推进 | §5 |
| 长上下文恢复缺少动作顺序 | 先 memory/LOG/QA/readiness 预检，再修复或报告唯一下一动作 | §3、§13、§18 |
| 用户被迫重复内部控制要求 | 加入禁止委托内部记录维护的回归测试 | `tests/test_user_prompts_contract.py` |

## GitHub 模式抽象

参考并抽象了 `learn-codebase` 的预测/主动回忆/分级提示、Microsoft VS Code Agents 的 Understand→Act→Validate、GitHub Awesome Copilot 的 preflight/失败即停/结构化产物，以及 Superpowers 的计划审查和验证回环。具体映射见 `references/prompt-workflow-patterns.md`。

## 验证

- 全部测试：44 个，43 个通过，1 个既有真实宿主/跨模型测试明确跳过。
- Prompt contract：通过。
- Skill quick validation：通过。
- Skill audit：`word_count=2312`，`missing_refs=0`。
- Python UTF-8 compile：通过。
- `git diff --check`：通过。

真实宿主是否会在每轮自动加载提示词、执行 memory doctor、调用 receipt guard，仍需目标宿主 forward-test；静态测试不能宣称该行为已经强制生效。
