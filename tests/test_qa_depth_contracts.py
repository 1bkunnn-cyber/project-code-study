from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_learning_ledger
from tests.test_regressions import make_bundle


COMPLETE = {
    "concept": """
定义：梯度累积是在多个 micro-batch 上累加梯度后再更新。
项目语境：本项目在 _do_train 中使用 accumulate 控制 optimizer_step。
类比：像把多笔小额账单合并结算。
反例：每个 batch 都 zero_grad 就不是跨 batch 累积。
相邻概念区别：warmup 改学习率，accumulate 改更新频率。
自测：accumulate=4 时第几批更新？参考答案：第 4 个合格批次。
""",
    "code": """
源码位置：ultralytics/engine/trainer.py:382-398，符号 _do_train。
真实代码片段：
```python
self.loss, self.loss_items = self.model(batch)
self.scaler.scale(self.loss).backward()
```
逐行解释：第一行把字典 batch 送入模型损失入口；第二行用 scaler 反向传播。
输入：batch 字典，img 为 [B,3,H,W]。输出：标量 loss 与三项 loss_items。
调用者：BaseTrainer._do_train。返回值：model(batch) 返回 loss 和 detached loss items。
最小例子：B=2 时先 forward，再 backward，达到 accumulate 后 optimizer_step。
""",
    "shape": """
输入 Shape：[8,3,640,640]。
每层公式：卷积输出 Hout=floor((H+2p-k)/s)+1，因此 stride=2 得 320。
通道来源：width=0.25 使 64 通道缩放为 16，并经 make_divisible 对齐。
分支合并：Concat 把 [8,256,40,40] 与 [8,128,40,40] 沿 C 合并为 [8,384,40,40]。
输出验证：Detect 接收 P3/P4/P5 三个尺度，空间尺寸为 80/40/20。
""",
    "metric": """
TP/FP/FN：匹配且类别正确为 TP，未匹配预测为 FP，未匹配真值为 FN。
公式：Precision=TP/(TP+FP)，Recall=TP/(TP+FN)，IoU=交集/并集。
来源：DetectionValidator 的匹配结果。
阈值：confidence 与 IoU 阈值共同影响计数。
项目字段：results.csv 的 metrics/precision、metrics/recall、metrics/mAP50。
评判标准：结合 P、R、mAP50-95 与曲线趋势判断。
误区：mAP50 高不代表严格定位精度也高。
""",
    "review": """
覆盖矩阵：
|要求|证据|状态|
|---|---|---|
|训练循环|SRC-008|covered|
遗漏内容：真实 AMP 宿主运行未执行。
证据等级：训练源码为 E1，实际运行指标为 E3。
下一步动作：使用相同 revision 执行最小训练并保存 receipt。
""",
    "correction": """
原结论：box_iou 输出固定为 [N_pred,N_gt]。
纠正内容：输出是 [N_box1,N_box2]，方向由调用参数顺序决定。
影响范围：QA、知识卡、Step 6 章节和最终摘要。
传播检查：四个派生产物均不得保留旧固定方向表述。
回归测试：交换 box1/box2 并验证输出 Shape 分别为 [N,M] 与 [M,N]。
""",
}


class QuestionDepthContractTests(unittest.TestCase):
    def test_shallow_answers_fail_with_type_specific_missing_fields(self) -> None:
        for question_type in COMPLETE:
            with self.subTest(question_type=question_type):
                errors = validate_learning_ledger.validate_question_depth(
                    question_type,
                    "这是一个超过二十个字符、但没有完成教学合同的形式完整答案。",
                )
                self.assertTrue(errors)
                self.assertTrue(all(question_type in error for error in errors))

    def test_complete_type_specific_answers_pass(self) -> None:
        for question_type, body in COMPLETE.items():
            with self.subTest(question_type=question_type):
                self.assertEqual(
                    validate_learning_ledger.validate_question_depth(question_type, body),
                    [],
                )

    def test_runtime_and_visual_legacy_types_use_composite_contracts(self) -> None:
        self.assertEqual(
            validate_learning_ledger.validate_question_depth("runtime", COMPLETE["code"]),
            [],
        )
        self.assertEqual(
            validate_learning_ledger.validate_question_depth("visual", COMPLETE["metric"]),
            [],
        )

    def test_publication_validation_rejects_structurally_valid_shallow_qa(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            _, qa = make_bundle(Path(directory))
            errors, _, _ = validate_learning_ledger.validate_text(
                qa.read_text(encoding="utf-8"),
                strict=True,
                publication=True,
            )
        self.assertTrue(any("Q-001 code answer missing" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
