#!/usr/bin/env python3
"""Validate project-study-document Markdown artifacts and canonical templates."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
import validate_finalization_bundle  # noqa: E402
import validate_learning_ledger as record_validator  # noqa: E402


SUPPORTED_SCHEMAS = {"1.0", "1.1", "1.2"}
COMMON_HEADINGS = [
    "## 1. 文档身份与证据范围", "## 2. 学习成果摘要",
    "## 3. 项目、任务与问题定义", "## 5. 运行场景与真实调用链",
    "## 7. 数据、Shape 与状态流", "## 8. 目标函数、训练、推理与评估",
    "## 9. 论文—代码映射与设计解释", "## 10. 用户重要提问",
    "## 11. 误区、规范修正与认知变化", "## 12. 相关方法、相似思想与模块组合",
    "## 13. 实验、失败、局限与未解决事项", "## 14. 复现、验证与修改指南",
    "## 15. 后续行动", "## 16. 证据与产物索引",
]
SCHEMA_HEADINGS = {
    "1.0": ["## 4. 动态学习路线与掌握情况", "## 6. 核心抽象与源码节点"],
    "1.1": ["## 4. 动态学习路线、知识覆盖与掌握情况", "## 6. 可重新学习的核心知识单元"],
    "1.2": ["## 4. 动态学习路线、知识覆盖与掌握情况", "## 6. 可重新学习的核心知识单元"],
}
DONE = {"done", "complete", "completed", "verified", "已完成"}
SKIPPED = {"skipped", "stale", "跳过", "已跳过"}
EMPTY = {"", "-", "—", "无", "none", "n/a", "na", "待确认", "待补充"}
BANNED = ["详见 chat", "详见chat", "同上", "前文已解释", "见之前回答", "详见对应 UNIT"]
GENERIC_FILLERS = ["本单元为项目地图，不涉及技术误区", "本单元为概念层，无具体张量", "不涉及此方面"]
UNIT_LABELS_12 = [
    "- 覆盖 Step：", "- 前置知识：", "- 本单元解决的问题：", "- 学习目标：",
    "- 运行位置与上游 / 下游：", "- 源码、配置、公式或论文位置：",
    "- 证据状态：", "- 未验证边界：",
]
UNIT_SECTIONS_12 = {
    "#### 核心讲解": 80,
    "#### 关键源码执行顺序": 30,
    "#### 输入、输出、Shape、公式与状态变化": 30,
    "#### 设计原因、替代方案与取舍": 30,
    "#### 重要提问、误区与规范修正": 20,
    "#### 自测": 12,
    "#### 参考答案": 30,
    "#### 与下一知识单元的连接": 15,
}


def parse_frontmatter(text: str) -> dict[str, str]:
    fm, errors = record_validator.frontmatter_of(text)
    if errors:
        raise ValueError(errors[0])
    return fm


def clean(value: str | None) -> str:
    return record_validator.clean(value)


def norm(value: str | None) -> str:
    return record_validator.norm(value)


def is_empty(value: str | None) -> bool:
    return norm(value) in EMPTY or bool(re.fullmatch(r"\{\{[A-Z0-9_]+\}\}", clean(value)))


def normalize_step(value: str) -> str:
    return re.sub(r"^step\s*", "", norm(value)).strip()


def unit_matches(text: str) -> list[tuple[str, str, str]]:
    section = re.search(r"(?ms)^## 6\. 可重新学习的核心知识单元\s*$\n(.*?)(?=^## 7\.)", text)
    if not section:
        return []
    body = section.group(1)
    matches = list(re.finditer(r"(?m)^###\s+(UNIT-[A-Za-z0-9_.-]+)\s+—\s+(.+)$", body))
    result: list[tuple[str, str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        result.append((match.group(1), clean(match.group(2)), body[match.start():end]))
    return result


def section_content(block: str, heading: str) -> str:
    match = re.search(rf"(?ms)^{re.escape(heading)}\s*$\n(.*?)(?=^####\s|\Z)", block)
    return match.group(1).strip() if match else ""


def label_value(block: str, label: str) -> str:
    match = re.search(rf"(?m)^{re.escape(label)}\s*(.+)$", block)
    return clean(match.group(1)) if match else ""


def validate_units_12(text: str, errors: list[str]) -> dict[str, set[str]]:
    units = unit_matches(text)
    if not units:
        errors.append("schema 1.2 contains no UNIT relearning unit")
        return {}
    ids = [unit_id for unit_id, _, _ in units]
    titles = [title for _, title, _ in units]
    if len(ids) != len(set(ids)):
        errors.append("duplicate UNIT ID/heading detected: " + ", ".join(sorted({item for item in ids if ids.count(item) > 1})))
    if len(titles) != len(set(titles)):
        errors.append("duplicate UNIT title detected")
    anchors = re.findall(r'(?m)^<a id="(unit-[A-Za-z0-9_.-]+)"></a>\s*$', text)
    if len(anchors) != len(set(anchors)):
        errors.append("duplicate explicit UNIT anchor detected")
    expected_anchors = {f"unit-{unit_id.removeprefix('UNIT-')}" for unit_id in ids}
    if set(anchors) != expected_anchors:
        errors.append(f"UNIT anchors do not match UNIT IDs: anchors={sorted(set(anchors))}, expected={sorted(expected_anchors)}")

    coverage: dict[str, set[str]] = {}
    for unit_id, _, block in units:
        for label in UNIT_LABELS_12:
            value = label_value(block, label)
            if not value or is_empty(value):
                errors.append(f"{unit_id} missing or empty relearning metadata: {label}")
        evidence = label_value(block, "- 证据状态：")
        if evidence and not any(token in evidence for token in ("已确认", "可推断", "背景知识", "待验证", "E1", "E2", "E3", "E0")):
            errors.append(f"{unit_id} evidence status is not classified")
        source = label_value(block, "- 源码、配置、公式或论文位置：")
        if source and not re.search(r"(?:SRC-|[A-Za-z0-9_.-]+[/\\][A-Za-z0-9_.-]+|\.(?:py|js|ts|md|yaml|yml|json|toml)\b|page|页|公式)", source):
            errors.append(f"{unit_id} source location is not traceable")
        for heading, minimum in UNIT_SECTIONS_12.items():
            content = section_content(block, heading)
            if not content:
                errors.append(f"{unit_id} missing relearning section: {heading}")
            elif len(content) < minimum:
                errors.append(f"{unit_id} relearning section too thin ({len(content)} < {minimum}): {heading}")
        covered = label_value(block, "- 覆盖 Step：")
        steps = {normalize_step(item) for item in re.split(r"[,，、;/]+", covered) if normalize_step(item)}
        if not steps:
            errors.append(f"{unit_id} declares no covered Step identifiers")
        coverage[unit_id] = steps
    return coverage


def extract_ledger_steps(text: str) -> dict[str, str]:
    tables = record_validator.tables_of(text)
    rows = record_validator.find_table(tables, {"Step", "状态"}) or []
    result: dict[str, str] = {}
    for row in rows:
        step = normalize_step(row.get("Step", ""))
        status = norm(row.get("状态"))
        if step and status in DONE | SKIPPED:
            result[step] = status
    return result


def validate_coverage(text: str, ledger_text: str, errors: list[str]) -> None:
    tables = record_validator.tables_of(text)
    rows = record_validator.find_table(tables, {"Step / 微 Step", "状态", "本 Step 学到的知识", "掌握证据", "复习单元"})
    if rows is None:
        errors.append("missing Step knowledge coverage table")
        return
    units = validate_units_12(text, errors)
    unit_ids = set(units)
    doc_steps: dict[str, str] = {}
    mapped_by_unit = {unit_id: set() for unit_id in unit_ids}
    referenced: set[str] = set()
    for row in rows:
        step = normalize_step(row.get("Step / 微 Step", ""))
        status = norm(row.get("状态"))
        if not step:
            errors.append("Step coverage row has empty identifier")
            continue
        if step in doc_steps:
            errors.append(f"duplicate Step coverage row: {step}")
        doc_steps[step] = status
        row_units = set(re.findall(r"UNIT-[A-Za-z0-9_.-]+", row.get("复习单元", "")))
        if status in DONE:
            if is_empty(row.get("本 Step 学到的知识")):
                errors.append(f"completed Step {step} has no durable learned knowledge")
            if is_empty(row.get("掌握证据")):
                errors.append(f"completed Step {step} has no mastery evidence")
            if not row_units:
                errors.append(f"completed Step {step} maps to no UNIT")
            for missing in row_units - unit_ids:
                errors.append(f"completed Step {step} references missing unit {missing}")
            for unit_id in row_units & unit_ids:
                mapped_by_unit[unit_id].add(step)
            referenced.update(row_units)
        elif status in SKIPPED:
            if is_empty(row.get("本 Step 学到的知识")):
                errors.append(f"skipped Step {step} lacks reason and impact")
        else:
            errors.append(f"Step {step} has non-final status: {status!r}")
    for unit_id in unit_ids - referenced:
        errors.append(f"UNIT is not mapped from a completed Step: {unit_id}")
    for unit_id in unit_ids:
        if units[unit_id] != mapped_by_unit[unit_id]:
            errors.append(f"{unit_id} Step declaration differs from coverage rows")

    summary_rows = record_validator.find_table(tables, {"指标", "数量或结论"}) or []
    summary = {clean(row.get("指标")): clean(row.get("数量或结论")) for row in summary_rows}
    expected = {
        "已完成 Step / 微 Step": sum(status in DONE for status in doc_steps.values()),
        "已映射到复习单元": sum(status in DONE for status in doc_steps.values()),
        "已明确跳过": sum(status in SKIPPED for status in doc_steps.values()),
    }
    if norm(summary.get("未映射 Step")) not in {"无", "none", "0"}:
        errors.append("Step coverage summary must report zero unmapped Steps")
    for metric, value in expected.items():
        actual = clean(summary.get(metric))
        if not actual.isdigit() or int(actual) != value:
            errors.append(f"Step coverage summary {metric!r} must be {value}, got {actual!r}")
    ledger_steps = extract_ledger_steps(ledger_text)
    if not ledger_steps:
        errors.append("ledger contains no done/skipped Step rows")
    missing = set(ledger_steps) - set(doc_steps)
    if missing:
        errors.append("ledger Steps missing from document coverage: " + ", ".join(sorted(missing)))
    extra_done = {step for step, status in doc_steps.items() if status in DONE} - set(ledger_steps)
    if extra_done:
        errors.append("document promotes Steps not final in ledger: " + ", ".join(sorted(extra_done)))


def validate_questions(text: str, qa_text: str, errors: list[str]) -> None:
    qa_tables = record_validator.tables_of(qa_text)
    rows = record_validator.find_table(qa_tables, {"Q ID", "状态", "Parent Q", "Transaction ID"}) or []
    qa_ids = set(record_validator.ids_in(rows, "Q ID", "Q"))
    included = set(re.findall(r"(?m)^###\s+(Q-\d+)\b", text))
    if qa_ids and not included:
        errors.append("important-question section contains no Q-ID entry")
    correction_qs = {clean(row.get("Q ID")) for row in rows if norm(row.get("修正 ID")) not in {"", "none", "无", "-"}}
    missing_correction_qs = correction_qs - included
    if missing_correction_qs:
        errors.append("correction-triggering Q IDs omitted: " + ", ".join(sorted(missing_correction_qs)))
    unknown = included - qa_ids
    if unknown:
        errors.append("document includes Q IDs absent from source Q&A: " + ", ".join(sorted(unknown)))


def promoted_text_without_history(text: str) -> str:
    return re.sub(r"(?ms)^## 11\. 误区、规范修正与认知变化\s*$.*?(?=^## 12\.)", "", text)


def validate_stale_patterns(text: str, ledger_text: str, errors: list[str]) -> None:
    rows = record_validator.find_table(record_validator.tables_of(ledger_text), {"ID", "Stale pattern", "Transaction ID", "状态"}) or []
    promoted = promoted_text_without_history(text)
    for row in rows:
        pattern = clean(row.get("Stale pattern"))
        if not is_empty(pattern) and pattern in promoted:
            errors.append(f"promoted content contains stale pattern from {row.get('ID')}: {pattern}")


def validate(path: Path, *, allow_template: bool, ledger_path: Path | None, qa_path: Path | None, preflight: bool) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        return [f"cannot read {path}: {exc}"]
    try:
        fm = parse_frontmatter(text)
    except ValueError as exc:
        return [str(exc)]
    errors: list[str] = []
    if fm.get("document_type") != "project-study-document":
        errors.append("frontmatter document_type must be 'project-study-document'")
    schema = fm.get("schema_version", "")
    if schema not in SUPPORTED_SCHEMAS:
        return errors + [f"unsupported schema_version: {schema!r}"]
    for heading in COMMON_HEADINGS + SCHEMA_HEADINGS[schema]:
        if heading not in text:
            errors.append(f"missing heading: {heading}")
    if text.count("```") % 2:
        errors.append("unbalanced Markdown code fences")
    if not allow_template:
        placeholders = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text)))
        if placeholders:
            errors.append("unresolved template placeholders: " + ", ".join(placeholders))
        for phrase in BANNED + GENERIC_FILLERS:
            if phrase.lower() in text.lower():
                errors.append(f"forbidden placeholder or hidden-context phrase: {phrase}")
        if schema in {"1.1", "1.2"}:
            headings = re.findall(r"(?m)^###\s+(UNIT-[A-Za-z0-9_.-]+)\s+—\s+(.+)$", text)
            unit_ids = [item[0] for item in headings]
            unit_titles = [clean(item[1]) for item in headings]
            if len(unit_ids) != len(set(unit_ids)):
                errors.append("duplicate UNIT ID/heading detected")
            if len(unit_titles) != len(set(unit_titles)):
                errors.append("duplicate UNIT title detected")
    if schema != "1.2" or allow_template:
        return errors

    required_fm = [
        "status", "project_name", "project_path", "repository_revision",
        "source_transaction_id", "readiness_transaction_id", "readiness_status",
        "learning_goal", "audience", "language", "generated_at", "source_ledger",
        "source_qa", "validation_status", "cold_start_status",
    ]
    for key in required_fm:
        if key not in fm or is_empty(fm.get(key)):
            errors.append(f"missing or empty frontmatter field: {key}")
    revision = norm(fm.get("repository_revision"))
    if revision in {"head", "unknown", "latest"}:
        errors.append("repository_revision must be immutable or explicit uncommitted:<hash>")
    generated = clean(fm.get("generated_at"))
    if generated and not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2})", generated):
        errors.append("generated_at must be a real ISO-8601 timestamp with timezone")
    status = norm(fm.get("status"))
    validation_status = norm(fm.get("validation_status"))
    if status == "complete":
        expected = "pending" if preflight else "validated"
        if validation_status != expected:
            errors.append(f"complete document validation_status must be {expected!r} for this pass")
    elif status == "incomplete-draft":
        if validation_status == "validated":
            errors.append("incomplete-draft cannot be validated")
    else:
        errors.append(f"artifact status must be complete or incomplete-draft, got {status!r}")

    if ledger_path is None or qa_path is None:
        errors.append("schema 1.2 validation requires --ledger and --qa")
        return errors
    try:
        ledger_text = ledger_path.read_text(encoding="utf-8-sig")
        qa_text = qa_path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        return errors + [f"cannot read source bundle: {exc}"]

    validate_coverage(text, ledger_text, errors)
    validate_questions(text, qa_text, errors)
    validate_stale_patterns(text, ledger_text, errors)
    if status == "complete":
        manifest = validate_finalization_bundle.evaluate_bundle(ledger_path, qa_path)
        if not manifest.get("ready"):
            positive_flags = {
                "route_final", "scenario_coverage_complete",
                "learner_closed_question_phase", "learner_consented_to_generation",
            }
            blockers = {
                key: value
                for key, value in manifest.items()
                if (key in positive_flags and value is False)
                or (key == "pending_user_response" and value is True)
                or (isinstance(value, list) and bool(value))
            }
            errors.append("finalization bundle is not ready: " + repr(blockers))
        if norm(fm.get("readiness_status")) not in {"ready", "pass", "true"}:
            errors.append("complete document readiness_status is not ready/pass")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--template", action="store_true")
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--qa", type=Path)
    parser.add_argument("--preflight", action="store_true", help="accept pending validation_status before final commit")
    args = parser.parse_args()
    errors = validate(args.document, allow_template=args.template, ledger_path=args.ledger, qa_path=args.qa, preflight=args.preflight)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Valid project study document: {args.document}")
    print("Validation pass: preflight" if args.preflight else "Validation pass: final")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
