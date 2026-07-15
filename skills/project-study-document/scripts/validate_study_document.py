#!/usr/bin/env python3
"""Validate a project-study-document Markdown artifact or its template."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FRONTMATTER = {
    "document_type": "project-study-document",
}
SUPPORTED_SCHEMAS = {"1.0", "1.1"}

COMMON_HEADINGS = [
    "## 1. 文档身份与证据范围",
    "## 2. 学习成果摘要",
    "## 3. 项目、任务与问题定义",
    "## 5. 运行场景与真实调用链",
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

SCHEMA_HEADINGS = {
    "1.0": [
        "## 4. 动态学习路线与掌握情况",
        "## 6. 核心抽象与源码节点",
    ],
    "1.1": [
        "## 4. 动态学习路线、知识覆盖与掌握情况",
        "## 6. 可重新学习的核心知识单元",
    ],
}

DONE_STATUSES = {"done", "complete", "completed", "verified", "已完成"}
SKIPPED_STATUSES = {"skipped", "跳过", "已跳过"}
EMPTY_VALUES = {"", "-", "—", "无", "none", "n/a", "na"}


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


def clean_cell(value: str) -> str:
    value = value.strip().strip("`").strip()
    return re.sub(r"\s+", " ", value)


def normalize_step(value: str) -> str:
    value = clean_cell(value).lower()
    value = re.sub(r"^step\s*", "", value)
    return value.strip()


def normalize_status(value: str) -> str:
    return clean_cell(value).lower()


def is_empty(value: str) -> bool:
    return clean_cell(value).lower() in EMPTY_VALUES


def split_table_row(line: str) -> list[str]:
    return [clean_cell(cell) for cell in line.strip().strip("|").split("|")]


def is_separator_row(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def parse_markdown_tables(text: str) -> list[tuple[list[str], list[dict[str, str]]]]:
    lines = text.splitlines()
    tables: list[tuple[list[str], list[dict[str, str]]]] = []
    index = 0
    while index + 1 < len(lines):
        if lines[index].lstrip().startswith("|") and is_separator_row(lines[index + 1]):
            headers = split_table_row(lines[index])
            rows: list[dict[str, str]] = []
            index += 2
            while index < len(lines) and lines[index].lstrip().startswith("|"):
                cells = split_table_row(lines[index])
                if len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))
                index += 1
            tables.append((headers, rows))
            continue
        index += 1
    return tables


def find_table(
    tables: list[tuple[list[str], list[dict[str, str]]]], required_headers: set[str]
) -> list[dict[str, str]] | None:
    for headers, rows in tables:
        if required_headers.issubset(set(headers)):
            return rows
    return None


def extract_ledger_steps(ledger_text: str) -> dict[str, str]:
    steps: dict[str, str] = {}
    for headers, rows in parse_markdown_tables(ledger_text):
        step_header = "微 Step" if "微 Step" in headers else "Step" if "Step" in headers else None
        if not step_header or "状态" not in headers:
            continue
        for row in rows:
            step = normalize_step(row.get(step_header, ""))
            status = normalize_status(row.get("状态", ""))
            if step and status in DONE_STATUSES | SKIPPED_STATUSES:
                steps[step] = status
    return steps


def extract_unit_blocks(text: str) -> dict[str, str]:
    section_match = re.search(
        r"(?ms)^## 6\. 可重新学习的核心知识单元\s*$\n(.*?)(?=^## 7\.)",
        text,
    )
    if not section_match:
        return {}
    section = section_match.group(1)
    matches = list(re.finditer(r"(?m)^###\s+(UNIT-[A-Za-z0-9_.-]+)\s+—\s+.+$", section))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        blocks[match.group(1)] = section[match.start():end]
    return blocks


def validate_relearning_units(text: str, errors: list[str]) -> dict[str, set[str]]:
    blocks = extract_unit_blocks(text)
    if not blocks:
        errors.append("schema 1.1 document contains no UNIT relearning unit")
        return {}

    required_labels = [
        "- 覆盖 Step：",
        "- 前置知识：",
        "- 学习目标：",
        "- 运行位置与上游 / 下游：",
        "- 源码、配置、公式或论文位置：",
        "- 证据状态：",
    ]
    required_subheadings = [
        "#### 核心讲解",
        "#### 输入、输出、Shape、公式与状态变化",
        "#### 设计原因、替代方案与取舍",
        "#### 重要提问、误区与规范修正",
        "#### 自测",
        "#### 参考答案",
        "#### 与下一知识单元的连接",
    ]
    minimum_section_lengths = {
        "#### 核心讲解": 40,
        "#### 输入、输出、Shape、公式与状态变化": 20,
        "#### 设计原因、替代方案与取舍": 20,
        "#### 重要提问、误区与规范修正": 10,
        "#### 自测": 8,
        "#### 参考答案": 15,
        "#### 与下一知识单元的连接": 8,
    }
    covered_steps_by_unit: dict[str, set[str]] = {}
    for unit_id, block in blocks.items():
        for label in required_labels:
            if label not in block:
                errors.append(f"{unit_id} missing relearning metadata: {label}")
                continue
            value_match = re.search(rf"(?m)^{re.escape(label)}\s*(.+)$", block)
            if not value_match or is_empty(value_match.group(1)):
                errors.append(f"{unit_id} has empty relearning metadata: {label}")
        for heading in required_subheadings:
            if heading not in block:
                errors.append(f"{unit_id} missing relearning section: {heading}")
                continue
            content_match = re.search(
                rf"(?ms)^{re.escape(heading)}\s*$\n(.*?)(?=^####\s|\Z)",
                block,
            )
            content = content_match.group(1).strip() if content_match else ""
            minimum = minimum_section_lengths[heading]
            if len(content) < minimum:
                errors.append(
                    f"{unit_id} relearning section is too thin ({len(content)} < {minimum} chars): {heading}"
                )

        covered_match = re.search(r"(?m)^- 覆盖 Step：\s*(.+)$", block)
        covered_steps: set[str] = set()
        if covered_match:
            covered_steps = {
                normalize_step(item)
                for item in re.split(r"[,，、;/]+", covered_match.group(1))
                if normalize_step(item)
            }
        if not covered_steps:
            errors.append(f"{unit_id} declares no covered Step identifiers")
        covered_steps_by_unit[unit_id] = covered_steps
    return covered_steps_by_unit


def validate_step_coverage(text: str, ledger_path: Path | None, errors: list[str]) -> None:
    tables = parse_markdown_tables(text)
    rows = find_table(
        tables,
        {"Step / 微 Step", "状态", "本 Step 学到的知识", "掌握证据", "复习单元"},
    )
    if rows is None:
        errors.append("missing Step knowledge coverage table")
        return

    unit_step_declarations = validate_relearning_units(text, errors)
    unit_ids = set(unit_step_declarations)
    document_steps: dict[str, str] = {}
    referenced_units: set[str] = set()
    mapped_steps_by_unit: dict[str, set[str]] = {unit_id: set() for unit_id in unit_ids}
    for row in rows:
        step = normalize_step(row.get("Step / 微 Step", ""))
        status = normalize_status(row.get("状态", ""))
        knowledge = row.get("本 Step 学到的知识", "")
        mastery = row.get("掌握证据", "")
        row_units = set(re.findall(r"UNIT-[A-Za-z0-9_.-]+", row.get("复习单元", "")))
        if not step:
            errors.append("Step coverage row has an empty Step identifier")
            continue
        if step in document_steps:
            errors.append(f"duplicate Step coverage row: {step}")
        document_steps[step] = status
        if status in DONE_STATUSES:
            if is_empty(knowledge):
                errors.append(f"completed Step {step} has no durable learned knowledge")
            if is_empty(mastery):
                errors.append(f"completed Step {step} has no mastery evidence")
            if not row_units:
                errors.append(f"completed Step {step} maps to no UNIT relearning unit")
            missing_units = row_units - unit_ids
            if missing_units:
                errors.append(
                    f"completed Step {step} references missing units: {', '.join(sorted(missing_units))}"
                )
            referenced_units.update(row_units)
            for unit_id in row_units & unit_ids:
                mapped_steps_by_unit[unit_id].add(step)
        elif status in SKIPPED_STATUSES:
            if is_empty(knowledge):
                errors.append(f"skipped Step {step} must state its reason and learning impact")
        else:
            errors.append(f"Step {step} has non-final status in final coverage table: {status!r}")

    unreferenced_units = unit_ids - referenced_units
    if unreferenced_units:
        errors.append(
            "UNIT relearning units are not mapped from any completed Step: "
            + ", ".join(sorted(unreferenced_units))
        )

    for unit_id in sorted(unit_ids):
        declared = unit_step_declarations[unit_id]
        mapped = mapped_steps_by_unit[unit_id]
        if declared != mapped:
            errors.append(
                f"{unit_id} Step declaration does not match coverage rows: "
                f"declared={sorted(declared)!r}, mapped={sorted(mapped)!r}"
            )

    summary_rows = find_table(tables, {"指标", "数量或结论"})
    if summary_rows is None:
        errors.append("missing Step coverage summary table")
    else:
        summary = {
            clean_cell(row.get("指标", "")): clean_cell(row.get("数量或结论", ""))
            for row in summary_rows
        }
        unmapped_values = [summary.get("未映射 Step", "")]
        if not unmapped_values or clean_cell(unmapped_values[0]).lower() not in {"无", "none", "0"}:
            errors.append("Step coverage summary must report zero unmapped Steps")
        expected_counts = {
            "已完成 Step / 微 Step": sum(
                status in DONE_STATUSES for status in document_steps.values()
            ),
            "已映射到复习单元": sum(
                status in DONE_STATUSES for status in document_steps.values()
            ),
            "已明确跳过": sum(
                status in SKIPPED_STATUSES for status in document_steps.values()
            ),
        }
        for metric, expected in expected_counts.items():
            actual = summary.get(metric, "")
            if not actual.isdigit() or int(actual) != expected:
                errors.append(
                    f"Step coverage summary {metric!r} must be {expected}, got {actual!r}"
                )

    if ledger_path is None:
        errors.append("schema 1.1 final validation requires --ledger")
        return
    try:
        ledger_text = ledger_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read ledger {ledger_path}: {exc}")
        return

    ledger_steps = extract_ledger_steps(ledger_text)
    if not ledger_steps:
        errors.append("ledger contains no done/skipped Step rows to audit")
        return
    missing_steps = set(ledger_steps) - set(document_steps)
    if missing_steps:
        errors.append(
            "completed/skipped ledger Steps missing from document coverage: "
            + ", ".join(sorted(missing_steps))
        )


def validate(path: Path, allow_template: bool, ledger_path: Path | None) -> list[str]:
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

    schema = frontmatter.get("schema_version", "")
    if schema not in SUPPORTED_SCHEMAS:
        errors.append(
            f"frontmatter 'schema_version' must be one of {sorted(SUPPORTED_SCHEMAS)!r}"
        )
        return errors

    for heading in COMMON_HEADINGS + SCHEMA_HEADINGS[schema]:
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

    if schema == "1.1" and not allow_template:
        validate_step_coverage(text, ledger_path, errors)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--template", action="store_true")
    parser.add_argument(
        "--ledger",
        type=Path,
        help="source PROJECT_STUDY_LOG.md used to audit complete Step coverage",
    )
    args = parser.parse_args()

    errors = validate(args.document, args.template, args.ledger)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Valid project study document: {args.document}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
