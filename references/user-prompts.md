# Project Code Study: Short Prompt Pack

Use the smallest prompt that matches the situation. The skill itself contains the full protocol; users should not need to paste a long role-and-checklist prompt every time.

## 1. Start

```text
请使用 $project-code-study 带我学习这个项目。

项目：<path / URL>
目标：<读懂 / 复现 / 修改 / 研究扩展>
基础：<简述>
每次时间：<时长>
论文或运行材料：<有则填写>

请先确认是否可以维护 PROJECT_STUDY_LOG.md 和 PROJECT_STUDY_QA.md，然后扫描源码、识别运行场景，生成项目专属学习路线。先只完成 Step 0。
```

## 2. Continue the main line

```text
请使用 $project-code-study 继续主线。

读取当前主线锚点和相关记录，从“精确继续位置”恢复。一次只学习一个运行时调用节点、类或函数；结束后更新记录并给出写入回执。
```

## 3. Ask a side question

```text
这是当前节点的支线问题：<question>

请完整回答并记录新的 Q-ID。回答后告诉我它与当前节点的关系，以及主线应从哪里继续。
```

## 4. Answer an active-recall question

```text
我的回答：<answer>

请判断正确程度，但无论对错都给出完整参考答案、证据和需要修正的地方；更新掌握度和问答记录后，再决定是否进入下一节点。
```

## 5. Resume after a break

```text
请使用 $project-code-study 恢复学习。

只读取热状态、当前调用节点、最新会话、阻塞项、到期复习和相关 Q&A。先给出 60 秒恢复摘要，再从精确继续位置继续或安排一次必要复习。
```

## 6. Rebuild the route

```text
当前学习顺序或粒度不合适。请重新扫描相关源码，按训练/推理等运行场景重建调用图和概念依赖，把后续路线拆成一次一个节点的微 Step，并写入学习日志。
```

## 7. Review

```text
请复习范围：<Step / Node / Q-ID>。

一次只问一个调用、Shape、预测或修改问题。我回答后必须给完整参考答案，再更新复习状态。
```

## 8. Audit blind spots

```text
请执行全局覆盖审计：重新检查运行场景、核心调用节点、概念依赖、用户问题、规范修正、论文代码映射和运行证据。发现遗漏时插入回补微 Step，不要直接把旧 Step 标为完成。
```

## 9. Final notes

```text
请生成最终 Markdown 学习笔记。核对 PROJECT_STUDY_LOG.md、PROJECT_STUDY_QA.md 和项目证据，使用最新规范表述，排除 stale 结论，并明确区分“讲过”和“已通过行为证明掌握”。
```

## 10. Host without skill support

```text
请按以下原则带我学习项目：先扫描源码并建立运行场景调用图；按真实调用顺序一次讲一个类/函数；维护主线锚点；所有实质问题和追问都持久记录；我回答测试题后必须得到完整参考答案；详细问答与紧凑学习日志分开；完成状态必须由行为证据支持。
```
