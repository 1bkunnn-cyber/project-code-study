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
import cold_start_test  # noqa: E402


SUPPORTED_SCHEMAS = {"1.0", "1.1", "1.2", "2.0", "2.1"}
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
    "2.0": ["## 4. 动态学习路线、知识覆盖与掌握情况", "## 6. 逐 Step 教材章节"],
    "2.1": [
        "## 0. 如何查阅这份手册",
        "## 快速检索索引",
        "## 4. 动态学习路线、知识覆盖与掌握情况",
        "## 6. 逐 Step 手册",
    ],
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

CHAPTER_LABELS_20 = [
    "- 覆盖 Step：",
    "- 本 Step 要解决的问题：",
    "- 前置知识：",
    "- 真实调用链位置：",
    "- 上游输入与下游输出：",
    "- 相关 RUN / NODE / micro-Step：",
    "- 源码锚点：",
    "- 本章学习完成标准：",
]
CHAPTER_SECTIONS_20 = {
    "#### 本章教材讲解": 160,
    "#### 调用链与前后 NODE": 60,
    "#### 关键源码片段": 40,
    "#### 逐段或逐行解释": 80,
    "#### 变量、参数与状态": 60,
    "#### 输入、输出、Shape 与状态变化": 80,
    "#### 数学公式与参数计算": 60,
    "#### 为什么这样设计、替代实现与取舍": 80,
    "#### 常见错误和错误表现": 60,
    "#### 当前项目具体例子": 70,
    "#### 重要 QA 问题和完整答案": 80,
    "#### 回忆题与练习题": 45,
    "#### 参考答案": 70,
    "#### 已确认、可推断、待验证的证据边界": 50,
    "#### 与前后 NODE 的连接": 45,
}

COMPACT_STEP_LABELS = [
    "- 覆盖 Step：",
    "- 阅读层级：",
    "- 预计复习时间：",
    "- 检索关键词：",
    "- 本 Step 要解决的问题：",
    "- 真实调用链位置：",
    "- 相关 RUN / NODE / micro-Step：",
    "- 源码锚点：",
    "- 学习完成标准：",
]
COMPACT_STEP_SECTIONS = {
    "#### 30 秒定位": 70,
    "#### 调用链与数据边界": 90,
    "#### 精选源码证据": 80,
    "#### 核心机制": 100,
    "#### 设计取舍与故障定位": 80,
    "#### 项目例子与重要 QA": 80,
    "#### 自测与参考答案": 80,
    "#### 证据边界与下一跳": 80,
}
READING_PROFILES = {
    "compact": {"min_prose": 450, "max_prose": 1200, "max_excerpts": 1, "max_lines": 24},
    "standard": {"min_prose": 800, "max_prose": 2200, "max_excerpts": 2, "max_lines": 60},
    "specialist": {"min_prose": 1400, "max_prose": 3600, "max_excerpts": 4, "max_lines": 120},
}
SOURCE_EXCERPT_PATTERN = re.compile(
    r"(?ms)^-\s*源码摘录：\s*(.+?):(\d+)-(\d+)\s*$"
    r"\s*```[^\n]*\n(.*?)^```\s*$"
)


def _source_excerpt_matches(block: str, repo_root: Path) -> list[str]:
    errors: list[str] = []
    excerpts = list(SOURCE_EXCERPT_PATTERN.finditer(block))
    if not excerpts:
        return ["chapter contains no '<relative path>:start-end' fenced source excerpt"]
    for match in excerpts:
        relative, raw_start, raw_end, excerpt = match.groups()
        path = (repo_root / relative.strip().replace("\\", "/")).resolve()
        try:
            path.relative_to(repo_root.resolve())
        except ValueError:
            errors.append(f"source excerpt escapes repository: {relative}")
            continue
        if not path.is_file():
            errors.append(f"source excerpt path does not exist: {relative}")
            continue
        start, end = int(raw_start), int(raw_end)
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        if start < 1 or end < start or end > len(lines):
            errors.append(f"source excerpt line range is invalid: {relative}:{start}-{end}")
            continue
        expected = "\n".join(lines[start - 1:end]).strip()
        if excerpt.strip() != expected:
            errors.append(
                f"source excerpt does not match source lines: {relative}:{start}-{end}"
            )
    return errors


def _prose_length(block: str) -> int:
    without_code = re.sub(r"(?ms)```.*?```", "", block)
    without_structure = re.sub(
        r"(?m)^(?:#{1,6}\s+|-\s+[^：\n]+：|<a\s+id=.*$).*$",
        "",
        without_code,
    )
    return len(re.sub(r"\s+", "", without_structure))


def validate_excerpt_budget(block: str, profile: str, repo_root: Path) -> list[str]:
    """Limit exact excerpts to the smallest source evidence needed for one Step."""
    errors: list[str] = []
    limits = READING_PROFILES.get(profile)
    if limits is None:
        return [f"unknown reading profile: {profile!r}"]
    matches = list(SOURCE_EXCERPT_PATTERN.finditer(block))
    if len(matches) > limits["max_excerpts"]:
        errors.append(
            f"{profile} profile source excerpt count exceeds budget "
            f"({len(matches)} > {limits['max_excerpts']})"
        )
    total_lines = 0
    covered_by_file: dict[Path, set[int]] = {}
    for match in matches:
        relative, raw_start, raw_end, _ = match.groups()
        start, end = int(raw_start), int(raw_end)
        excerpt_lines = end - start + 1
        total_lines += excerpt_lines
        if excerpt_lines > 45:
            errors.append(
                f"single source excerpt exceeds 45 lines: "
                f"{relative.strip()}:{start}-{end}"
            )
        path = (repo_root / relative.strip().replace("\\", "/")).resolve()
        try:
            path.relative_to(repo_root.resolve())
        except ValueError:
            continue
        if not path.is_file():
            continue
        file_lines = path.read_text(encoding="utf-8-sig").splitlines()
        covered_by_file.setdefault(path, set()).update(range(start, end + 1))
        if len(file_lines) < 20 and excerpt_lines > 12:
            errors.append(
                f"small-file source excerpt exceeds 12 lines: "
                f"{relative.strip()}:{start}-{end}"
            )
    if total_lines > limits["max_lines"]:
        errors.append(
            f"{profile} profile source line budget exceeded "
            f"({total_lines} > {limits['max_lines']})"
        )
    for path, covered in covered_by_file.items():
        file_line_count = len(path.read_text(encoding="utf-8-sig").splitlines())
        if file_line_count >= 20 and len(covered) / file_line_count > 0.35:
            relative = path.relative_to(repo_root.resolve()).as_posix()
            errors.append(
                f"source coverage is too high for a handbook excerpt: "
                f"{relative} ({len(covered)}/{file_line_count} > 35%)"
            )
    return errors


def validate_compact_step_contract(
    step_id: str,
    block: str,
    *,
    repo_root: Path | None = None,
) -> list[str]:
    """Validate one schema 2.1 progressive-disclosure Step manual entry."""
    errors: list[str] = []
    if not re.search(r"(?m)^###\s+CHAPTER-[A-Za-z0-9_.-]+\s+—\s+\S+", block):
        errors.append(f"Step {step_id} has no unique CHAPTER heading")
    for label in COMPACT_STEP_LABELS:
        value = label_value(block, label)
        if not value or is_empty(value):
            errors.append(f"Step {step_id} missing compact handbook metadata: {label}")
    profile = norm(label_value(block, "- 阅读层级："))
    if profile not in READING_PROFILES:
        errors.append(f"Step {step_id} has invalid reading profile: {profile!r}")
    covered = {
        normalize_step(item)
        for item in re.split(
            r"[,，、;/]+",
            label_value(block, "- 覆盖 Step："),
        )
        if normalize_step(item)
    }
    if normalize_step(step_id) not in covered:
        errors.append(f"Step {step_id} compact entry does not declare its covered Step")
    for heading, minimum in COMPACT_STEP_SECTIONS.items():
        content = section_content(block, heading)
        if not content:
            errors.append(f"Step {step_id} missing compact handbook section: {heading}")
        elif len(re.sub(r"\s+", "", content)) < minimum:
            errors.append(
                f"Step {step_id} compact handbook section too thin: {heading}"
            )
    prose_length = _prose_length(block)
    if profile in READING_PROFILES:
        limits = READING_PROFILES[profile]
        if not limits["min_prose"] <= prose_length <= limits["max_prose"]:
            errors.append(
                f"Step {step_id} prose budget violation for {profile} "
                f"({prose_length} not in "
                f"{limits['min_prose']}-{limits['max_prose']})"
            )
    qa = section_content(block, "#### 项目例子与重要 QA")
    if qa and not re.search(r"\bQ-\d+\b", qa):
        errors.append(f"Step {step_id} important QA has no Q-ID")
    boundary = section_content(block, "#### 证据边界与下一跳")
    for level in ("已确认", "可推断", "待验证"):
        if boundary and level not in boundary:
            errors.append(f"Step {step_id} evidence boundary omits {level}")
    data = section_content(block, "#### 调用链与数据边界")
    if data and not re.search(r"\[[0-9,\s×x]+\]", data):
        errors.append(f"Step {step_id} has no concrete Shape example")
    if repo_root is not None:
        errors.extend(_source_excerpt_matches(block, repo_root))
        if profile in READING_PROFILES:
            errors.extend(validate_excerpt_budget(block, profile, repo_root))
    return errors


def validate_chapter_duplication(
    chapters: list[tuple[str, str, str]],
) -> list[str]:
    """Reject long prose copied verbatim between Step entries."""
    owners: dict[str, str] = {}
    errors: list[str] = []
    for chapter_id, _, block in chapters:
        prose = re.sub(r"(?ms)```.*?```", "", block)
        for paragraph in re.split(r"\n\s*\n", prose):
            normalized = re.sub(r"\s+", "", paragraph).strip()
            if len(normalized) < 80 or normalized.startswith(("#", "-", "<a")):
                continue
            previous = owners.get(normalized)
            if previous and previous != chapter_id:
                errors.append(
                    f"repeated handbook paragraph across {previous} and {chapter_id}"
                )
            else:
                owners[normalized] = chapter_id
    return sorted(set(errors))


def validate_specialist_reading_profile(step_id: str, block: str) -> list[str]:
    specialist = (
        step_id == "4"
        or step_id.startswith("4.")
        or step_id == "6"
        or step_id.startswith("6.")
        or step_id == "10"
        or step_id.startswith("10.")
    )
    if specialist and norm(label_value(block, "- 阅读层级：")) != "specialist":
        return [f"Step {step_id} requires the specialist reading profile"]
    return []


def validate_lookup_index(
    text: str,
    *,
    completed_steps: set[str],
    required_qids: set[str],
) -> list[str]:
    """Require one navigable lookup row per completed Step and required Q-ID."""
    errors: list[str] = []
    rows = record_validator.find_table(
        record_validator.tables_of(text),
        {"Step", "关键词", "源码 / 符号", "重要 Q", "手册条目"},
    )
    if rows is None:
        return ["schema 2.1 is missing the quick lookup index table"]
    chapter_anchors = set(
        re.findall(
            r'(?m)^<a id="(chapter-[A-Za-z0-9_.-]+)"></a>\s*$',
            text,
        )
    )
    indexed_steps: set[str] = set()
    indexed_qids: set[str] = set()
    for row in rows:
        step = normalize_step(row.get("Step", ""))
        if step:
            indexed_steps.add(step)
        for field in ("关键词", "源码 / 符号", "手册条目"):
            if is_empty(row.get(field)):
                errors.append(f"lookup index Step {step or '?'} has empty {field}")
        entry_targets = re.findall(
            r"\]\(#(chapter-[A-Za-z0-9_.-]+)\)",
            row.get("手册条目", ""),
        )
        if len(entry_targets) != 1 or entry_targets[0] not in chapter_anchors:
            errors.append(
                f"lookup index Step {step or '?'} has no resolvable "
                "manual-entry anchor"
            )
        indexed_qids.update(re.findall(r"\bQ-\d+\b", row.get("重要 Q", "")))
    for step in sorted(completed_steps - indexed_steps):
        errors.append(f"lookup index is missing completed Step {step}")
    for qid in sorted(required_qids - indexed_qids):
        errors.append(f"lookup index is missing required question {qid}")
    return errors


def validate_chapter_contract(
    step_id: str,
    block: str,
    *,
    repo_root: Path | None = None,
) -> list[str]:
    """Validate one standalone textbook chapter against the 20-part contract."""
    errors: list[str] = []
    if not re.search(r"(?m)^###\s+CHAPTER-[A-Za-z0-9_.-]+\s+—\s+\S+", block):
        errors.append(f"Step {step_id} has no unique CHAPTER heading")
    for label in CHAPTER_LABELS_20:
        value = label_value(block, label)
        if not value or is_empty(value):
            errors.append(f"Step {step_id} missing chapter metadata: {label}")
    covered = {
        normalize_step(item)
        for item in re.split(r"[,，、;/]+", label_value(block, "- 覆盖 Step："))
        if normalize_step(item)
    }
    if normalize_step(step_id) not in covered:
        errors.append(f"Step {step_id} chapter does not declare its covered Step")
    for heading, minimum in CHAPTER_SECTIONS_20.items():
        content = section_content(block, heading)
        if not content:
            errors.append(f"Step {step_id} missing handbook section: {heading}")
        elif len(content) < minimum:
            errors.append(
                f"Step {step_id} handbook section too thin "
                f"({len(content)} < {minimum}): {heading}"
            )
    qa = section_content(block, "#### 重要 QA 问题和完整答案")
    if qa and not re.search(r"\bQ-\d+\b", qa):
        errors.append(f"Step {step_id} important QA section has no Q-ID")
    boundary = section_content(block, "#### 已确认、可推断、待验证的证据边界")
    for level in ("已确认", "可推断", "待验证"):
        if boundary and level not in boundary:
            errors.append(f"Step {step_id} evidence boundary omits {level}")
    shape = section_content(block, "#### 输入、输出、Shape 与状态变化")
    if shape and not re.search(r"\[[0-9,\s×x]+\]", shape):
        errors.append(f"Step {step_id} has no concrete Shape example")
    if repo_root is not None:
        errors.extend(_source_excerpt_matches(block, repo_root))
    elif not re.search(r"(?m)^-\s*源码摘录：\s*.+:\d+-\d+\s*$", block):
        errors.append(f"Step {step_id} has no exact source line range")
    return errors


def validate_special_step_contracts(text: str, completed_steps: set[str]) -> list[str]:
    """Enforce project-critical teaching depth that generic length cannot prove."""
    errors: list[str] = []
    normalized = {normalize_step(step) for step in completed_steps}
    if any(step == "4" or step.startswith("4.") for step in normalized):
        required = [
            "_do_train()",
            "model(batch)",
            "DetectionModel.forward()",
            "v8DetectionLoss",
            "梯度累积",
            "AMP",
            "EMA",
            "optimizer",
            "epoch",
            "验证",
            "保存",
            "[8,3,640,640]",
            "Conv",
            "C2f",
            "SPPF",
            "Upsample",
            "Concat",
            "Detect",
            "parse_model()",
        ]
        compact = re.sub(r"\s+", "", text)
        missing = [token for token in required if re.sub(r"\s+", "", token) not in compact]
        if missing:
            errors.append("Step 4.x handbook missing: " + ", ".join(missing))
    if "6" in normalized or any(step.startswith("6.") for step in normalized):
        required = ["TP", "FP", "FN", "IoU", "AP", "mAP", "results.csv", "可视化", "评估源码"]
        missing = [token for token in required if token not in text]
        if missing:
            errors.append("Step 6 handbook missing: " + ", ".join(missing))
    if "10" in normalized or any(step.startswith("10.") for step in normalized):
        required = ["缝合", "SE", "baseline", "消融", "创新验证"]
        missing = [token for token in required if token.lower() not in text.lower()]
        if missing:
            errors.append("Step 10 handbook missing: " + ", ".join(missing))
    return errors


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


def chapter_matches(text: str) -> list[tuple[str, str, str]]:
    section = re.search(
        r"(?ms)^## 6\. 逐 Step (?:教材章节|手册)\s*$\n(.*?)(?=^## 7\.)",
        text,
    )
    if not section:
        return []
    body = section.group(1)
    matches = list(
        re.finditer(r"(?m)^###\s+(CHAPTER-[A-Za-z0-9_.-]+)\s+—\s+(.+)$", body)
    )
    result: list[tuple[str, str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        result.append((match.group(1), clean(match.group(2)), body[match.start():end]))
    return result


def validate_deep_dive_links(text: str) -> list[str]:
    """Keep progressive-disclosure links inside the hash-bound document."""
    targets = set(
        re.findall(r"\]\(#(deep-dive-[A-Za-z0-9_.-]+)\)", text, re.IGNORECASE)
    )
    anchors = set(
        re.findall(
            r'(?m)^<a id="(deep-dive-[A-Za-z0-9_.-]+)"></a>\s*$',
            text,
            re.IGNORECASE,
        )
    )
    return [
        f"document-local deep-dive link has no matching anchor: {target}"
        for target in sorted(targets - anchors)
    ]


def section_content(block: str, heading: str) -> str:
    match = re.search(rf"(?ms)^{re.escape(heading)}\s*$\n(.*?)(?=^####\s|\Z)", block)
    return match.group(1).strip() if match else ""


def label_value(block: str, label: str) -> str:
    match = re.search(rf"(?m)^{re.escape(label)}\s*(.+)$", block)
    return clean(match.group(1)) if match else ""


def validate_units_12(text: str, errors: list[str], repo_root: Path | None = None) -> dict[str, set[str]]:
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
        if "..." in source or "<path>" in source.lower() or "TODO" in source:
            errors.append(f"{unit_id} contains placeholder source location")
        if repo_root and source:
            for relative in re.findall(r"(?<![A-Za-z0-9_./-])([A-Za-z0-9_.-]+(?:[/\\][A-Za-z0-9_.-]+)+\.(?:py|js|ts|md|yaml|yml|json|toml))(?::\d+(?:-\d+)?)?", source):
                if not (repo_root / relative).is_file():
                    errors.append(f"{unit_id} source path does not exist: {relative}")
        for heading, minimum in UNIT_SECTIONS_12.items():
            content = section_content(block, heading)
            if not content:
                errors.append(f"{unit_id} missing relearning section: {heading}")
            elif len(content) < minimum:
                errors.append(f"{unit_id} relearning section too thin ({len(content)} < {minimum}): {heading}")
        semantic_sections = {
            "#### 关键源码执行顺序": ("顺序", "first", "second", "then", "先", "随后"),
            "#### 输入、输出、Shape、公式与状态变化": ("输入", "输出", "shape", "状态", "input", "output", "state"),
            "#### 设计原因、替代方案与取舍": ("取舍", "替代", "alternative", "trade-off", "direct"),
            "#### 自测": ("自测", "重建", "解释", "验证", "reconstruct", "verify"),
            "#### 参考答案": ("答案", "应", "先", "调用", "answer", "caller", "call"),
        }
        for heading, tokens in semantic_sections.items():
            content = section_content(block, heading).lower()
            if not any(token.lower() in content for token in tokens):
                errors.append(f"{unit_id} missing semantic evidence in {heading}")
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


def validate_handbook_20(
    text: str,
    ledger_text: str,
    errors: list[str],
    *,
    repo_root: Path | None,
) -> set[str]:
    chapters = chapter_matches(text)
    if not chapters:
        errors.append("schema 2.0 contains no standalone Step handbook chapter")
        return set()
    ids = [chapter_id for chapter_id, _, _ in chapters]
    if len(ids) != len(set(ids)):
        errors.append("duplicate CHAPTER ID detected")
    anchors = re.findall(r'(?m)^<a id="(chapter-[A-Za-z0-9_.-]+)"></a>\s*$', text)
    expected_anchors = {
        f"chapter-{chapter_id.removeprefix('CHAPTER-')}"
        for chapter_id in ids
    }
    if len(anchors) != len(set(anchors)) or set(anchors) != expected_anchors:
        errors.append("CHAPTER anchors must be unique and match CHAPTER IDs")

    covered_by_chapter: set[str] = set()
    for chapter_id, _, block in chapters:
        declared = {
            normalize_step(item)
            for item in re.split(
                r"[,，、;/]+",
                label_value(block, "- 覆盖 Step："),
            )
            if normalize_step(item)
        }
        if not declared:
            errors.append(f"{chapter_id} declares no Step")
        elif len(declared) != 1:
            errors.append(f"{chapter_id} must map to exactly one completed Step")
        for step in declared:
            errors.extend(
                validate_chapter_contract(step, block, repo_root=repo_root)
            )
        duplicates = covered_by_chapter & declared
        if duplicates:
            errors.append(
                "completed Steps appear in multiple chapters: "
                + ", ".join(sorted(duplicates))
            )
        covered_by_chapter.update(declared)

    ledger_steps = extract_ledger_steps(ledger_text)
    done_steps = {
        step
        for step, status in ledger_steps.items()
        if status in DONE
    }
    missing = done_steps - covered_by_chapter
    extra = covered_by_chapter - done_steps
    if missing:
        errors.append(
            "completed ledger Steps missing standalone chapters: "
            + ", ".join(sorted(missing))
        )
    if extra:
        errors.append(
            "chapters promote Steps not completed in ledger: "
            + ", ".join(sorted(extra))
        )
    errors.extend(validate_special_step_contracts(text, done_steps))
    return done_steps


def validate_handbook_21(
    text: str,
    ledger_text: str,
    errors: list[str],
    *,
    repo_root: Path | None,
) -> set[str]:
    chapters = chapter_matches(text)
    if not chapters:
        errors.append("schema 2.1 contains no compact Step manual entry")
        return set()
    ids = [chapter_id for chapter_id, _, _ in chapters]
    if len(ids) != len(set(ids)):
        errors.append("duplicate CHAPTER ID detected")
    anchors = re.findall(
        r'(?m)^<a id="(chapter-[A-Za-z0-9_.-]+)"></a>\s*$',
        text,
    )
    expected_anchors = {
        f"chapter-{chapter_id.removeprefix('CHAPTER-')}"
        for chapter_id in ids
    }
    if len(anchors) != len(set(anchors)) or set(anchors) != expected_anchors:
        errors.append("CHAPTER anchors must be unique and match CHAPTER IDs")

    covered_by_chapter: set[str] = set()
    for chapter_id, _, block in chapters:
        declared = {
            normalize_step(item)
            for item in re.split(
                r"[,，、;/]+",
                label_value(block, "- 覆盖 Step："),
            )
            if normalize_step(item)
        }
        if len(declared) != 1:
            errors.append(
                f"{chapter_id} must map to exactly one completed Step"
            )
        for step in declared:
            errors.extend(
                validate_compact_step_contract(
                    step,
                    block,
                    repo_root=repo_root,
                )
            )
            errors.extend(validate_specialist_reading_profile(step, block))
        duplicates = covered_by_chapter & declared
        if duplicates:
            errors.append(
                "completed Steps appear in multiple chapters: "
                + ", ".join(sorted(duplicates))
            )
        covered_by_chapter.update(declared)

    errors.extend(validate_chapter_duplication(chapters))
    errors.extend(validate_deep_dive_links(text))
    ledger_steps = extract_ledger_steps(ledger_text)
    done_steps = {
        step
        for step, status in ledger_steps.items()
        if status in DONE
    }
    missing = done_steps - covered_by_chapter
    extra = covered_by_chapter - done_steps
    if missing:
        errors.append(
            "completed ledger Steps missing compact manual entries: "
            + ", ".join(sorted(missing))
        )
    if extra:
        errors.append(
            "manual entries promote Steps not completed in ledger: "
            + ", ".join(sorted(extra))
        )
    errors.extend(validate_special_step_contracts(text, done_steps))
    return done_steps


def validate_required_question_ids(
    text: str,
    qa_text: str,
    raw_ids: str,
    errors: list[str],
) -> None:
    required = set(re.findall(r"\bQ-\d+\b", raw_ids))
    qa_ids = set(re.findall(r"\bQ-\d+\b", qa_text))
    chapter_section = re.search(
        r"(?ms)^## 6\. 逐 Step (?:教材章节|手册)\s*$\n(.*?)(?=^## 7\.)",
        text,
    )
    question_section = re.search(
        r"(?ms)^## 10\. 用户重要提问\s*$\n(.*?)(?=^## 11\.)",
        text,
    )
    for qid in sorted(required):
        if qid not in qa_ids:
            errors.append(f"required question is absent from source QA: {qid}")
        if chapter_section is None or not re.search(
            rf"\b{re.escape(qid)}\b",
            chapter_section.group(1),
        ):
            errors.append(f"required question is not taught inside a chapter: {qid}")
        if question_section is None or not re.search(
            rf"\b{re.escape(qid)}\b",
            question_section.group(1),
        ):
            errors.append(
                f"required question is missing from the important-question section: {qid}"
            )


def validate_coverage(text: str, ledger_text: str, errors: list[str], repo_root: Path | None = None) -> None:
    tables = record_validator.tables_of(text)
    rows = record_validator.find_table(tables, {"Step / 微 Step", "状态", "本 Step 学到的知识", "掌握证据", "复习单元"})
    if rows is None:
        errors.append("missing Step knowledge coverage table")
        return
    units = validate_units_12(text, errors, repo_root=repo_root)
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
    question_section = re.search(
        r"(?ms)^## 10\. 用户重要提问\s*$\n(.*?)(?=^## 11\.)",
        text,
    )
    included = (
        set(re.findall(r"\bQ-\d+\b", question_section.group(1)))
        if question_section
        else set()
    )
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


def validate(
    path: Path,
    *,
    allow_template: bool,
    ledger_path: Path | None,
    qa_path: Path | None,
    preflight: bool,
    repo_root: Path | None = None,
    publication: bool = False,
    cold_start_report: Path | None = None,
) -> list[str]:
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
    if publication and schema != "2.1":
        errors.append("formal publication requires compact handbook schema 2.1")
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
    if schema not in {"1.2", "2.0", "2.1"} or allow_template:
        return errors

    required_fm = [
        "status", "project_name", "project_path", "repository_revision",
        "source_transaction_id", "readiness_transaction_id", "readiness_status",
        "learning_goal", "audience", "language", "generated_at", "source_ledger",
        "source_qa", "validation_status", "cold_start_status",
    ]
    if schema in {"2.0", "2.1"}:
        required_fm.extend(["release_transaction_id", "required_question_ids"])
    if schema == "2.1":
        required_fm.extend(["handbook_mode", "default_reading_profile"])
    for key in required_fm:
        if key not in fm or is_empty(fm.get(key)):
            errors.append(f"missing or empty frontmatter field: {key}")
    if clean(fm.get("language")).lower() != "zh-cn":
        errors.append("generated project study document requires language: zh-CN")
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
        errors.append(f"schema {schema} validation requires --ledger and --qa")
        return errors
    try:
        ledger_text = ledger_path.read_text(encoding="utf-8-sig")
        qa_text = qa_path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        return errors + [f"cannot read source bundle: {exc}"]

    if schema == "1.2":
        validate_coverage(text, ledger_text, errors, repo_root=repo_root)
        completed_steps = {
            step
            for step, state in extract_ledger_steps(ledger_text).items()
            if state in DONE
        }
    elif schema == "2.0":
        completed_steps = validate_handbook_20(
            text,
            ledger_text,
            errors,
            repo_root=repo_root,
        )
        validate_required_question_ids(
            text,
            qa_text,
            fm.get("required_question_ids", ""),
            errors,
        )
    else:
        completed_steps = validate_handbook_21(
            text,
            ledger_text,
            errors,
            repo_root=repo_root,
        )
        required_qids = set(
            re.findall(r"\bQ-\d+\b", fm.get("required_question_ids", ""))
        )
        errors.extend(
            validate_lookup_index(
                text,
                completed_steps=completed_steps,
                required_qids=required_qids,
            )
        )
        validate_required_question_ids(
            text,
            qa_text,
            fm.get("required_question_ids", ""),
            errors,
        )
        if norm(fm.get("handbook_mode")) != "layered-step-manual":
            errors.append(
                "schema 2.1 handbook_mode must be layered-step-manual"
            )
        if norm(fm.get("default_reading_profile")) not in READING_PROFILES:
            errors.append("schema 2.1 default_reading_profile is invalid")
    validate_questions(text, qa_text, errors)
    validate_stale_patterns(text, ledger_text, errors)
    if status == "complete":
        manifest = validate_finalization_bundle.evaluate_bundle(
            ledger_path,
            qa_path,
            publication=publication,
        )
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
    if publication and not preflight:
        if norm(fm.get("cold_start_status")) != "pass":
            errors.append("formal publication requires cold_start_status: pass")
        if cold_start_report is None:
            errors.append("formal publication requires --cold-start-report")
        elif not cold_start_report.is_file():
            errors.append(f"cold-start report not found: {cold_start_report}")
        else:
            errors.extend(
                cold_start_test.evaluate_report(
                    cold_start_report,
                    path,
                    required_steps=completed_steps,
                    handbook_schema=schema if schema == "2.1" else None,
                )
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--template", action="store_true")
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--qa", type=Path)
    parser.add_argument("--preflight", action="store_true", help="accept pending validation_status before final commit")
    parser.add_argument("--repo-root", type=Path, help="repository root for source path and symbol link checks")
    parser.add_argument(
        "--publication",
        action="store_true",
        help="require compact handbook schema 2.1 and a real cold-start report",
    )
    parser.add_argument("--cold-start-report", type=Path)
    args = parser.parse_args()
    errors = validate(
        args.document,
        allow_template=args.template,
        ledger_path=args.ledger,
        qa_path=args.qa,
        preflight=args.preflight,
        repo_root=args.repo_root,
        publication=args.publication,
        cold_start_report=args.cold_start_report,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Valid project study document: {args.document}")
    print("Validation pass: preflight" if args.preflight else "Validation pass: final")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
