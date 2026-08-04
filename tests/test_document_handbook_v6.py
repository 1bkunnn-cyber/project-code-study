from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

VALIDATOR_PATH = (
    ROOT
    / "skills"
    / "project-study-document"
    / "scripts"
    / "validate_study_document.py"
)
SPEC = importlib.util.spec_from_file_location("study_document_validator_v6", VALIDATOR_PATH)
document_validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(document_validator)

import cold_start_test
from tests.test_regressions import STAMP, make_bundle


def complete_chapter(source_path: str = "src/model.py", snippet: str = "def forward(x):\n    return x + 1") -> str:
    return f"""### CHAPTER-4.1 — 从输入到一次前向传播

- 覆盖 Step：4.1
- 本 Step 要解决的问题：追踪一个 batch 如何进入模型并产生预测。
- 前置知识：Python 调用、张量维度、卷积基础。
- 真实调用链位置：RUN-train / NODE-forward / micro-Step 4.1.a。
- 上游输入与下游输出：上游 dataloader 提供 batch，下游 loss 接收预测。
- 相关 RUN / NODE / micro-Step：RUN-train；NODE-forward；4.1.a。
- 源码锚点：{source_path}:1-2。
- 本章学习完成标准：能够脱离聊天复述调用链、核对源码并完成练习。

#### 本章教材讲解

这一章围绕真实运行链展开：训练循环先取得 batch，再调用模型。读者需要把控制流、数据流和状态流同时连起来，不能把“前向传播”缩写成一个箭头。这里给出调用者、被调用者、返回对象及其被 loss 消费的方式，并用项目中的最小输入说明每一步发生了什么。阅读时应能从入口沿调用关系进入实现，再沿返回值回到调用者，同时指出哪些结论来自源码、哪些仍需要运行验证。

#### 调用链与前后 NODE

上游 NODE 准备 batch，当前 NODE 执行 forward，下游 NODE 计算 loss。先识别调用者，再进入实现，最后沿返回值回到训练循环；continuation NODE 保持为 loss。

#### 关键源码片段

- 源码摘录：{source_path}:1-2

```python
{snippet}
```

#### 逐段或逐行解释

第 1 行定义 forward 并接收 x，说明调用边界；第 2 行返回变换后的张量，返回值由下游 loss 使用。解释必须对应真实行号，不能只把代码改写成自然语言。调用者负责准备输入，被调用者只实现当前变换。

#### 变量、参数与状态

`x` 是当前 batch 张量；返回值是新张量。函数没有修改优化器状态。模型参数由模块持有，训练或推理模式会影响部分层，但这个最小函数本身不保存额外状态。

#### 输入、输出、Shape 与状态变化

输入示例为 `[8, 3, 640, 640]`，运算不改变维度，因此输出仍为 `[8, 3, 640, 640]`。batch 维、通道、高和宽来源清楚；此处没有分支合并，状态变化为生成一个新张量。

#### 数学公式与参数计算

逐元素公式是 `y = x + 1`，所以参数量为 0，输出每个位置等于输入对应位置加一。这里不涉及卷积核参数；明确说明“不适用”的原因比省略公式更可靠。

#### 为什么这样设计、替代实现与取舍

直接返回新张量让数据依赖清楚。替代方案可以原地修改，但会增加 autograd 和共享引用风险；另一种是封装为模块，便于组合却增加结构。当前实现用最小复杂度换取可读性。

#### 常见错误和错误表现

常见错误是把通道维与 batch 维交换，表现为后续卷积报通道不匹配；另一个错误是原地修改需要梯度的张量，表现为 backward 版本计数异常。排查时先打印 Shape 和调用栈。

#### 当前项目具体例子

当 batch 为 8 张三通道 640×640 图像时，当前 NODE 保持 Shape 并把数值整体平移。这个例子可以用一个全零小张量验证：输出应全为 1，再交给下游节点。

#### 重要 QA 问题和完整答案

Q-049 问“返回值由谁消费”。完整答案是训练循环中的 loss NODE 接收模型输出；调用者决定何时调用，forward 决定如何变换，返回值的语义要沿真实调用链确认，不能只看函数名猜测。

#### 回忆题与练习题

回忆题：四个 Shape 维度分别是什么？练习题：给定全零 `[8,3,640,640]` 输入，写出输出 Shape、一个元素的值以及下一个 NODE。

#### 参考答案

四维依次是 batch、channel、height、width。输出 Shape 不变，一个元素从 0 变为 1；下一个 NODE 是 loss。答案还应指出该函数不更新 optimizer 或 EMA 状态。

#### 已确认、可推断、待验证的证据边界

已确认：源码两行和 Shape 保持。可推断：下游按调用链消费返回值。待验证：真实训练数据的数值范围，需要运行时日志；未运行内容明确标为 not-run。

#### 与前后 NODE 的连接

前一个 NODE 产生 batch，当前 NODE 产生预测张量，后一个 NODE 计算 loss。完成后回到 continuation NODE，而不是跳到任意新主题。
"""


class DocumentHandbookV6Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        source = self.root / "src" / "model.py"
        source.parent.mkdir()
        source.write_text("def forward(x):\n    return x + 1\n", encoding="utf-8")
        self.chapter = complete_chapter()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_shallow_step_index_is_not_a_handbook_chapter(self) -> None:
        errors = document_validator.validate_chapter_contract(
            "4.1",
            "### CHAPTER-4.1 — 前向\n\n结论：前向后计算 loss。",
            repo_root=self.root,
        )
        self.assertGreaterEqual(len(errors), 10)

    def test_complete_chapter_with_exact_source_excerpt_passes(self) -> None:
        self.assertEqual(
            document_validator.validate_chapter_contract(
                "4.1",
                self.chapter,
                repo_root=self.root,
            ),
            [],
        )

    def test_tampered_source_excerpt_fails_exact_line_check(self) -> None:
        chapter = self.chapter.replace("return x + 1", "return x + 2")
        errors = document_validator.validate_chapter_contract(
            "4.1",
            chapter,
            repo_root=self.root,
        )
        self.assertTrue(any("does not match source lines" in error for error in errors))

    def test_special_step_contracts_reject_missing_training_metric_and_innovation_depth(self) -> None:
        text = "\n".join(
            [
                "Step 4.7：forward → loss → backward → optimizer。",
                "Step 6：mAP 用来评估。",
                "Step 10：加入 SE 作为创新。",
            ]
        )
        errors = document_validator.validate_special_step_contracts(
            text,
            {"4.7", "6", "10"},
        )
        self.assertTrue(any("_do_train()" in error for error in errors))
        self.assertTrue(any("TP" in error and "results.csv" in error for error in errors))
        self.assertTrue(any("baseline" in error and "消融" in error for error in errors))

    def test_cold_start_report_is_document_hash_bound_and_step_complete(self) -> None:
        document = self.root / "DOCUMENT.md"
        document.write_text(self.chapter, encoding="utf-8")
        digest = hashlib.sha256(document.read_bytes()).hexdigest()
        report = {
            "schema_version": "1.0",
            "mode": "fresh-model-no-chat",
            "fresh_session": True,
            "input_scope": "document-only",
            "document_hash": digest,
            "model": "codex-host-test",
            "steps": {
                "4.1": {
                    "objective": "trace one batch through forward",
                    "runtime_position": "RUN-train/NODE-forward",
                    "call_chain": "dataloader -> forward -> loss",
                    "source_explanation": "model.py lines 1-2 define and return",
                    "io_shape_state": "[8,3,640,640] -> [8,3,640,640], state unchanged",
                    "important_qa": "Q-049 caller and return consumer",
                    "exercise_answer": "shape unchanged; next NODE is loss",
                    "evidence_boundary": "runtime values remain not-run",
                    "result": "pass",
                }
            },
            "overall_status": "pass",
        }
        report_path = self.root / "cold-start.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        self.assertEqual(
            cold_start_test.evaluate_report(
                report_path,
                document,
                required_steps={"4.1"},
            ),
            [],
        )
        report["document_hash"] = "0" * 64
        report_path.write_text(json.dumps(report), encoding="utf-8")
        self.assertTrue(
            cold_start_test.evaluate_report(
                report_path,
                document,
                required_steps={"4.1"},
            )
        )

    def test_complete_schema_2_document_remains_readable_for_migration(self) -> None:
        ledger, qa = make_bundle(self.root)
        qa_text = qa.read_text(encoding="utf-8")
        depth = """源码位置：src/model.py:1-2。
真实代码片段：
```python
def forward(x):
    return x + 1
```
逐行解释：第一行定义调用边界，第二行返回变换结果。
输入：x 张量。输出：新张量。调用者：entry。返回值：交给下游。
最小例子：输入 0 时输出 1。"""
        qa.write_text(
            qa_text.replace(
                "- 完整参考答案：The entry validates the input first, calls the main operation second, and returns the verified output last.",
                "- 完整参考答案：The entry validates input and returns output。\n" + depth,
            ),
            encoding="utf-8",
        )
        chapter = complete_chapter().replace("CHAPTER-4.1", "CHAPTER-0")
        chapter = chapter.replace("覆盖 Step：4.1", "覆盖 Step：0")
        chapter = chapter.replace("Q-049", "Q-001")
        document = self.root / "PROJECT_STUDY_DOCUMENT.md"
        body = f"""---
document_type: project-study-document
schema_version: "2.0"
status: "complete"
project_name: "Demo"
project_path: "{self.root.as_posix()}"
repository_revision: "abc1234"
source_transaction_id: "TX-0002"
readiness_transaction_id: "TX-0002"
readiness_status: "pass"
learning_goal: "understand"
audience: "learner"
language: "zh-CN"
generated_at: "{STAMP}"
source_ledger: "PROJECT_STUDY_LOG.md"
source_qa: "PROJECT_STUDY_QA.md"
validation_status: "validated"
cold_start_status: "pass"
release_transaction_id: "DOC-TX-0001"
required_question_ids: "Q-001"
---
# Demo 项目学习手册
## 1. 文档身份与证据范围
已确认源码与账本范围。
## 2. 学习成果摘要
已确认入口调用关系。
## 3. 项目、任务与问题定义
项目把输入变换为输出。
## 4. 动态学习路线、知识覆盖与掌握情况
Step 0 已完成并映射到 CHAPTER-0。
## 5. 运行场景与真实调用链
RUN-main 从 entry 进入 NODE-001。
## 6. 逐 Step 教材章节
<a id="chapter-0"></a>
{chapter}
## 7. 数据、Shape 与状态流
输入、输出和状态边界见教材章节。
## 8. 目标函数、训练、推理与评估
此最小项目没有训练目标；已说明适用边界。
## 9. 论文—代码映射与设计解释
没有论文依赖。
## 10. 用户重要提问
### Q-001 — 返回值由谁消费
完整答案：调用者接收返回值并交给下游节点。
## 11. 误区、规范修正与认知变化
没有未传播修正。
## 12. 相关方法、相似思想与模块组合
可替换为显式模块封装。
## 13. 实验、失败、局限与未解决事项
真实部署未运行。
## 14. 复现、验证与修改指南
用最小输入验证返回值。
## 15. 后续行动
复核真实运行日志。
## 16. 证据与产物索引
源码为 src/model.py:1-2。
"""
        document.write_text(body, encoding="utf-8")
        digest = hashlib.sha256(document.read_bytes()).hexdigest()
        report = {
            "schema_version": "1.0",
            "mode": "fresh-model-no-chat",
            "fresh_session": True,
            "input_scope": "document-only",
            "document_hash": digest,
            "model": "codex-host-gold",
            "steps": {
                "0": {
                    "objective": "trace input through the project entry",
                    "runtime_position": "RUN-main and NODE-001",
                    "call_chain": "entry -> forward -> downstream output",
                    "source_explanation": "src/model.py lines 1-2 define forward and return x plus one",
                    "io_shape_state": "[8,3,640,640] remains [8,3,640,640] with no optimizer state",
                    "important_qa": "Q-001 explains which caller consumes the return value",
                    "exercise_answer": "the Shape is unchanged and the caller receives the result",
                    "evidence_boundary": "source is confirmed; deployment runtime remains not-run",
                    "result": "pass",
                }
            },
            "overall_status": "pass",
        }
        report_path = self.root / "cold-start-gold.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        self.assertEqual(
            document_validator.validate(
                document,
                allow_template=False,
                ledger_path=ledger,
                qa_path=qa,
                preflight=False,
                repo_root=self.root,
                publication=False,
                cold_start_report=report_path,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
