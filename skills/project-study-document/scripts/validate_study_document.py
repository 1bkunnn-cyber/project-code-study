#!/usr/bin/env python3
"""Validate a project-study-document Markdown artifact or its template."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FRONTMATTER = {
    "document_type": "project-study-document",
    "schema_version": "1.0",
}

REQUIRED_HEADINGS = [
    "## 1. 文档身份与证据范围",
    "## 2. 学习成果摘要",
    "## 3. 项目、任务与问题定义",
    "## 4. 动态学习路线与掌握情况",
    "## 5. 运行场景与真实调用链",
    "## 6. 核心抽象与源码节点",
    "## 7. 数据、Shape 与状态流",
    "## 8. 目标函数、训练、推理与评估",
    "## 9. 论文—代码映射与设计解释",
    "## 10. 用户重要提问",
    "## 11. 误区、规范修正与认知变化",
    "## 12. 相关方法、相似思想与模块组合",
    "## 13. 实验、失败、局限与未解决事项",
    "## 14. 复现、验证与修改指南",
    "## 15. 后续行动",
    "## 16. 证据与产物索引",
]


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        raise ValueError("missing YAML frontmatter")

    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        item = re.match(r"^([A-Za-z0-9_-]+):\s*[\"']?([^\"']*)[\"']?\s*$", line)
        if item:
            values[item.group(1)] = item.group(2).strip()
    return values


def validate(path: Path, allow_template: bool) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]

    try:
        frontmatter = parse_frontmatter(text)
    except ValueError as exc:
        return [str(exc)]

    for key, expected in REQUIRED_FRONTMATTER.items():
        if frontmatter.get(key) != expected:
            errors.append(f"frontmatter {key!r} must be {expected!r}")

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing heading: {heading}")

    if "| Q-" not in text and "### Q-" not in text:
        errors.append("important-question section contains no Q-ID entry")

    if "M/C ID" not in text:
        errors.append("missing correction table")

    if not allow_template and re.search(r"\{\{[A-Z0-9_]+\}\}", text):
        errors.append("unresolved template placeholders remain")

    if frontmatter.get("validation_status") == "pending" and not allow_template:
        errors.append("validation_status is still pending")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--template", action="store_true")
    args = parser.parse_args()

    errors = validate(args.document, args.template)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Valid project study document: {args.document}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
