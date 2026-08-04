#!/usr/bin/env python3
"""Validate the short, source-grounded contract for every NODE response."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


REQUIRED_SECTIONS = [
    "## 本 NODE 要解决的问题",
    "## 调用链",
    "## 真实代码",
    "## 输入 / 输出 / Shape / 状态",
    "## 为什么这样写",
    "## 常见错误",
    "## 自测题",
    "## QA / receipt 状态",
]
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
    for heading in REQUIRED_SECTIONS:
        if heading not in text:
            errors.append(f"missing NODE teaching section: {heading}")
    if "## 真实代码" in text and not re.search(
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
    shape = re.search(
        r"(?ms)^## 输入 / 输出 / Shape / 状态\s*$\n(.*?)(?=^##\s|\Z)",
        text,
    )
    if shape and not re.search(r"\[[0-9,\s×x]+\]", shape.group(1)):
        errors.append("NODE response requires one concrete Shape")
    if state.get("response_mode") == "recall_answer":
        for heading in ("## 回答评价", "## 完整解释"):
            if heading not in text:
                errors.append(f"recall answer must include {heading}")
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
