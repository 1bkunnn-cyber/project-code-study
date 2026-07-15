#!/usr/bin/env python3
"""Validate project-code-study schema 4 records and legacy schema 3.1 ledgers."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


LEGACY_H2 = [
    "阅读导航", "状态规范", "1. 当前状态", "2. 学习契约", "3. 学习路线",
    "4. 掌握度地图", "5. 证据索引", "6. 开放事项", "7. 误区与纠正",
    "8. 用户问题", "9. 实验、命令与失败尝试", "10. 论文、代码与来源冲突",
    "11. 复习队列", "12. 维护状态", "13. 里程碑总结", "14. 会话日志",
    "15. 用户心得与学习感受", "16. 用户问题与反馈",
]

LOG_V4_H2 = [
    "阅读导航", "状态规范", "1. 当前状态与主线锚点", "2. 学习契约",
    "3. 动态学习路线", "4. Step 知识卡与掌握度", "5. 证据索引",
    "6. 开放事项", "7. 误区、纠正与规范表述", "8. 问题索引",
    "9. 实验、命令与失败尝试", "10. 来源冲突、相关方法与组合延伸",
    "11. 复习队列", "12. 维护状态", "13. 里程碑总结", "14. 会话日志",
    "15. 用户心得摘要", "16. 用户反馈摘要",
]

QA_V1_H2 = [
    "1. 问题索引", "2. 详细问答", "3. 用户心得与学习感受",
    "4. 用户反馈", "5. 维护与归档",
]

COMMON_METADATA = [
    "document_type", "schema_version", "project_name", "project_path",
    "created_at", "updated_at", "write_authorized",
]

LOG_V4_METADATA = COMMON_METADATA + [
    "qa_path", "current_step", "current_micro_step", "current_scenario",
    "current_node", "study_mode",
]

LEGACY_METADATA = [
    "document_type", "schema_version", "project_name", "project_path",
    "created_at", "updated_at", "current_step", "study_mode", "write_authorized",
]

QA_METADATA = COMMON_METADATA + ["ledger_path"]

LOG_V4_HEADERS = [
    "| Step | 主题 | 状态 | 完成标准 | 当前行为证据 | 下一决策 |",
    "| Scenario ID | 场景 | 入口 / 命令 | 目标输出 | 静态或运行验证 | 状态 |",
    "| 顺序 | 场景 | 微 Step | Node ID | 调用者 | 当前类 / 函数 | 下游节点 | 输入 / 输出 | 前置依赖 | 状态 |",
    "| Step | Node ID | 核心结论 | 调用 / Shape 边界 | 证据 ID | 修正 ID | 状态 |",
    "| ID | 概念或能力 | 重要性 | 掌握度 | 行为证据 | 自信度 1-5 | 最近测试 | 下次复习 |",
    "| Q ID | Step / Node | 问题摘要 | Parent Q | 状态 | 是否阻塞 | 修正 / 证据 ID | 下一动作 |",
    "| Session ID | 日期 | Step / Node | 模式 / 时长 | 本次目标 | 学习与问题 IDs | 行为证据 | 状态变化 | 会话结果 | 唯一下一行动 |",
]

QA_HEADERS = [
    "| Q ID | 日期 | Step / Node | 类型 | 问题摘要 | Parent Q | 状态 | 回答位置 | 修正 ID |",
    "| NOTE ID | 日期 | Step / Node | 用户原文 | 自信度 1-5 | 希望如何调整 | AI 已读取 / 调整 | 状态 |",
    "| FB ID | 日期 | Step / Node | 类型 | 用户反馈原文 | 为什么不满意 / 困难 | 希望得到什么 | 评分 1-5 | AI 回应摘要 | 调整动作 | 状态 |",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="ledger, Q&A record, or canonical template")
    parser.add_argument("--template", action="store_true", help="allow {{PLACEHOLDER}} values")
    return parser.parse_args()


def frontmatter_of(text: str) -> tuple[str, list[str]]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        errors.append("missing YAML frontmatter")
    match = re.match(r"---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        errors.append("invalid or unclosed YAML frontmatter")
        return "", errors
    return match.group(1), errors


def field(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}\s*:\s*[\"']?([^\"'\n]+)[\"']?\s*$", frontmatter, re.MULTILINE)
    return match.group(1).strip() if match else None


def validate_required_metadata(frontmatter: str, keys: list[str], errors: list[str]) -> None:
    for key in keys:
        if not re.search(rf"^{re.escape(key)}\s*:", frontmatter, flags=re.MULTILINE):
            errors.append(f"missing metadata key: {key}")


def validate_headings(text: str, expected: list[str], errors: list[str]) -> None:
    headings = re.findall(r"^## (.+?)\s*$", text, flags=re.MULTILINE)
    if headings != expected:
        errors.append("H2 headings or their order differ from the canonical schema")


def validate_headers(text: str, expected: list[str], errors: list[str]) -> None:
    for header in expected:
        if header not in text:
            errors.append(f"missing or changed table header: {header}")


def main() -> int:
    args = parse_args()
    if not args.path.is_file():
        print(f"ERROR: file not found: {args.path}")
        return 2

    text = args.path.read_text(encoding="utf-8-sig")
    frontmatter, errors = frontmatter_of(text)
    document_type = field(frontmatter, "document_type")
    schema_version = field(frontmatter, "schema_version")

    if document_type == "project-code-study-ledger" and schema_version == "4.0":
        validate_required_metadata(frontmatter, LOG_V4_METADATA, errors)
        validate_headings(text, LOG_V4_H2, errors)
        validate_headers(text, LOG_V4_HEADERS, errors)
        label = "learning ledger schema 4.0"
    elif document_type == "project-code-study-qa" and schema_version == "1.0":
        validate_required_metadata(frontmatter, QA_METADATA, errors)
        validate_headings(text, QA_V1_H2, errors)
        validate_headers(text, QA_HEADERS, errors)
        label = "Q&A record schema 1.0"
    elif document_type == "project-code-study-ledger" and schema_version == "3.1":
        validate_required_metadata(frontmatter, LEGACY_METADATA, errors)
        validate_headings(text, LEGACY_H2, errors)
        label = "legacy learning ledger schema 3.1"
    else:
        errors.append(f"unsupported document_type/schema_version: {document_type!r}/{schema_version!r}")
        label = "unknown record"

    if not args.template:
        placeholders = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text)))
        if placeholders:
            errors.append("uninitialized placeholders: " + ", ".join(placeholders))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Valid {label}: {args.path}")
    if schema_version == "3.1":
        print("NOTE: legacy schema is supported; migrate to schema 4.0 only with authorization")
    return 0


if __name__ == "__main__":
    sys.exit(main())
