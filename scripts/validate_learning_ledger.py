#!/usr/bin/env python3
"""Validate project-code-study ledgers and Q&A records.

Schema-only validation preserves compatibility with ledger 3.1/4.0 and Q&A
1.0. ``--strict`` enables schema 4.1/1.1 semantic and cross-file gates.
"""

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
LOG_H2 = [
    "阅读导航", "状态规范", "1. 当前状态与主线锚点", "2. 学习契约",
    "3. 动态学习路线", "4. Step 知识卡与掌握度", "5. 证据索引",
    "6. 开放事项", "7. 误区、纠正与规范表述", "8. 问题索引",
    "9. 实验、命令与失败尝试", "10. 来源冲突、相关方法与组合延伸",
    "11. 复习队列", "12. 维护状态", "13. 里程碑总结", "14. 会话日志",
    "15. 用户心得摘要", "16. 用户反馈摘要",
]
QA_H2 = [
    "1. 问题索引", "2. 详细问答", "3. 用户心得与学习感受",
    "4. 用户反馈", "5. 维护与归档",
]

COMMON_METADATA = [
    "document_type", "schema_version", "project_name", "project_path",
    "created_at", "updated_at", "write_authorized",
]
LOG_40_METADATA = COMMON_METADATA + [
    "qa_path", "current_step", "current_micro_step", "current_scenario",
    "current_node", "study_mode",
]
LOG_41_METADATA = COMMON_METADATA + [
    "language", "qa_path", "current_step", "current_micro_step", "current_scenario",
    "current_node_id", "continuation_node_id", "interaction_state",
    "pending_user_response", "active_side_question_ids", "last_question_id",
    "last_transaction_id", "learner_closed_question_phase",
    "learner_consented_to_generation", "study_mode",
]
QA_10_METADATA = COMMON_METADATA + ["ledger_path"]
QA_11_METADATA = COMMON_METADATA + ["language", "ledger_path", "last_question_id", "last_transaction_id"]

LOG_40_HEADERS = [
    {"Step", "主题", "状态", "完成标准", "当前行为证据", "下一决策"},
    {"Scenario ID", "场景", "入口 / 命令", "目标输出", "静态或运行验证", "状态"},
    {"顺序", "场景", "微 Step", "Node ID", "调用者", "当前类 / 函数", "状态"},
    {"Step", "Node ID", "核心结论", "证据 ID", "状态"},
    {"Q ID", "Step / Node", "问题摘要", "Parent Q", "状态", "下一动作"},
]
LOG_41_HEADERS = [
    {"Step", "主题", "Required", "状态", "K ID", "Transaction ID"},
    {"Scenario ID", "场景", "Required", "状态"},
    {"顺序", "场景", "微 Step", "Node ID", "状态", "Reason", "Impact", "Revisit condition", "Learner acceptance"},
    {"K ID", "Step", "Node ID", "掌握行为证据", "Transaction ID", "状态"},
    {"Q ID", "Step / Node", "问题摘要", "Parent Q", "状态", "下一动作"},
    {"Transaction ID", "时间", "QA delta", "LOG delta", "精确回读", "Strict validation", "Receipt"},
]
QA_10_HEADERS = [
    {"Q ID", "日期", "Step / Node", "类型", "问题摘要", "Parent Q", "状态", "回答位置", "修正 ID"},
]
QA_11_HEADERS = [
    {"Q ID", "日期", "Step / Node", "类型", "问题摘要", "Parent Q", "状态", "回答位置", "修正 ID", "Transaction ID"},
]

STEP_STATES = {"planned", "active", "blocked-prerequisite", "review", "done", "skipped", "stale"}
NODE_STATES = {"discovered", "planned", "active", "traced", "verified", "blocked-prerequisite", "deferred", "skipped", "stale"}
QUESTION_STATES = {"open", "answered", "retest-due", "closed", "deferred", "stale"}
INTERACTION_STATES = {
    "TEACHING_CURRENT_NODE", "AWAITING_RECALL", "ANSWERING_RECALL",
    "ANSWERING_SIDE_QUESTION", "AWAITING_QUESTIONS_OR_CONTINUE",
    "FINAL_QUESTION_PHASE", "FINAL_AUDIT", "DOCUMENT_CONSENT", "READY_TO_GENERATE",
}
FINAL_STEP_STATES = {"done", "skipped", "stale"}
EMPTY = {"", "-", "—", "none", "n/a", "na", "无", "待确认", "待生成", "待学习"}
HIDDEN_CHAT_PATTERNS = ["详见 chat", "详见chat", "同上", "前文已解释", "见之前回答", "详见对应 UNIT"]
Q_DETAIL_LABELS = [
    "主线继续位置", "用户问题原意", "完整参考答案", "项目 / 论文 / 背景证据",
    "是否改变旧结论", "关联 M-/C-/SRC- ID", "最小验证动作", "回到主线",
    "状态", "Transaction ID", "Persistence receipt",
]
K_DETAIL_LABELS = [
    "Transaction ID", "Prerequisites", "Learning objective", "Runtime position",
    "Complete explanation", "Source locations", "Inputs / outputs / Shapes / states",
    "Rationale / alternatives / trade-offs", "Important Q IDs",
    "Canonical M/C IDs and wording", "Evidence status and remaining boundary",
    "Self-check", "Complete reference answer", "Next connection", "Mastery behavior evidence",
]


def clean(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value.strip().strip("`").strip('"').strip("'"))


def norm(value: str | None) -> str:
    return clean(value).lower()


def is_empty(value: str | None) -> bool:
    return norm(value) in EMPTY or bool(re.fullmatch(r"\{\{[A-Z0-9_]+\}\}", clean(value)))


def frontmatter_of(text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}, ["missing or invalid YAML frontmatter"]
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        item = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if item:
            values[item.group(1)] = clean(item.group(2))
    return values, errors


def split_row(line: str) -> list[str]:
    return [clean(cell) for cell in line.strip().strip("|").split("|")]


def separator(line: str) -> bool:
    cells = split_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def tables_of(text: str) -> list[tuple[list[str], list[dict[str, str]]]]:
    lines = text.splitlines()
    tables: list[tuple[list[str], list[dict[str, str]]]] = []
    i = 0
    while i + 1 < len(lines):
        if lines[i].lstrip().startswith("|") and separator(lines[i + 1]):
            headers = split_row(lines[i])
            rows: list[dict[str, str]] = []
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = split_row(lines[i])
                if len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))
                i += 1
            tables.append((headers, rows))
            continue
        i += 1
    return tables


def find_table(tables: list[tuple[list[str], list[dict[str, str]]]], headers: set[str]) -> list[dict[str, str]] | None:
    for actual, rows in tables:
        if headers.issubset(set(actual)):
            return rows
    return None


def validate_headings(text: str, expected: list[str], errors: list[str]) -> None:
    headings = re.findall(r"^## (.+?)\s*$", text, re.MULTILINE)
    if headings != expected:
        errors.append("H2 headings or their order differ from the canonical schema")


def validate_headers(tables: list[tuple[list[str], list[dict[str, str]]]], expected: list[set[str]], errors: list[str]) -> None:
    for header_set in expected:
        if find_table(tables, header_set) is None:
            errors.append("missing or changed table with headers: " + ", ".join(sorted(header_set)))


def ids_in(rows: list[dict[str, str]] | None, key: str, prefix: str) -> list[str]:
    if not rows:
        return []
    return [clean(row.get(key)) for row in rows if re.fullmatch(rf"{prefix}-\d+", clean(row.get(key)), re.I)]


def numeric_max(ids: list[str]) -> str:
    if not ids:
        return "none"
    return max(ids, key=lambda item: int(item.split("-")[1])).upper()


def detail_blocks(text: str, prefix: str) -> dict[str, str]:
    matches = list(re.finditer(rf"(?m)^###\s+({prefix}-\d+)\b.*$", text, re.I))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[match.group(1).upper()] = text[match.start():end]
    return result


def label_value(block: str, label: str) -> str | None:
    match = re.search(rf"(?m)^-\s*{re.escape(label)}[：:]\s*(.+)$", block)
    return clean(match.group(1)) if match else None


def validate_log_strict(text: str, fm: dict[str, str], tables: list[tuple[list[str], list[dict[str, str]]]], errors: list[str]) -> None:
    hot_rows = find_table(tables, {"字段", "当前值"}) or []
    hot = {clean(row.get("字段")): clean(row.get("当前值")) for row in hot_rows}
    mapping = {
        "current_scenario": "当前场景", "current_node_id": "当前节点",
        "continuation_node_id": "继续节点 ID", "interaction_state": "交互状态",
        "pending_user_response": "等待用户回应", "active_side_question_ids": "当前支线问题",
        "last_question_id": "最近 Q ID", "last_transaction_id": "最近事务 ID",
        "updated_at": "更新时间",
    }
    step_value = clean(hot.get("当前 Step / 微 Step"))
    if step_value:
        parts = [clean(part) for part in step_value.split("/")]
        if len(parts) == 2:
            if parts[0] != clean(fm.get("current_step")):
                errors.append("frontmatter current_step differs from hot state")
            if parts[1] != clean(fm.get("current_micro_step")):
                errors.append("frontmatter current_micro_step differs from hot state")
    for key, label in mapping.items():
        if label not in hot:
            errors.append(f"hot state missing authoritative field: {label}")
        elif norm(fm.get(key)) != norm(hot[label]):
            errors.append(f"frontmatter {key} differs from hot state {label}")

    if clean(fm.get("interaction_state")) not in INTERACTION_STATES:
        errors.append(f"invalid interaction_state: {fm.get('interaction_state')!r}")
    if norm(fm.get("pending_user_response")) not in {"true", "false"}:
        errors.append("pending_user_response must be true or false")

    route = find_table(tables, {"Step", "Required", "状态", "K ID", "Transaction ID"}) or []
    active = [row for row in route if norm(row.get("状态")) in {"active", "review", "blocked-prerequisite"}]
    if len(active) > 1:
        errors.append(f"route has more than one active/review/blocked Step: {len(active)}")
    k_index = find_table(tables, {"K ID", "Step", "Node ID", "掌握行为证据", "Transaction ID", "状态"}) or []
    k_by_id = {clean(row.get("K ID")).upper(): row for row in k_index}
    k_blocks = detail_blocks(text, "K")
    k_headings = [item.upper() for item in re.findall(r"(?m)^###\s+(K-\d+)\b", text, re.I)]
    if len(k_headings) != len(set(k_headings)):
        errors.append("duplicate durable knowledge card ID")
    for row in route:
        state = norm(row.get("状态"))
        if state not in STEP_STATES:
            errors.append(f"invalid Step state {row.get('状态')!r} for Step {row.get('Step')}")
            continue
        if state == "done":
            kid = clean(row.get("K ID")).upper()
            txid = clean(row.get("Transaction ID")).upper()
            if not re.fullmatch(r"K-\d+", kid):
                errors.append(f"done Step {row.get('Step')} has no K ID")
            if not re.fullmatch(r"TX-\d+", txid):
                errors.append(f"done Step {row.get('Step')} has no transaction ID")
            if kid not in k_by_id:
                errors.append(f"done Step {row.get('Step')} references missing knowledge index {kid}")
            if kid not in k_blocks:
                errors.append(f"done Step {row.get('Step')} references missing durable knowledge card {kid}")
            else:
                for label in K_DETAIL_LABELS:
                    value = label_value(k_blocks[kid], label)
                    if value is None or is_empty(value):
                        errors.append(f"{kid} missing or empty durable field: {label}")

    nodes = find_table(tables, {"顺序", "微 Step", "Node ID", "状态", "Reason", "Impact", "Revisit condition", "Learner acceptance"}) or []
    node_ids: set[str] = set()
    for row in nodes:
        node_id = clean(row.get("Node ID")).upper()
        if node_id in node_ids:
            errors.append(f"duplicate Node ID row: {node_id}")
        node_ids.add(node_id)
        state = norm(row.get("状态"))
        if state not in NODE_STATES:
            errors.append(f"invalid NODE state {row.get('状态')!r} for {node_id or 'unknown'}")
        if state in {"deferred", "skipped"}:
            for field_name in ("Reason", "Impact", "Revisit condition", "Learner acceptance"):
                if is_empty(row.get(field_name)):
                    errors.append(f"{node_id} {state} missing {field_name}")

    tx_rows = find_table(tables, {"Transaction ID", "时间", "QA delta", "LOG delta", "精确回读", "Strict validation", "Receipt"}) or []
    if not tx_rows:
        errors.append("missing transaction log row")
    else:
        last = tx_rows[-1]
        if clean(last.get("Transaction ID")).upper() != clean(fm.get("last_transaction_id")).upper():
            errors.append("last transaction row differs from frontmatter last_transaction_id")
        if clean(last.get("时间")) != clean(fm.get("updated_at")):
            errors.append("updated_at differs from last successful transaction time")
        if norm(last.get("Receipt")) != "saved":
            errors.append("last transaction receipt is not saved")


def validate_qa_strict(text: str, fm: dict[str, str], tables: list[tuple[list[str], list[dict[str, str]]]], errors: list[str]) -> None:
    for pattern in HIDDEN_CHAT_PATTERNS:
        if pattern.lower() in text.lower():
            errors.append(f"Q&A contains forbidden hidden-context dependency: {pattern}")
    rows = find_table(tables, {"Q ID", "状态", "Parent Q", "Transaction ID"}) or []
    ids = ids_in(rows, "Q ID", "Q")
    if len(ids) != len(set(item.upper() for item in ids)):
        errors.append("duplicate Q ID in Q&A index")
    blocks = detail_blocks(text, "Q")
    detail_headings = [item.upper() for item in re.findall(r"(?m)^###\s+(Q-\d+)\b", text, re.I)]
    if len(detail_headings) != len(set(detail_headings)):
        errors.append("duplicate Q ID in Q&A detail blocks")
    for qid in ids:
        qid = qid.upper()
        if qid not in blocks:
            errors.append(f"Q&A index has no detail block for {qid}")
            continue
        for label in Q_DETAIL_LABELS:
            value = label_value(blocks[qid], label)
            if value is None or is_empty(value):
                errors.append(f"{qid} missing or empty standalone field: {label}")
        answer = label_value(blocks[qid], "完整参考答案") or ""
        if len(answer) < 20:
            errors.append(f"{qid} complete reference answer is too thin")
    detail_ids = set(blocks)
    if detail_ids != {item.upper() for item in ids}:
        errors.append("Q&A detail IDs and index IDs differ")
    for row in rows:
        state = norm(row.get("状态"))
        if state not in QUESTION_STATES:
            errors.append(f"invalid Q state {row.get('状态')!r} for {row.get('Q ID')}")
    expected_last = numeric_max(ids)
    if clean(fm.get("last_question_id")).upper() != expected_last.upper():
        errors.append(f"frontmatter last_question_id must be {expected_last}")


def q_index_ids(tables: list[tuple[list[str], list[dict[str, str]]]]) -> set[str]:
    rows = find_table(tables, {"Q ID", "状态", "Parent Q"}) or []
    return {item.upper() for item in ids_in(rows, "Q ID", "Q")}


def validate_cross(log_text: str, log_fm: dict[str, str], qa_text: str, qa_fm: dict[str, str], errors: list[str]) -> None:
    log_tables, qa_tables = tables_of(log_text), tables_of(qa_text)
    log_ids, qa_ids = q_index_ids(log_tables), q_index_ids(qa_tables)
    if log_ids != qa_ids:
        errors.append(f"LOG/QA Q-ID indexes differ: log={sorted(log_ids)}, qa={sorted(qa_ids)}")
    max_id = numeric_max(sorted(qa_ids))
    for label, value in (("LOG", log_fm.get("last_question_id")), ("QA", qa_fm.get("last_question_id"))):
        if clean(value).upper() != max_id.upper():
            errors.append(f"{label} last_question_id must be {max_id}")
    if clean(log_fm.get("last_transaction_id")).upper() != clean(qa_fm.get("last_transaction_id")).upper():
        errors.append("LOG/QA last_transaction_id values differ")
    if clean(log_fm.get("updated_at")) != clean(qa_fm.get("updated_at")):
        errors.append("LOG/QA updated_at values differ")


def validate_text(text: str, *, allow_template: bool = False, strict: bool = False) -> tuple[list[str], dict[str, str], str]:
    fm, errors = frontmatter_of(text)
    document_type = fm.get("document_type", "")
    schema = fm.get("schema_version", "")
    tables = tables_of(text)
    if document_type == "project-code-study-ledger" and schema == "4.1":
        required, headings, headers, label = LOG_41_METADATA, LOG_H2, LOG_41_HEADERS, "learning ledger schema 4.1"
    elif document_type == "project-code-study-ledger" and schema == "4.0":
        required, headings, headers, label = LOG_40_METADATA, LOG_H2, LOG_40_HEADERS, "learning ledger schema 4.0"
    elif document_type == "project-code-study-ledger" and schema == "3.1":
        required, headings, headers, label = ["document_type", "schema_version", "project_name", "project_path", "created_at", "updated_at", "current_step", "study_mode", "write_authorized"], LEGACY_H2, [], "legacy learning ledger schema 3.1"
    elif document_type == "project-code-study-qa" and schema == "1.1":
        required, headings, headers, label = QA_11_METADATA, QA_H2, QA_11_HEADERS, "Q&A record schema 1.1"
    elif document_type == "project-code-study-qa" and schema == "1.0":
        required, headings, headers, label = QA_10_METADATA, QA_H2, QA_10_HEADERS, "Q&A record schema 1.0"
    else:
        return errors + [f"unsupported document_type/schema_version: {document_type!r}/{schema!r}"], fm, "unknown record"
    for key in required:
        if key not in fm:
            errors.append(f"missing metadata key: {key}")
    if schema in {"4.1", "1.1"} and clean(fm.get("language")).lower() != "zh-cn":
        errors.append("current generated learning artifacts require language: zh-CN")
    validate_headings(text, headings, errors)
    validate_headers(tables, headers, errors)
    if not allow_template:
        placeholders = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text)))
        if placeholders:
            errors.append("uninitialized placeholders: " + ", ".join(placeholders))
    if strict and not allow_template:
        if document_type == "project-code-study-ledger" and schema != "4.1":
            errors.append("strict validation requires ledger schema 4.1")
        elif document_type == "project-code-study-qa" and schema != "1.1":
            errors.append("strict validation requires Q&A schema 1.1")
        elif document_type == "project-code-study-ledger":
            validate_log_strict(text, fm, tables, errors)
        else:
            validate_qa_strict(text, fm, tables, errors)
    return errors, fm, label


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--template", action="store_true", help="allow canonical placeholders")
    parser.add_argument("--strict", action="store_true", help="run semantic and cross-file checks")
    parser.add_argument("--qa", type=Path, help="companion PROJECT_STUDY_QA.md for a ledger")
    parser.add_argument("--ledger", type=Path, help="companion PROJECT_STUDY_LOG.md for a Q&A record")
    args = parser.parse_args()
    if not args.path.is_file():
        print(f"ERROR: file not found: {args.path}", file=sys.stderr)
        return 2
    text = args.path.read_text(encoding="utf-8-sig")
    errors, fm, label = validate_text(text, allow_template=args.template, strict=args.strict)
    peer = args.qa or args.ledger
    if args.strict and not args.template:
        if peer is None:
            errors.append("strict validation requires --qa for a ledger or --ledger for a Q&A record")
        elif not peer.is_file():
            errors.append(f"companion file not found: {peer}")
        else:
            peer_text = peer.read_text(encoding="utf-8-sig")
            peer_errors, peer_fm, _ = validate_text(peer_text, strict=True)
            errors.extend(f"companion: {error}" for error in peer_errors)
            if fm.get("document_type") == "project-code-study-ledger":
                validate_cross(text, fm, peer_text, peer_fm, errors)
            else:
                validate_cross(peer_text, peer_fm, text, fm, errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Valid {label}: {args.path}")
    if args.strict:
        print("Strict semantic and cross-file validation: pass")
    if fm.get("schema_version") in {"3.1", "4.0", "1.0"}:
        print("NOTE: compatibility schema accepted; migrate only with authorization")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
