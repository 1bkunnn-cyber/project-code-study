# project-code-study 5.4.0 修缮报告

## 目标

将 Engramory-inspired 连续性记忆从“可选协议说明”落实为项目级、用户同意后才初始化的工作流，避免 Skill 在被学习项目中静默创建记忆目录。

## 主要改动

| 缺口 | 修复 | 证据 |
| --- | --- | --- |
| 记忆目录创建前没有明确同意门禁 | `sync_protocol_memory.py init` 强制 `--user-consent` | `scripts/sync_protocol_memory.py` |
| 用户不知道记忆存放位置 | 明确创建于 `<PROJECT_ROOT>/.project-study-memory/` | `references/continuity-memory-protocol.md`、`references/user-prompts.md` |
| 用户拒绝或未回答时可能继续使用记忆 | 增加 `memory-consent-pending` 规则；pending 阻断推进 | `scripts/interaction_state.py` |
| 提示词没有初始化确认模板 | 增加 Skill 自动询问、启用/拒绝/含糊回答分支 | `references/user-prompts.md` |

## 验证

- 全部测试：47 个，46 个通过，1 个真实宿主/跨模型测试明确跳过。
- Skill quick validation：通过。
- Skill audit：`missing_refs=0`。
- 不写 `.pyc` 的静态 Python `compile()`：通过。
- `git diff --check`：通过。

真实宿主是否会自动询问用户并执行 `init --user-consent`，仍需在目标宿主中进行 forward-test；Skill 内部已经对初始化命令和推进决策提供可执行门禁。
