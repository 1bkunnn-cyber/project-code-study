#!/usr/bin/env python3
"""Validate the short, source-grounded contract for every NODE response."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


NODE_TEACHING_SECTIONS = [
    "## 本 NODE 要解决的问题",
    "## 调用链",
    "## 真实代码",
    "## 输入 / 输出 / Shape / 状态",
    "## 为什么这样写",
    "## 常见错误",
    "## 自测题",
    "## QA / receipt 状态",
]
PROFILE_SECTIONS = {
    "start": ["## 学习定位", "## 下一步", "## QA / receipt 状态"],
    "node-teaching": NODE_TEACHING_SECTIONS,
    "question-answer": ["## 问题结论", "## 解释与证据", "## 回到主线", "## QA / receipt 状态"],
    "recall-assessment": ["## 回答评价", "## 完整解释", "## QA / receipt 状态"],
    "recovery": ["## 恢复结果", "## 唯一下一行动", "## QA / receipt 状态"],
    "repair": ["## 状态冲突", "## 修复动作", "## QA / receipt 状态"],
    "close": ["## 本轮沉淀", "## 等待", "## QA / receipt 状态"],
}
STATE_LABELS = {
    "current_step": "- 当前 Step：",
    "current_micro_step": "- 当前 micro-Step：",
    "current_run": "- 当前 RUN：",
    "current_node": "- 当前 NODE：",
    "mainline_anchor": "- 主线锚点：",
}
HOST_CAPABILITIES = {
    "transaction_entrypoint",
    "pre_response_hook",
    "cold_start_host",
    "real_compaction_hook",
}


def evaluate_host_capabilities(manifest: dict[str, Any]) -> dict[str, Any]:
    """Expose missing enforcement as advisory/not-run, never as implicit pass."""
    capabilities = {
        name: "enforced" if manifest.get(name) is True else (
            "not-run" if name in {"cold_start_host", "real_compaction_hook"}
            else "advisory"
        )
        for name in sorted(HOST_CAPABILITIES)
    }
    return {
        "capabilities": capabilities,
        "persistence_claims_allowed": (
            capabilities["transaction_entrypoint"] == "enforced"
            and capabilities["pre_response_hook"] == "enforced"
        ),
        "publication_claims_allowed": all(
            capabilities[name] == "enforced"
            for name in (
                "transaction_entrypoint",
                "pre_response_hook",
                "cold_start_host",
            )
        ),
    }


def validate_response(text: str, state: dict[str, Any]) -> list[str]:
    """Return blocking errors; callers must not emit a failing response."""
    errors: list[str] = []
    if state.get("state_consistent") is not True:
        errors.append("REPAIR_REQUIRED: authoritative state is inconsistent")
    if state.get("pending_user_intents"):
        errors.append("unresolved pending_user_intents must be handled before emission")
    if re.search(r"(?i)(?:已保存|已经保存|saved|validated|正式文档已生成)", text):
        host = evaluate_host_capabilities(state.get("host_capabilities", {}))
        if not host["persistence_claims_allowed"]:
            errors.append("host capability is advisory; positive persistence claim is forbidden")
    profile = state.get("response_profile", "node-teaching")
    required_sections = PROFILE_SECTIONS.get(profile)
    if required_sections is None:
        errors.append(f"unknown response profile: {profile}")
        required_sections = []
    for heading in required_sections:
        if heading not in text:
            errors.append(f"missing {profile} response section: {heading}")
    if profile == "node-teaching" and "## 真实代码" in text and not re.search(
        r"(?ms)^## 真实代码\s*$.*?```[A-Za-z0-9_+-]*\n.+?^```",
        text,
    ):
        errors.append("真实代码 section requires a fenced source excerpt")
    for key, label in STATE_LABELS.items():
        expected = str(state.get(key, "")).strip()
        if not expected:
            errors.append(f"authoritative state missing {key}")
        elif not re.search(
            rf"(?m)^{re.escape(label)}\s*`?{re.escape(expected)}`?\s*$",
            text,
        ):
            errors.append(f"response state does not match {key}: {expected}")
    content_kind = state.get("content_kind", "code")
    if content_kind == "tensor" and not re.search(r"\[[0-9,\s×x]+\]", text):
        errors.append("tensor response requires one concrete Shape")
    if content_kind == "code" and not re.search(r"```(?:[A-Za-z0-9_+-]+)?\s*\n.+?\n```", text, re.DOTALL):
        errors.append("code response requires a fenced source excerpt")
    if content_kind == "metric" and not re.search(r"(?i)(?:precision|recall|iou|ap|map)\s*=", text):
        errors.append("metric response requires an explicit formula")
    if content_kind not in {"tensor", "code", "metric", "state", "config", "concept"}:
        errors.append(f"unknown content kind: {content_kind}")
    if state.get("response_mode") == "side_question":
        recall = str(state.get("active_recall_question", "")).strip()
        if not recall or recall not in text:
            errors.append("side-question response must preserve the original recall question")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    try:
        state = json.loads(args.state.read_text(encoding="utf-8"))
        text = args.response.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors = validate_response(text, state)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("NODE teaching response contract: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
