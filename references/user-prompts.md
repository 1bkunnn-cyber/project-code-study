# project-code-study v6.2 使用方式

用户只需要表达学习目标、回答回忆题、自然提问或说“继续”。Skill 负责内部定位、意图拆分、Q-ID、QA/LOG/memory、事务、receipt、恢复和推进门禁；用户默认不需要操作这些机制。

## 唯一启动提示

```text
我想开始学习这个项目。目标是 <读懂 / 复现 / 修改 / 研究扩展>，我目前了解 <一句话基础>，希望重点学习 <可留空>。请按真实调用链带我逐步学习。
```

只提供“我想开始学习这个项目”也可以。缺少但确实影响路线的信息，由 Skill 在 START 阶段一次询问；其余从项目证据中发现。

## 固定学习模式

每一轮都复用同一个闭环：

```text
定位 → 学习 → 检验 → 沉淀 → 等待
```

- `START`：确认项目、目标、权限、证据边界和代表性 RUN。
- `LEARN`：只讲当前一个 NODE，给出真实调用链与必要源码。
- `ASK`：用户直接自然提问；先保留主线，再处理一个或多个问题。
- `ASSESS`：用户回答回忆题后先评价，再给完整解释；部分正确或错误时安排 retest。
- `RECOVER`：优先从 handoff、LOG、QA、memory 和 receipt 恢复，不重新猜状态。
- `CLOSE`：沉淀本轮知识卡、证据边界和唯一下一行动，然后等待。
- `REPAIR`：状态、hash 或事务不一致时停止教学，只修复记录和证据。

用户不必指定模式。Skill 根据当前状态和本次输入自动路由。

## 日常输入：直接自然提问

可以像普通对话一样输入：

```text
继续。
```

```text
为什么这里要做 Concat？
```

```text
我认为这个通道数应该是 384，不是 256，请重新核对。
```

```text
我对回忆题的回答是：model(batch) 先进入 forward，然后训练路径再计算 loss。
```

```text
先暂停，下一次从当前回忆题继续。
```

深讲、Shape、指标、论文—代码映射和运行验证也直接说需求，不必复制内部控制提示词。

## 一次提出任意数量的问题

问题不要求编号，也没有协议上的数量上限。例如：

```text
Conv 为什么改变通道数？C2f 的分支从哪里来？最后输出 Shape 是多少？
```

Skill 必须先完成批次 intake：识别全部独立问题、保持原顺序和 source span、为每个问题分配唯一 Q-ID，并把每个问题在 QA/LOG 中全部登记为 `pending`。只有全部登记和 intake receipt 校验成功后，才逐题回答。

回答采用独立事务：每个问题更新自己的原 Q-ID、完整答案、证据、状态和 TX receipt；不能把三个回答合成一个 Q，也不能回答第一题后遗漏后续题。聊天过长时可以每轮展示最多三题，但队列中每个问题都必须保留。某题失败时，已成功题保持 `answered`，失败题进入 repair，后续题保持 `pending`。

追问获得新的 Q-ID，并通过 Parent Q 指向被追问的问题。普通一次性问题写 QA，但不会自动污染长期 memory。

若同一消息包含问题与“继续”，问题优先，“继续”标记为 `expired-by-question`；问题闭环后必须等待用户新发一次“继续”。

## 回忆题与支线问题

用户回答回忆题时，Skill 先复述理解并逐项评价正确、缺失、错误或证据不足，再给完整参考答案。短回答不等于错误，不能替用户虚构内容。

如果用户在回忆题中插入问题，原回忆题仍保留。支线问题登记、回答和保存后，返回原 `AWAITING_RECALL`，不能把支线回答当成回忆完成。retest 未通过时禁止推进。

## 每轮可见的最小结果

响应按模式变化，不机械套用同一大模板，但始终显示：

- 当前 Step / micro-Step / RUN / NODE / 主线锚点；
- 本轮解决的问题或恢复/修复结果；
- 与内容类型相符的证据：代码、Shape、配置状态或指标公式；
- QA 与事务状态；
- 等待状态、阻塞原因或唯一下一行动。

只有张量路径必须给出具体 Shape；配置或状态问题不能为满足格式编造 Shape。

## 成功声明与 fail-closed

`saved`、`validated`、`complete` 和正式文档生成都必须来自宿主实际执行的控制工具、严格 validator 与匹配 hash 的机器 receipt。宿主未执行 transaction entrypoint 或 pre-response hook 时，只能报告 `unverified`、`unsaved-partial` 或 `not-run`，不能用自然语言补写成功。

正式 `PROJECT_STUDY_DOCUMENT.md` 仍需用户明确同意。它是可快速翻阅、能按 Step 重新学习的紧凑手册，不复制完整聊天或大段源码；正式发布还需 readiness 与 cold-start 通过。

## 高级诊断（默认不需要）

只有出现异常时才使用自然诊断请求，例如：

```text
暂停教学，检查当前 Step/RUN/NODE、问题队列、retest、LOG/QA/memory hash、最后成功 TX 和唯一下一行动；没有机器 receipt 的状态一律按未保存处理。
```

```text
当前可能发生上下文压缩，请只从结构化 handoff 恢复；若 handoff 与现有 artifact hash 不一致，进入 REPAIR，不开始新 NODE。
```

```text
我同意生成正式 PROJECT_STUDY_DOCUMENT.md。请先运行 fresh readiness、validator 和 cold-start；失败时只修复并重新审计。
```

这些诊断文字不是日常提示词。状态机、pending intents、Q-ID、receipt 和 finalizer 仍由 Skill 与宿主负责。
