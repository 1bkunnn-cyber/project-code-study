# project-code-study 6.0.0 实施与测试报告

日期：2026-08-04
分支：`codex/skill-reliability-v5`
修改前基线：`39471be818c0c40e385469e2255583717862e79f`
环境：Windows / Python 3.11.3 / Codex Desktop

## 交付结论

方案 A 已实现为机制改造：事件与恢复、分类型 QA、memory 生命周期、统一
release WAL/receipt、NODE 响应合同、schema 2.0 教材、精确源码片段和真实
cold-start report 边界。没有修改授权学习项目的源码、QA、LOG、memory 或
最终文档。

## 修改前后对应

| 修改前问题 | v6 机制 |
| --- | --- |
| 混合消息和旧 `继续` 依赖模型记忆 | input event + ordered intents + consumed continue IDs |
| 状态压缩后靠猜测恢复 | 完整 handoff + artifact hashes + `REPAIR_REQUIRED` |
| QA 只检查统一 20 字门槛 | concept/code/shape/metric/review/correction 分类型合同 |
| 一次性问题可能污染 memory | durable trigger classifier；普通问题返回 no candidate |
| memory 没有候选/拒绝/失效状态 | candidate/approved/saved/rejected/stale + hash journal |
| QA/LOG、memory、finalizer receipt 相互独立 | PREPARED/COMMITTED schema 6.0 release receipt |
| finalizer 可单独声称 saved | publication finalizer 只返回 `release-pending` |
| 文档是 Step/UNIT 摘要索引 | schema 2.0 每个完成 Step 的 20 项教材章节 |
| 源码路径存在即可 | 精确相对路径、行段和 fenced excerpt 内容一致性 |
| 静态检查可被写成 cold-start 通过 | fresh-model/no-chat、document-hash-bound JSON report |
| 长上下文导致 NODE 输出降级 | 每 NODE 加载短合同并由 response validator 检查 |
| 宿主不调用工具仍可能口头声称成功 | exact response hash + COMMITTED receipt；无 hook 则禁止 claim |

## 保留的设计

真实调用链路线、单 RUN/NODE、动态 Step/micro-Step、主线/continuation、
支线后恢复、pending intents、fresh continue、retest gate、唯一 Q/M/C/TX、
QA/LOG 事务、not-run 边界、禁止虚假 claim、correction 传播、memory
fail-closed、显式文档同意、草稿隔离、readiness repair、research 副本隔离、
宿主责任边界、strict validator 和证据等级均保留。

## 测试结果

| 要求 | 命令/用例 | 结果 |
| --- | --- | --- |
| Skill 静态结构 | `validate_skill_structure.py` | PASS |
| 所有脚本单元测试 | `python -m unittest discover -s tests -p "test_*.py" -v` | 88 total：87 PASS / 1 SKIP |
| 旧 QA/LOG strict | 授权样本，非 publication | PASS |
| v6 QA 深度 | 授权样本 `--publication` | 正确 FAIL；586 条深度缺口 |
| memory doctor | 授权样本 `.project-study-memory` | PASS |
| 旧文档兼容 validator | 授权样本 schema 1.2 | PASS |
| v6 document publication | 授权样本 `--publication` | 正确 FAIL：非 schema 2.0、cold-start not-run/report 缺失 |
| document cold-start | hash-bound synthetic fresh-model report | PASS；真实样本 not-run |
| mixed intents | question/feedback/continue ordered split | PASS |
| retest gate | T-21 | PASS |
| 旧 `继续` 消费 | T-04/T-22 + event replay | PASS |
| Q/M/C/TX 唯一性 | allocator v6 test | PASS |
| receipt hash 一致性 | changed-after-prepare abort + exact response | PASS |
| memory 自动维护/拒绝 | durable triggers、one-off rejection、redaction | PASS |
| 上下文恢复 | handoff hash match/mismatch | PASS（模拟）；真实 compact not-run |
| NODE 响应合同 | 8 sections/state/recall/side-question | PASS |
| 真实 Codex 宿主 | 本 Codex Desktop 任务实际执行 Skill 维护、文件工具、测试、GitHub 调研 | PASS（维护宿主路径）；新版本 fresh-load golden conversation not-run |
| Codex CLI 独立宿主 | `codex --help` | BLOCKED：WindowsApps executable 拒绝访问 |
| GitHub 官方 API | 16 个参考仓库元数据 | PASS |

静态 validator、模拟 handoff 和当前维护任务不等于新模型教学 golden
conversation。T31 因此继续 SKIP，而不是伪造通过。

## 授权样本文档观察

- 49,102 个字符，1,401 行；
- 10 个 `UNIT`，0 个 schema 2.0 `CHAPTER`；
- Q-049、Q-067、Q-070 未出现；Q-063 出现 3 次，Q-068 出现 1 次；
- legacy validator 通过只表示可读取旧 schema，不表示达到 v6 教材标准。

## not-run / 依赖宿主

- 多模型教学一致性：not-run；
- 新版本 fresh-session Claude/Codex golden conversation：not-run；
- 授权样本的真实 fresh-model cold-start：not-run（样本先被 publication gate 拒绝）；
- 真实上下文 compact hook：not-run；
- 宿主级 pre-response hook：not-run；
- Claude CLI：not-run（未发现可执行命令）；
- torch 训练/推理：not-run，当前改造不需要运行模型；
- 学习项目源码或记录写入：not-run，且按权限明确禁止。

## 仍有风险

1. Skill 文本不能自行安装宿主 pre-response/compact hook；必须由宿主 runner
   实际调用控制脚本。
2. release receipt 提供逻辑原子发布证明，不虚称跨文件系统级原子替换。
3. QA marker contract 可阻止结构性敷衍，但教育正确性仍需源码证据和真实宿主
   抽样评估。
4. 精确源码 excerpt 校验依赖传入正确 repo root；revision 由 release receipt
   绑定，validator 本身不执行 git checkout。
5. 旧 schema 保持兼容读取，因此调用方必须显式使用 `--publication` 才会执行
   v6 硬门禁。

## Skill-improver 更新记录

修改按高优先级（事务、claim、教材）、中优先级（memory、handoff、QA）、
低优先级（README、致谢、模板）实施。修改前工作树干净，Git 基线 commit
提供可恢复备份；未在用户目录额外复制 Skill。所有新增机制均先有失败测试，
再实现并执行全量回归。
