from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_teaching_response


def valid_response() -> str:
    return """## 本 NODE 要解决的问题
解释 batch 如何进入 forward。

- 当前 Step：4.1
- 当前 micro-Step：4.1.a
- 当前 RUN：RUN-train
- 当前 NODE：NODE-forward
- 主线锚点：ANCHOR-train-forward

## 调用链
dataloader -> trainer -> model(batch) -> loss

## 真实代码
```python
preds = model(batch)
```

## 输入 / 输出 / Shape / 状态
输入 `[8,3,640,640]`，输出预测，optimizer 状态未更新。

## 为什么这样写
分离 forward 和 loss，便于复用推理路径。

## 常见错误
把 forward 当作完整训练会漏掉 backward。

## 自测题
model(batch) 之后哪个 NODE 消费返回值？

## QA / receipt 状态
Q-063 candidate；TX 尚未 commit，因此未声称 saved。
"""


class TeachingResponseContractV6Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = {
            "current_step": "4.1",
            "current_micro_step": "4.1.a",
            "current_run": "RUN-train",
            "current_node": "NODE-forward",
            "mainline_anchor": "ANCHOR-train-forward",
            "pending_user_intents": [],
            "retest_due_questions": [],
            "state_consistent": True,
            "host_capabilities": {
                "transaction_entrypoint": True,
                "pre_response_hook": True,
                "cold_start_host": False,
                "real_compaction_hook": False,
            },
            "response_profile": "node-teaching",
            "content_kind": "tensor",
        }

    def test_complete_node_response_matches_loaded_state(self) -> None:
        self.assertEqual(
            validate_teaching_response.validate_response(
                valid_response(),
                self.state,
            ),
            [],
        )

    def test_summary_style_response_fails_required_teaching_sections(self) -> None:
        errors = validate_teaching_response.validate_response(
            "前向后计算 loss，然后 backward。",
            self.state,
        )
        self.assertGreaterEqual(len(errors), 8)

    def test_state_drift_and_unresolved_intents_enter_repair(self) -> None:
        state = dict(self.state)
        state["state_consistent"] = False
        state["pending_user_intents"] = ["Q-070"]
        errors = validate_teaching_response.validate_response(valid_response(), state)
        self.assertTrue(any("REPAIR_REQUIRED" in error for error in errors))

    def test_recall_answer_requires_evaluation_then_full_explanation(self) -> None:
        state = dict(self.state)
        state["response_profile"] = "recall-assessment"
        errors = validate_teaching_response.validate_response(valid_response(), state)
        self.assertTrue(any("回答评价" in error for error in errors))
        enriched = valid_response() + "\n## 回答评价\n方向正确但缺少 loss。\n\n## 完整解释\n返回值由 loss NODE 消费。\n"
        self.assertEqual(
            validate_teaching_response.validate_response(enriched, state),
            [],
        )

    def test_side_question_must_preserve_original_recall_question(self) -> None:
        state = dict(self.state)
        state["response_mode"] = "side_question"
        state["active_recall_question"] = "model(batch) 之后哪个 NODE 消费返回值？"
        errors = validate_teaching_response.validate_response(
            valid_response().replace("model(batch) 之后哪个 NODE 消费返回值？", "另一个问题？"),
            state,
        )
        self.assertTrue(any("original recall question" in error for error in errors))

    def test_missing_pre_response_hook_forbids_positive_saved_claim(self) -> None:
        state = dict(self.state)
        state["host_capabilities"] = {
            "transaction_entrypoint": True,
            "pre_response_hook": False,
            "cold_start_host": False,
            "real_compaction_hook": False,
        }
        response = valid_response().replace(
            "TX 尚未 commit，因此未声称 saved。",
            "TX 已经保存。",
        )
        errors = validate_teaching_response.validate_response(response, state)
        self.assertTrue(any("positive persistence claim is forbidden" in error for error in errors))
        capabilities = validate_teaching_response.evaluate_host_capabilities(
            state["host_capabilities"]
        )
        self.assertEqual(capabilities["capabilities"]["pre_response_hook"], "advisory")
        self.assertEqual(capabilities["capabilities"]["real_compaction_hook"], "not-run")

    def test_start_profile_uses_small_mode_contract_not_eight_node_sections(self) -> None:
        state = dict(self.state)
        state["response_profile"] = "start"
        state["content_kind"] = "state"
        response = """## 学习定位
- 当前 Step：4.1
- 当前 micro-Step：4.1.a
- 当前 RUN：RUN-train
- 当前 NODE：NODE-forward
- 主线锚点：ANCHOR-train-forward

当前先确认真实训练入口。

## 下一步
定位 dataloader 到 trainer 的调用边界。

## QA / receipt 状态
没有新问题；未执行持久化。
"""
        self.assertEqual(validate_teaching_response.validate_response(response, state), [])

    def test_question_answer_state_content_does_not_invent_numeric_shape(self) -> None:
        state = dict(self.state)
        state["response_profile"] = "question-answer"
        state["content_kind"] = "state"
        response = """## 问题结论
- 当前 Step：4.1
- 当前 micro-Step：4.1.a
- 当前 RUN：RUN-train
- 当前 NODE：NODE-forward
- 主线锚点：ANCHOR-train-forward

`optimizer.step()` 之后参数状态才改变。

## 解释与证据
调用者是 `_do_train()`；当前证据为源码 E1，尚未运行。

## 回到主线
仍回到 NODE-forward 的原回忆题。

## QA / receipt 状态
Q-064 已登记；回答事务尚未执行。
"""
        self.assertEqual(validate_teaching_response.validate_response(response, state), [])

    def test_tensor_question_requires_concrete_shape_but_config_question_does_not(self) -> None:
        state = dict(self.state)
        state["response_profile"] = "question-answer"
        base = """## 问题结论
- 当前 Step：4.1
- 当前 micro-Step：4.1.a
- 当前 RUN：RUN-train
- 当前 NODE：NODE-forward
- 主线锚点：ANCHOR-train-forward

输出进入下一节点。

## 解释与证据
源码证据为 SRC-002。

## 回到主线
返回 NODE-forward。

## QA / receipt 状态
Q-065 pending。
"""
        state["content_kind"] = "tensor"
        self.assertTrue(any("Shape" in error for error in validate_teaching_response.validate_response(base, state)))
        state["content_kind"] = "config"
        self.assertEqual(validate_teaching_response.validate_response(base, state), [])


if __name__ == "__main__":
    unittest.main()
