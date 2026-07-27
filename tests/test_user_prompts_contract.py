from __future__ import annotations

import re
import unittest
from pathlib import Path


PROMPTS = Path(__file__).resolve().parents[1] / "references" / "user-prompts.md"


class UserPromptContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PROMPTS.read_text(encoding="utf-8")

    def test_router_covers_the_full_learning_loop(self) -> None:
        required = [
            "首次启动", "选择讲解方式", "恢复已有学习", "正常继续", "提出问题",
            "回答主动回忆", "深讲当前 NODE", "Shape", "论文—代码", "修复 QA/LOG",
            "纠正旧结论", "暂停、压缩上下文", "重建项目专属路线", "关闭问题阶段",
            "最终化", "最小机器诊断", "宿主或工具异常", "项目连续性记忆初始化", "回忆题中插入问题",
        ]
        for heading in required:
            self.assertIn(heading, self.text)

    def test_prompt_router_has_required_state_and_failure_terms(self) -> None:
        for token in ("preflight", "receipt", "unsaved-partial", "unsaved-memory", "retest", "AWAITING_QUESTIONS_OR_CONTINUE", "唯一下一动作"):
            self.assertIn(token, self.text)

    def test_user_prompts_do_not_delegate_internal_recordkeeping(self) -> None:
        forbidden = [
            "请你维护 Q-ID", "请你维护 QA", "请你更新 LOG", "请你生成 receipt",
            "请你自行暂停并等待",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, self.text)

    def test_memory_initialization_requires_explicit_consent(self) -> None:
        for token in ("--user-consent", "memory-consent-pending", "拒绝则不创建", "pending_user_intents"):
            self.assertIn(token, self.text)

    def test_each_numbered_prompt_has_a_code_block(self) -> None:
        headings = re.findall(r"^##\s+(\d+)\.\s+", self.text, flags=re.MULTILINE)
        self.assertEqual(headings, [str(i) for i in range(0, 19)])
        blocks = re.findall(r"```text\n.*?\n```", self.text, flags=re.DOTALL)
        self.assertGreaterEqual(len(blocks), 19)


if __name__ == "__main__":
    unittest.main()
