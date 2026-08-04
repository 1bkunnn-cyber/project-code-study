from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
VALIDATOR_PATH = (
    ROOT
    / "skills"
    / "project-study-document"
    / "scripts"
    / "validate_study_document.py"
)
SPEC = importlib.util.spec_from_file_location(
    "study_document_validator_v61",
    VALIDATOR_PATH,
)
document_validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(document_validator)

import cold_start_test
from tests.test_regressions import STAMP, make_bundle


SHARED_PARAGRAPH = (
    "这一段解释批次从调用者进入当前节点，再沿返回值进入下游损失节点；"
    "它同时标出控制流、数据流和状态流，避免只把真实执行压缩成一个箭头。"
)


def compact_step(
    *,
    step: str = "4.1",
    chapter: str = "4.1",
    profile: str = "standard",
    source_path: str = "src/model.py",
    start: int = 10,
    end: int = 12,
    excerpt: str = "line_10 = x\nline_11 = line_10 + 1\nline_12 = line_11",
    extra_core: str = "",
) -> str:
    return f"""### CHAPTER-{chapter} — 一次前向传播

- 覆盖 Step：{step}
- 阅读层级：{profile}
- 预计复习时间：8 分钟
- 检索关键词：forward；batch；Shape；Q-049
- 本 Step 要解决的问题：追踪一个 batch 如何进入模型并交给 loss。
- 真实调用链位置：RUN-train / NODE-forward。
- 相关 RUN / NODE / micro-Step：RUN-train；NODE-forward；{step}.a。
- 源码锚点：{source_path}:{start}-{end}。
- 学习完成标准：能定位源码、解释 I/O 和完成应用题。

#### 30 秒定位

当前 Step 解决“模型调用发生在哪里、返回值由谁消费”。前置知识是 Python
调用与四维张量；上游 dataloader 产生 batch，下游 loss 消费预测。读完应先能说出
入口、当前节点和唯一下一跳，不需要先阅读完整训练循环。

#### 调用链与数据边界

RUN-train 中调用者先取得 `[8,3,640,640]` 的 batch，再进入 NODE-forward，返回结果
交给 NODE-loss。输入是图像张量，输出是预测结构；本摘录不更新 optimizer、EMA 或
epoch 状态。前一节点准备数据，后一节点计算目标函数。

#### 精选源码证据

- 源码摘录：{source_path}:{start}-{end}

```python
{excerpt}
```

第 {start} 行接收当前输入，第 {start + 1} 行执行最小变换，第 {end} 行保留返回边界。
这三行只保留理解当前调用所需的证据；完整函数通过路径和行号回到仓库查阅。

#### 核心机制

`x` 表示当前 batch，局部变量保存中间结果。示例运算不改变 Shape，因此
`[8,3,640,640] → [8,3,640,640]`。若记为 `y=x+1`，参数量为 0；真实模型的参数和
分支 Shape 由对应 specialist deep dive 解释。{SHARED_PARAGRAPH}{extra_core}

#### 设计取舍与故障定位

显式局部变量让返回链可追踪；原地运算更省临时内存，却可能触发 autograd 版本错误。
常见错误是把 batch 维和 channel 维交换，表现为卷积通道不匹配；应先核对 Shape、
调用栈和当前 train/eval 状态。

#### 项目例子与重要 QA

项目例子使用 8 张三通道 640×640 图像。Q-049 问返回值由谁消费：规范答案是调用者
获得 forward 返回值，并按真实 RUN-train 调用链交给 loss；函数名本身不能证明消费方。

#### 自测与参考答案

回忆题：四个 Shape 维度是什么？应用题：全零输入经过示例变换后，一个元素和下一
NODE 是什么？参考答案：依次是 batch、channel、height、width；元素变为 1，Shape
不变，下一节点是 NODE-loss，且当前节点不更新 optimizer 或 EMA。

#### 证据边界与下一跳

已确认：指定源码行与局部 Shape 不变。可推断：返回值按已锁定调用链进入 loss。
待验证：真实训练 batch 数值范围，运行状态为 not-run。前一节点是 batch prepare，
唯一下一跳是 NODE-loss；更完整的训练状态见文档内 `DEEP-DIVE-TRAINING`。
"""


class CompactHandbookV61Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        source = self.root / "src" / "model.py"
        source.parent.mkdir()
        source.write_text(
            "\n".join(f"line_{index} = x" for index in range(1, 101)) + "\n",
            encoding="utf-8",
        )
        self.step = compact_step(
            excerpt="line_10 = x\nline_11 = x\nline_12 = x",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_compact_eight_slot_step_passes_without_textbook_expansion(self) -> None:
        errors = document_validator.validate_compact_step_contract(
            "4.1",
            self.step,
            repo_root=self.root,
        )
        self.assertEqual(errors, [])

    def test_profile_budget_rejects_bloated_step(self) -> None:
        bloated = compact_step(
            excerpt="line_10 = x\nline_11 = x\nline_12 = x",
            extra_core="扩写内容" * 700,
        )
        errors = document_validator.validate_compact_step_contract(
            "4.1",
            bloated,
            repo_root=self.root,
        )
        self.assertTrue(any("prose budget" in error for error in errors))

    def test_source_budget_rejects_copying_most_of_a_file(self) -> None:
        source = self.root / "src" / "short.py"
        lines = [f"value_{index} = {index}" for index in range(1, 31)]
        source.write_text("\n".join(lines) + "\n", encoding="utf-8")
        copied = compact_step(
            source_path="src/short.py",
            start=1,
            end=20,
            excerpt="\n".join(lines[:20]),
        )
        errors = document_validator.validate_compact_step_contract(
            "4.1",
            copied,
            repo_root=self.root,
        )
        self.assertTrue(any("source coverage" in error for error in errors))

    def test_training_metric_and_innovation_steps_require_specialist_profile(self) -> None:
        for step in ("4.7", "6", "10.2"):
            errors = document_validator.validate_specialist_reading_profile(
                step,
                self.step,
            )
            self.assertTrue(any("specialist" in error for error in errors))
        self.assertEqual(
            document_validator.validate_specialist_reading_profile(
                "3",
                self.step,
            ),
            [],
        )

    def test_repeated_long_paragraphs_across_steps_are_rejected(self) -> None:
        other = compact_step(
            step="4.2",
            chapter="4.2",
            excerpt="line_10 = x\nline_11 = x\nline_12 = x",
        )
        errors = document_validator.validate_chapter_duplication(
            [
                ("CHAPTER-4.1", "前向", self.step),
                ("CHAPTER-4.2", "损失", other),
            ]
        )
        self.assertTrue(any("repeated handbook paragraph" in error for error in errors))

    def test_lookup_index_must_locate_step_keyword_source_and_question(self) -> None:
        document = """## 0. 如何查阅这份手册
先按 Step 或关键词查找。
## 快速检索索引
| Step | 关键词 | 源码 / 符号 | 重要 Q | 手册条目 |
| --- | --- | --- | --- | --- |
| 4.1 | forward；Shape | src/model.py；forward | Q-049 | [CHAPTER-4.1](#chapter-4.1) |
<a id="chapter-4.1"></a>
"""
        self.assertEqual(
            document_validator.validate_lookup_index(
                document,
                completed_steps={"4.1"},
                required_qids={"Q-049"},
            ),
            [],
        )
        errors = document_validator.validate_lookup_index(
            document.replace("Q-049", "无"),
            completed_steps={"4.1"},
            required_qids={"Q-049"},
        )
        self.assertTrue(any("Q-049" in error for error in errors))
        errors = document_validator.validate_lookup_index(
            document.replace("#chapter-4.1", "#chapter-missing"),
            completed_steps={"4.1"},
            required_qids={"Q-049"},
        )
        self.assertTrue(any("manual-entry anchor" in error for error in errors))

    def test_document_local_deep_dive_link_must_resolve(self) -> None:
        document = """## 6. 逐 Step 手册
本 Step 的核心解释已经在本条目内完成；进一步推导见
[训练状态深讲](#deep-dive-training)。
## 7. 数据、Shape 与状态流
<a id="deep-dive-training"></a>
### DEEP-DIVE-TRAINING — 训练状态
这里集中解释跨 Step 复用的训练状态。
"""
        self.assertEqual(
            document_validator.validate_deep_dive_links(document),
            [],
        )
        errors = document_validator.validate_deep_dive_links(
            document.replace('<a id="deep-dive-training"></a>', "")
        )
        self.assertTrue(any("deep-dive-training" in error for error in errors))

    def test_schema_21_cold_start_requires_retrieval_evidence(self) -> None:
        document = self.root / "DOCUMENT.md"
        document.write_text(self.step, encoding="utf-8")
        report = {
            "schema_version": "1.1",
            "mode": "fresh-model-no-chat",
            "fresh_session": True,
            "input_scope": "document-only",
            "document_hash": hashlib.sha256(document.read_bytes()).hexdigest(),
            "model": "codex-host-test",
            "steps": {
                "4.1": {
                    "objective": "trace a batch through forward",
                    "runtime_position": "RUN-train/NODE-forward",
                    "call_chain": "dataloader -> forward -> loss",
                    "source_explanation": "src/model.py lines 10-12",
                    "io_shape_state": "[8,3,640,640] stays unchanged",
                    "important_qa": "Q-049 identifies the consumer",
                    "exercise_answer": "next NODE is loss",
                    "evidence_boundary": "runtime remains not-run",
                    "result": "pass",
                }
            },
            "overall_status": "pass",
        }
        report_path = self.root / "cold-start.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        errors = cold_start_test.evaluate_report(
            report_path,
            document,
            required_steps={"4.1"},
            handbook_schema="2.1",
        )
        self.assertTrue(any("lookup_path" in error for error in errors))
        report["steps"]["4.1"].update(
            {
                "lookup_path": "快速检索索引 -> CHAPTER-4.1",
                "retrieval_result": "pass",
                "explanation_result": "pass",
                "application_result": "pass",
            }
        )
        report_path.write_text(json.dumps(report), encoding="utf-8")
        self.assertEqual(
            cold_start_test.evaluate_report(
                report_path,
                document,
                required_steps={"4.1"},
                handbook_schema="2.1",
            ),
            [],
        )

    def test_cold_start_cli_accepts_schema_21_flag(self) -> None:
        document = self.root / "CLI-DOCUMENT.md"
        document.write_text(self.step, encoding="utf-8")
        report = {
            "schema_version": "1.1",
            "mode": "fresh-model-no-chat",
            "fresh_session": True,
            "input_scope": "document-only",
            "document_hash": hashlib.sha256(document.read_bytes()).hexdigest(),
            "model": "codex-host-cli",
            "steps": {
                "4.1": {
                    "objective": "trace a batch through one forward call",
                    "runtime_position": "RUN-train and NODE-forward",
                    "call_chain": "dataloader -> forward -> loss",
                    "source_explanation": "src/model.py lines 10-12 show the selected boundary",
                    "io_shape_state": "[8,3,640,640] remains unchanged in the local example",
                    "important_qa": "Q-049 identifies the caller consuming the return value",
                    "exercise_answer": "the Shape is unchanged and next NODE is loss",
                    "evidence_boundary": "source is confirmed while runtime values remain not-run",
                    "lookup_path": "快速检索索引 -> CHAPTER-4.1",
                    "retrieval_result": "pass",
                    "explanation_result": "pass",
                    "application_result": "pass",
                    "result": "pass",
                }
            },
            "overall_status": "pass",
        }
        report_path = self.root / "cold-start-cli.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "cold_start_test.py"),
                "--report",
                str(report_path),
                "--document",
                str(document),
                "--step",
                "4.1",
                "--handbook-schema",
                "2.1",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_schema_21_publication_uses_compact_manual_and_lookup_index(self) -> None:
        ledger, qa = make_bundle(self.root)
        qa_text = qa.read_text(encoding="utf-8")
        qa_depth = """源码位置：src/model.py:10-12。
真实代码片段：
```python
line_10 = x
line_11 = x
line_12 = x
```
逐行解释：三行标出输入、中间值和返回边界。
输入：x 张量。输出：新张量。调用者：entry。返回值：交给下游。
最小例子：输入 0 时输出 1。"""
        qa.write_text(
            qa_text.replace(
                "- 完整参考答案：The entry validates the input first, calls the main operation second, and returns the verified output last.",
                "- 完整参考答案：The entry validates input and returns output。\n"
                + qa_depth,
            ),
            encoding="utf-8",
        )
        step = compact_step(
            step="0",
            chapter="0",
            excerpt="line_10 = x\nline_11 = x\nline_12 = x",
        ).replace("Q-049", "Q-001")
        document = self.root / "PROJECT_STUDY_DOCUMENT.md"
        body = f"""---
document_type: project-study-document
schema_version: "2.1"
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
handbook_mode: "layered-step-manual"
default_reading_profile: "standard"
---
# Demo 项目学习手册
## 0. 如何查阅这份手册
先用快速索引定位 Step、符号、源码或 Q-ID，再读对应条目的八个槽位。
## 快速检索索引
| Step | 关键词 | 源码 / 符号 | 重要 Q | 手册条目 |
| --- | --- | --- | --- | --- |
| 0 | forward；Shape | src/model.py；forward | Q-001 | [CHAPTER-0](#chapter-0) |
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
## 6. 逐 Step 手册
<a id="chapter-0"></a>
{step}
## 7. 数据、Shape 与状态流
<a id="deep-dive-training"></a>
### DEEP-DIVE-TRAINING — 训练状态
这里只保存跨 Step 复用的深入解释；Step 核心闭环不依赖聊天。
## 8. 目标函数、训练、推理与评估
此最小项目没有训练目标；已说明适用边界。
## 9. 论文—代码映射与设计解释
没有论文依赖。
## 10. 用户重要提问
| Q-ID | Step | 主题 | 一句话结论 | 正文锚点 |
| --- | --- | --- | --- | --- |
| Q-001 | 0 | 返回值消费方 | 调用者接收并交给下游 | [CHAPTER-0](#chapter-0) |
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
源码为 src/model.py:10-12。
"""
        document.write_text(body, encoding="utf-8")
        report = {
            "schema_version": "1.1",
            "mode": "fresh-model-no-chat",
            "fresh_session": True,
            "input_scope": "document-only",
            "document_hash": hashlib.sha256(document.read_bytes()).hexdigest(),
            "model": "codex-host-gold",
            "steps": {
                "0": {
                    "objective": "trace input through the project entry",
                    "runtime_position": "RUN-main and NODE-001",
                    "call_chain": "entry -> forward -> downstream output",
                    "source_explanation": "src/model.py lines 10-12 define the local boundary",
                    "io_shape_state": "[8,3,640,640] remains unchanged with no optimizer state",
                    "important_qa": "Q-001 explains which caller consumes the return value",
                    "exercise_answer": "the Shape is unchanged and the caller receives the result",
                    "evidence_boundary": "source is confirmed; runtime remains not-run",
                    "lookup_path": "快速检索索引 -> CHAPTER-0",
                    "retrieval_result": "pass",
                    "explanation_result": "pass",
                    "application_result": "pass",
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
                publication=True,
                cold_start_report=report_path,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
