#!/usr/bin/env python3
"""Validate the fixed structure of a project-code-study learning ledger."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_H2 = [
    "阅读导航",
    "状态规范",
    "1. 当前状态",
    "2. 学习契约",
    "3. 学习路线",
    "4. 掌握度地图",
    "5. 证据索引",
    "6. 开放事项",
    "7. 误区与纠正",
    "8. 用户问题",
    "9. 实验、命令与失败尝试",
    "10. 论文、代码与来源冲突",
    "11. 复习队列",
    "12. 维护状态",
    "13. 里程碑总结",
    "14. 会话日志",
]

REQUIRED_TABLE_HEADERS = [
    "| Step | 主题 | 状态 | 完成标准 | 当前行为证据 | 下一决策 |",
    "| ID | 概念或能力 | 重要性 | 掌握度 | 行为证据 | 自信度 1-5 | 最近测试 | 下次复习 |",
    "| ID | 类型 | 定位 | 版本 / 页码 | 实际检查内容 | 支持对象 | 状态 |",
    "| ID | 类型 | 事项 | 是否阻塞 | 需要的证据 | 下一动作 | 目标 Step | 状态 |",
    "| ID | 观察到的误解 | 如何发现 | 正确模型 | 证据 | 重测问题 | 状态 |",
    "| ID | 日期 | 假设 / 目的 | 命令或改动 | 结果 | 证据产物 | 解释 | 下一动作 |",
]

REQUIRED_METADATA = [
    "document_type",
    "schema_version",
    "project_name",
    "project_path",
    "created_at",
    "updated_at",
    "current_step",
    "study_mode",
    "write_authorized",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="PROJECT_STUDY_LOG.md or template path")
    parser.add_argument(
        "--template",
        action="store_true",
        help="Allow {{PLACEHOLDER}} values in the canonical template",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.path.is_file():
        print(f"ERROR: file not found: {args.path}")
        return 2

    text = args.path.read_text(encoding="utf-8-sig")
    errors: list[str] = []

    if not text.startswith("---\n"):
        errors.append("missing YAML frontmatter")
    frontmatter_match = re.match(r"---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not frontmatter_match:
        errors.append("invalid or unclosed YAML frontmatter")
        frontmatter = ""
    else:
        frontmatter = frontmatter_match.group(1)

    for key in REQUIRED_METADATA:
        if not re.search(rf"^{re.escape(key)}\s*:", frontmatter, flags=re.MULTILINE):
            errors.append(f"missing metadata key: {key}")

    if not re.search(r'^schema_version:\s*["\']?3\.0["\']?\s*$', frontmatter, re.MULTILINE):
        errors.append("schema_version must be 3.0")

    headings = re.findall(r"^## (.+?)\s*$", text, flags=re.MULTILINE)
    if headings != REQUIRED_H2:
        errors.append("H2 headings or their order differ from the canonical schema")

    for header in REQUIRED_TABLE_HEADERS:
        if header not in text:
            errors.append(f"missing or changed table header: {header}")

    if not args.template:
        placeholders = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text)))
        if placeholders:
            errors.append("uninitialized placeholders: " + ", ".join(placeholders))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Learning ledger is valid (schema 3.0): {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
