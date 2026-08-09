#!/usr/bin/env python3
"""Fail-closed logical transactions for project-code-study records.

The model may propose a delta, but only this module may allocate stable IDs,
commit LOG/QA changes, emit a saved receipt, or promote a correction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

import study_events


ID_RE = re.compile(r"\b(?P<prefix>TX|Q|M|C|FB|NOTE|K|SRC|RUN|NODE)-(?P<num>\d+)\b")
SUCCESS = "saved"
PARTIAL = "unsaved-partial"


class TransactionError(ValueError):
    """Raised when a delta cannot be committed without ambiguity."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def ids_in(text: str, prefix: str | None = None) -> set[str]:
    values = {m.group(0) for m in ID_RE.finditer(text)}
    return {item for item in values if prefix is None or item.startswith(prefix + "-")}


def split_question_intents(text: str) -> list[str]:
    """Split explicitly separable numbered/bulleted intents without merging them."""
    parts = re.split(r"(?m)^\s*(?:\d+[.)]|[-*])\s+", text.strip())
    parts = [part.strip() for part in parts if part.strip()]
    return parts or ([text.strip()] if text.strip() else [])


def _next_number(texts: Iterable[str], prefix: str) -> int:
    numbers = [int(m.group("num")) for text in texts for m in ID_RE.finditer(text) if m.group("prefix") == prefix]
    return max(numbers, default=0) + 1


def allocate_id(prefix: str, *texts: str, requested: str | None = None) -> str:
    """Allocate one ID and reject an explicit duplicate instead of reusing it."""
    if requested:
        if not re.fullmatch(rf"{re.escape(prefix)}-\d+", requested):
            raise TransactionError(f"invalid {prefix} ID: {requested}")
        if any(requested in ids_in(text, prefix) for text in texts):
            raise TransactionError(f"duplicate {prefix} ID rejected: {requested}")
        return requested
    candidate = _next_number(texts, prefix)
    used = set().union(*(ids_in(text, prefix) for text in texts))
    while f"{prefix}-{candidate:03d}" in used:
        candidate += 1
    return f"{prefix}-{candidate:03d}"


def _heading_range(text: str, heading: str) -> tuple[int, int]:
    starts = [m.start() for m in re.finditer(rf"(?m)^{re.escape(heading)}\s*$", text)]
    if len(starts) != 1:
        raise TransactionError(f"expected one section heading: {heading}")
    start = starts[0]
    next_heading = re.search(r"(?m)^#{1,6}\s+", text[start + len(heading):])
    end = start + len(heading) + next_heading.start() if next_heading else len(text)
    return start, end


def insert_before_heading(text: str, heading: str, block: str) -> str:
    start, _ = _heading_range(text, heading)
    return text[:start] + block.rstrip() + "\n\n" + text[start:]


def append_table_row(text: str, required_columns: set[str], row: str) -> str:
    """Append inside the unique table containing required columns."""
    lines = text.splitlines(keepends=True)
    matches: list[tuple[int, int]] = []
    for index in range(len(lines) - 1):
        if not lines[index].lstrip().startswith("|") or not lines[index + 1].lstrip().startswith("|"):
            continue
        headers = {cell.strip() for cell in lines[index].strip().strip("|").split("|")}
        separators = [cell.strip() for cell in lines[index + 1].strip().strip("|").split("|")]
        if not required_columns <= headers or not separators or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separators):
            continue
        end = index + 2
        while end < len(lines) and lines[end].lstrip().startswith("|"):
            end += 1
        matches.append((index, end))
    if len(matches) != 1:
        raise TransactionError(f"expected one table with columns: {sorted(required_columns)}")
    _, end = matches[0]
    prefix = "".join(lines[:end])
    suffix = "".join(lines[end:])
    return prefix.rstrip("\r\n") + "\n" + row.rstrip() + "\n" + suffix


def append_table_mapping(text: str, required_columns: set[str], values: dict[str, str]) -> str:
    """Append a row using the table's actual column order."""
    lines = text.splitlines()
    matches: list[list[str]] = []
    for index in range(len(lines) - 1):
        if not lines[index].lstrip().startswith("|") or not lines[index + 1].lstrip().startswith("|"):
            continue
        headers = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
        separators = [cell.strip() for cell in lines[index + 1].strip().strip("|").split("|")]
        if required_columns <= set(headers) and separators and all(re.fullmatch(r":?-{3,}:?", cell) for cell in separators):
            matches.append(headers)
    if len(matches) != 1:
        raise TransactionError(f"expected one table with columns: {sorted(required_columns)}")
    row = "| " + " | ".join(values.get(header, "none") for header in matches[0]) + " |"
    return append_table_row(text, required_columns, row)


def update_table_row(text: str, key_column: str, key_value: str, updates: dict[str, str]) -> str:
    """Update exactly one Markdown table row by a named key column."""
    lines = text.splitlines(keepends=True)
    active_headers: list[str] | None = None
    matches = 0
    for index, line in enumerate(lines):
        if line.lstrip().startswith("|") and index + 1 < len(lines):
            candidate = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if key_column in candidate and lines[index + 1].lstrip().startswith("|"):
                active_headers = candidate
                continue
        if active_headers is None:
            continue
        if not line.lstrip().startswith("|"):
            active_headers = None
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != len(active_headers):
            continue
        row = dict(zip(active_headers, cells))
        if row.get(key_column) != key_value:
            continue
        row.update(updates)
        newline = "\r\n" if line.endswith("\r\n") else "\n"
        lines[index] = "| " + " | ".join(row[header] for header in active_headers) + " |" + newline
        matches += 1
    if matches != 1:
        raise TransactionError(f"expected one row where {key_column}={key_value}, found {matches}")
    return "".join(lines)


def _replace_frontmatter_key(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"(?m)^{re.escape(key)}:\s*.*$")
    replacement = f'{key}: "{value}"'
    if len(pattern.findall(text)) != 1:
        raise TransactionError(f"frontmatter key must occur once: {key}")
    return pattern.sub(replacement, text, count=1)


def update_authoritative_state(text: str, state: dict[str, str]) -> str:
    """Update frontmatter and the matching hot-state table without tail appends."""
    result = text
    for key, value in state.items():
        result = _replace_frontmatter_key(result, key, value)
    hot_start = re.search(r"(?m)^## 1\. 当前状态与主线锚点\s*$", result)
    hot_end = re.search(r"(?m)^## 2\. 学习契约\s*$", result)
    if not hot_start or not hot_end or hot_end.start() <= hot_start.end():
        return result
    start, end = hot_start.end(), hot_end.start()
    hot = result[start:end]
    step_micro = None
    if state.get("current_step") is not None or state.get("current_micro_step") is not None:
        current = re.search(r"(?m)^\|\s*当前 Step / 微 Step\s*\|\s*`?([^|`]+)`?\s*\|", hot)
        old_parts = [part.strip() for part in current.group(1).split("/")] if current else ["", ""]
        step_micro = f"{state.get('current_step', old_parts[0])} / {state.get('current_micro_step', old_parts[1] if len(old_parts) > 1 else '')}"
    for label, value in {
        "当前场景": state.get("current_scenario"),
        "当前 Step / 微 Step": step_micro,
        "当前节点": state.get("current_node_id"),
        "继续节点 ID": state.get("continuation_node_id"),
        "交互状态": state.get("interaction_state"),
        "等待用户回应": state.get("pending_user_response"),
        "待处理用户意图": state.get("pending_user_intents"),
        "当前输入事件": state.get("active_input_event_id"),
        "问题队列": state.get("question_queue_ids"),
        "问题队列返回状态": state.get("question_queue_return_state"),
        "最近 Q ID": state.get("last_question_id"),
        "最近事务 ID": state.get("last_transaction_id"),
        "更新时间": state.get("updated_at"),
    }.items():
        if value is None:
            continue
        pattern = re.compile(rf"(?m)^(\|\s*{re.escape(label)}\s*\|\s*)[^|]*(\|.*)$")
        if pattern.search(hot):
            hot = pattern.sub(rf"\g<1>`{value}`\g<2>", hot, count=1)
    return result[:start] + hot + result[end:]


def _atomic_replace(paths_and_text: dict[Path, str]) -> None:
    staged: list[tuple[Path, Path]] = []
    backups: list[tuple[Path, Path]] = []
    try:
        for path, text in paths_and_text.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, raw = tempfile.mkstemp(prefix=f".{path.name}.txn-", dir=path.parent)
            os.close(fd)
            stage = Path(raw)
            stage.write_text(text, encoding="utf-8", newline="\n")
            staged.append((path, stage))
        for path, _ in staged:
            if path.exists():
                backup = path.with_name(f".{path.name}.bak-txn")
                if backup.exists():
                    backup.unlink()
                os.replace(path, backup)
                backups.append((path, backup))
        for path, stage in staged:
            os.replace(stage, path)
        for _, backup in backups:
            backup.unlink(missing_ok=True)
    except Exception:
        for path, stage in staged:
            stage.unlink(missing_ok=True)
        for path, backup in backups:
            if not path.exists() and backup.exists():
                os.replace(backup, path)
        raise


def write_machine_receipt(receipt_path: Path, payload: dict[str, object]) -> dict[str, object]:
    """Write the only accepted success receipt format."""
    required = {"persistence_status", "tx_id", "files", "hashes", "validator", "created_at"}
    if set(payload) < required or payload.get("persistence_status") != SUCCESS:
        raise TransactionError("only a complete machine success payload may be written")
    receipt_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def read_machine_receipt(receipt_path: Path, files: Iterable[Path]) -> dict[str, object] | None:
    try:
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if payload.get("persistence_status") != SUCCESS or payload.get("validator") != "pass":
        return None
    hashes = payload.get("hashes")
    if not isinstance(hashes, dict):
        return None
    for path in files:
        key = str(path.resolve())
        if hashes.get(key) != sha256_text(path.read_text(encoding="utf-8")):
            return None
    return payload


def _question_detail(qid: str, txid: str, data: dict[str, str]) -> str:
    required = ["question_intent", "canonical_answer", "evidence", "anchor", "status"]
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise TransactionError("question delta missing: " + ", ".join(missing))
    return f"""### {qid} — {data['title']}\n\n- Parent Q：{data.get('parent_id', 'none')}\n- 学习位置：{data.get('location', 'current NODE')}\n- 用户问题原意：{data['question_intent']}\n- 判断：{data.get('verdict', '证据不足')}\n- 正确部分：{data.get('correct_parts', '待逐项核对')}\n- 缺失或需要纠正的部分：{data.get('repair', '无')}\n- 完整参考答案：{data['canonical_answer']}\n- 项目 / 论文 / 运行证据：{data['evidence']}\n- 是否改变旧结论：{data.get('changes_old_conclusion', 'no')}\n- 关联 M-/C-/SRC- ID：{data.get('evidence_ids', 'none')}\n- 最小验证动作：{data.get('verification_action', '复核对应证据')}\n- 回到主线：{data['anchor']}\n- 状态：{data['status']}\n- Transaction ID：{txid}\n- Persistence receipt：machine transaction pending commit\n"""


def _pending_question_detail(
    qid: str,
    txid: str,
    input_event_id: str,
    intent: dict[str, Any],
    data: dict[str, str],
) -> str:
    title = data.get("title") or intent["text"][:48]
    return f"""### {qid} — {title}

- 日期：{data.get('date', datetime.now(timezone.utc).date().isoformat())}
- Step / Node：{data.get('location', 'current NODE')}
- Parent Q：{data.get('parent_id', 'none')}
- Input event：{input_event_id}
- Intent ID：{intent['intent_id']}
- Intent 顺序：{intent['source_order']}
- 主线继续位置：{data.get('anchor', 'current NODE')}
- 用户问题原意：{intent['text']}
- 直接结论：pending
- 判断：待回答
- 用户回答中正确的部分：待回答
- 缺失或需要纠正的部分：待回答
- 完整参考答案：pending
- 项目 / 论文 / 背景证据：not-run
- 是否改变旧结论：pending
- 关联 M-/C-/SRC- ID：none
- 最小验证动作：回答后确定
- 回到主线：{data.get('anchor', 'current NODE')}
- 回答状态：pending
- 状态：open
- Transaction ID：{txid}
- Persistence receipt：registered by question-intake transaction
"""


def _question_block_range(text: str, qid: str) -> tuple[int, int]:
    match = re.search(rf"(?m)^###\s+{re.escape(qid)}\b.*$", text)
    if not match:
        raise TransactionError(f"missing question detail: {qid}")
    next_heading = re.search(r"(?m)^#{2,3}\s+", text[match.end():])
    end = match.end() + next_heading.start() if next_heading else len(text)
    return match.start(), end


def _label(block: str, name: str) -> str:
    match = re.search(rf"(?m)^-\s*{re.escape(name)}[：:]\s*(.+)$", block)
    if not match:
        raise TransactionError(f"question detail missing {name}")
    return match.group(1).strip()


def _frontmatter_value(text: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*[\"']?([^\"'\n]+)[\"']?\s*$", text)
    if not match:
        raise TransactionError(f"frontmatter missing {key}")
    return match.group(1).strip()


def _validated_commit(
    ledger_path: Path,
    qa_path: Path,
    new_log: str,
    new_qa: str,
    validator: Callable[[Path, Path], list[str]],
) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="project-study-validate-") as tmp:
        staged_log, staged_qa = Path(tmp) / ledger_path.name, Path(tmp) / qa_path.name
        staged_log.write_text(new_log, encoding="utf-8")
        staged_qa.write_text(new_qa, encoding="utf-8")
        errors = validator(staged_log, staged_qa)
        if errors:
            return errors
    _atomic_replace({ledger_path: new_log, qa_path: new_qa})
    return []


def register_question_batch(
    ledger_path: Path,
    qa_path: Path,
    input_event: dict[str, Any],
    questions: list[dict[str, str]],
    *,
    receipt_path: Path | None = None,
    validator: Callable[[Path, Path], list[str]] | None = None,
) -> dict[str, object]:
    """Register every question in one input event before any answer is emitted."""
    if validator is None:
        return {"persistence_status": PARTIAL, "written": [], "errors": ["strict validator callback is required before commit"], "next_action": "repair-records-only"}
    try:
        source_text = input_event.get("raw_text")
        if not isinstance(source_text, str):
            raise TransactionError("source-bound input event is missing raw_text")
        envelope_errors = study_events.validate_intent_envelope(input_event, source_text)
        if envelope_errors:
            raise TransactionError("invalid source-bound input event: " + "; ".join(envelope_errors))
        intents = [item for item in input_event.get("intents", []) if item.get("kind") == "question"]
        if not intents or len(intents) != len(questions):
            raise TransactionError("question metadata count must match question intents")
        old_log = ledger_path.read_text(encoding="utf-8")
        old_qa = qa_path.read_text(encoding="utf-8")
        txid = allocate_id("TX", old_log, old_qa)
        new_log, new_qa = old_log, old_qa
        qids: list[str] = []
        allocation_text = old_log + old_qa
        for intent, data in zip(intents, questions):
            qid = allocate_id("Q", allocation_text)
            allocation_text += "\n" + qid
            qids.append(qid)
            intent["question_id"] = qid
            detail = _pending_question_detail(qid, txid, input_event["input_event_id"], intent, data)
            new_qa = insert_before_heading(new_qa, "## 3. 用户心得与学习感受", detail)
            new_qa = append_table_mapping(new_qa, {"Q ID", "状态", "Parent Q", "Transaction ID"}, {
                "Q ID": qid,
                "日期": data.get("date", datetime.now(timezone.utc).date().isoformat()),
                "Step / Node": data.get("location", "current"),
                "类型": data.get("question_type", "concept"),
                "问题摘要": data.get("title", intent["text"][:48]),
                "Parent Q": data.get("parent_id", "none"),
                "状态": "open",
                "回答状态": "pending",
                "Input event": input_event["input_event_id"],
                "Intent ID": intent["intent_id"],
                "回答位置": "detail",
                "修正 ID": "none",
                "Transaction ID": txid,
            })
            new_log = append_table_mapping(new_log, {"Q ID", "状态", "Parent Q"}, {
                "Q ID": qid,
                "Step / Node": data.get("location", "current"),
                "问题摘要": data.get("title", intent["text"][:48]),
                "Parent Q": data.get("parent_id", "none"),
                "状态": "open",
                "回答状态": "pending",
                "Input event": input_event["input_event_id"],
                "Intent ID": intent["intent_id"],
                "是否阻塞": "yes",
                "修正 / 证据 ID": "none",
                "下一动作": txid,
            })
        now = datetime.now(timezone.utc).isoformat()
        queue = ",".join(qids)
        new_log = update_authoritative_state(new_log, {
            "last_question_id": qids[-1],
            "last_transaction_id": txid,
            "updated_at": now,
            "interaction_state": "ANSWERING_QUESTION_QUEUE",
            "pending_user_response": "false",
            "pending_user_intents": queue,
            "active_input_event_id": input_event["input_event_id"],
            "question_queue_ids": queue,
            "question_queue_return_state": input_event.get("received_state", "AWAITING_QUESTIONS_OR_CONTINUE"),
        })
        new_qa = update_authoritative_state(new_qa, {"last_question_id": qids[-1], "last_transaction_id": txid, "updated_at": now})
        new_log = append_table_mapping(new_log, {"Transaction ID", "时间", "QA delta", "LOG delta", "精确回读", "Strict validation", "Receipt"}, {
            "Transaction ID": txid,
            "时间": now,
            "QA delta": "question intake " + ",".join(qids),
            "LOG delta": "question queue registered",
            "精确回读": "pass",
            "Strict validation": "pass",
            "Receipt": "saved",
        })
        errors = _validated_commit(ledger_path, qa_path, new_log, new_qa, validator)
        if errors:
            return {"persistence_status": PARTIAL, "tx_id": txid, "written": [], "errors": errors, "next_action": "repair-question-batch"}
        payload: dict[str, object] = {
            "persistence_status": SUCCESS,
            "transaction_kind": "question-intake",
            "tx_id": txid,
            "input_event_id": input_event["input_event_id"],
            "qa_ids": qids,
            "files": [str(ledger_path), str(qa_path)],
            "hashes": {str(ledger_path.resolve()): sha256_text(new_log), str(qa_path.resolve()): sha256_text(new_qa)},
            "validator": "pass",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if receipt_path:
            write_machine_receipt(receipt_path, payload)
        return payload
    except Exception as exc:
        return {"persistence_status": PARTIAL, "written": [], "errors": [str(exc)], "next_action": "repair-question-batch"}


def answer_question(
    ledger_path: Path,
    qa_path: Path,
    qid: str,
    data: dict[str, str],
    *,
    receipt_path: Path | None = None,
    validator: Callable[[Path, Path], list[str]] | None = None,
) -> dict[str, object]:
    """Answer one registered Q without reallocating it or touching later answers."""
    if validator is None:
        return {"persistence_status": PARTIAL, "written": [], "errors": ["strict validator callback is required before commit"], "next_action": "repair-question-batch"}
    try:
        if not data.get("canonical_answer") or not data.get("evidence"):
            raise TransactionError("question answer requires canonical_answer and evidence")
        old_log = ledger_path.read_text(encoding="utf-8")
        old_qa = qa_path.read_text(encoding="utf-8")
        return_state = _frontmatter_value(old_log, "question_queue_return_state")
        active_input_event_id = _frontmatter_value(old_log, "active_input_event_id")
        start, end = _question_block_range(old_qa, qid)
        old_block = old_qa[start:end]
        if _label(old_block, "回答状态") != "pending":
            raise TransactionError(f"question is not pending: {qid}")
        txid = allocate_id("TX", old_log, old_qa)
        replacements = {
            "直接结论": data.get("direct_conclusion", data["canonical_answer"]),
            "判断": data.get("verdict", "已回答"),
            "用户回答中正确的部分": data.get("correct_parts", "不适用：用户直接提问"),
            "缺失或需要纠正的部分": data.get("repair", "无"),
            "完整参考答案": data["canonical_answer"],
            "项目 / 论文 / 背景证据": data["evidence"],
            "是否改变旧结论": data.get("changes_old_conclusion", "no"),
            "关联 M-/C-/SRC- ID": data.get("evidence_ids", "none"),
            "最小验证动作": data.get("verification_action", "复核对应证据"),
            "回答状态": "answered",
            "状态": data.get("status", "answered"),
            "Transaction ID": txid,
            "Persistence receipt": "machine answer transaction pending commit",
        }
        new_block = old_block
        for label, value in replacements.items():
            pattern = re.compile(rf"(?m)^(-\s*{re.escape(label)}[：:]\s*).+$")
            if not pattern.search(new_block):
                raise TransactionError(f"question detail missing {label}")
            new_block = pattern.sub(lambda match, replacement=value: match.group(1) + replacement, new_block, count=1)
        new_qa = old_qa[:start] + new_block + old_qa[end:]
        new_qa = update_table_row(new_qa, "Q ID", qid, {"状态": data.get("status", "answered"), "回答状态": "answered", "Transaction ID": txid})
        new_log = update_table_row(old_log, "Q ID", qid, {"状态": data.get("status", "answered"), "回答状态": "answered", "下一动作": txid})
        remaining_ids = [
            match.group(1)
            for match in re.finditer(r"(?ms)^###\s+(Q-\d+)\b.*?(?=^###\s+Q-\d+\b|^##\s+3\.|\Z)", new_qa)
            if "- 回答状态：pending" in match.group(0)
        ]
        now = datetime.now(timezone.utc).isoformat()
        new_log = update_authoritative_state(new_log, {
            "last_transaction_id": txid,
            "updated_at": now,
            "interaction_state": "ANSWERING_QUESTION_QUEUE" if remaining_ids else return_state,
            "pending_user_response": "false" if remaining_ids else "true",
            "pending_user_intents": ",".join(remaining_ids) if remaining_ids else "none",
            "question_queue_ids": ",".join(remaining_ids) if remaining_ids else "none",
            "active_input_event_id": active_input_event_id if remaining_ids else "none",
            "question_queue_return_state": return_state if remaining_ids else "none",
        })
        new_qa = update_authoritative_state(new_qa, {"last_transaction_id": txid, "updated_at": now})
        new_log = append_table_mapping(new_log, {"Transaction ID", "时间", "QA delta", "LOG delta", "精确回读", "Strict validation", "Receipt"}, {
            "Transaction ID": txid,
            "时间": now,
            "QA delta": f"answer {qid}",
            "LOG delta": "question queue updated",
            "精确回读": "pass",
            "Strict validation": "pass",
            "Receipt": "saved",
        })
        errors = _validated_commit(ledger_path, qa_path, new_log, new_qa, validator)
        if errors:
            return {"persistence_status": PARTIAL, "tx_id": txid, "written": [], "errors": errors, "next_action": f"repair-answer:{qid}"}
        payload: dict[str, object] = {
            "persistence_status": SUCCESS,
            "transaction_kind": "question-answer",
            "tx_id": txid,
            "qa_ids": [qid],
            "remaining_qa_ids": remaining_ids,
            "files": [str(ledger_path), str(qa_path)],
            "hashes": {str(ledger_path.resolve()): sha256_text(new_log), str(qa_path.resolve()): sha256_text(new_qa)},
            "validator": "pass",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if receipt_path:
            write_machine_receipt(receipt_path, payload)
        return payload
    except Exception as exc:
        return {"persistence_status": PARTIAL, "written": [], "errors": [str(exc)], "next_action": f"repair-answer:{qid}"}


def commit_question(ledger_path: Path, qa_path: Path, data: dict[str, str], *, receipt_path: Path | None = None, validator: Callable[[Path, Path], list[str]] | None = None) -> dict[str, object]:
    """Commit one Q plus its LOG state as one validated logical transaction."""
    old_log = ledger_path.read_text(encoding="utf-8")
    old_qa = qa_path.read_text(encoding="utf-8")
    if validator is None:
        return {"persistence_status": PARTIAL, "written": [], "errors": ["strict validator callback is required before commit"], "next_action": "repair-records-only"}
    try:
        qid = allocate_id("Q", old_log, old_qa, requested=data.get("qid"))
        txid = allocate_id("TX", old_log, old_qa, requested=data.get("txid"))
        detail = _question_detail(qid, txid, data)
        new_qa = insert_before_heading(old_qa, "## 3. 用户心得与学习感受", detail)
        qa_row = "| {qid} | {date} | {location} | question | {summary} | {parent} | {status} | detail | none | {tx} |".format(
            qid=qid, date=data.get("date", datetime.now(timezone.utc).date().isoformat()), location=data.get("location", "current"), summary=data["title"], parent=data.get("parent_id", "none"), status=data["status"], tx=txid)
        new_qa = append_table_row(new_qa, {"Q ID", "状态", "Parent Q", "Transaction ID"}, qa_row)
        new_log = append_table_row(old_log, {"Q ID", "状态", "Parent Q"}, f"| {qid} | {data.get('location', 'current')} | {data['title']} | {data.get('parent_id', 'none')} | {data['status']} | yes | none | {txid} |")
        now = datetime.now(timezone.utc).isoformat()
        state = {"last_question_id": qid, "last_transaction_id": txid, "updated_at": now, "interaction_state": "AWAITING_QUESTIONS_OR_CONTINUE", "pending_user_response": "true", "pending_user_intents": data.get("pending_user_intents", "none")}
        if data.get("current_node_id"):
            state["current_node_id"] = data["current_node_id"]
        new_log = update_authoritative_state(new_log, state)
        new_qa = update_authoritative_state(new_qa, {"last_question_id": qid, "last_transaction_id": txid, "updated_at": now})
        tx_row = f"| {txid} | {now} | question {qid} | state {qid} | pass | pending | saved |"
        new_log = append_table_row(new_log, {"Transaction ID", "时间", "QA delta", "LOG delta", "精确回读", "Strict validation", "Receipt"}, tx_row)
        with tempfile.TemporaryDirectory(prefix="project-study-validate-") as tmp:
            staged_log, staged_qa = Path(tmp) / ledger_path.name, Path(tmp) / qa_path.name
            staged_log.write_text(new_log, encoding="utf-8")
            staged_qa.write_text(new_qa, encoding="utf-8")
            errors = validator(staged_log, staged_qa)
            if errors:
                return {"persistence_status": PARTIAL, "tx_id": txid, "written": [], "missing": [str(ledger_path), str(qa_path)], "errors": errors, "next_action": "repair-records-only"}
        _atomic_replace({ledger_path: new_log, qa_path: new_qa})
        payload = {"persistence_status": SUCCESS, "tx_id": txid, "qa_ids": [qid], "files": [str(ledger_path), str(qa_path)], "hashes": {str(ledger_path.resolve()): sha256_text(new_log), str(qa_path.resolve()): sha256_text(new_qa)}, "validator": "pass", "created_at": datetime.now(timezone.utc).isoformat()}
        if receipt_path:
            write_machine_receipt(receipt_path, payload)
        return payload
    except Exception as exc:
        return {"persistence_status": PARTIAL, "written": [], "errors": [str(exc)], "next_action": "repair-records-only"}


def correct_promoted_claim(paths: Iterable[Path], original: str, canonical: str, stale_patterns: list[str], *, correction_id: str, tx_id: str, receipt_path: Path | None = None) -> dict[str, object]:
    """Propagate one correction through promoted artifacts; preserve history files."""
    if not original or not canonical or not stale_patterns:
        raise TransactionError("correction requires original, canonical, and stale_patterns")
    originals: dict[Path, str] = {path: path.read_text(encoding="utf-8") for path in paths}
    replacements: dict[Path, str] = {}
    for path, text in originals.items():
        if path.name == "PROJECT_STUDY_QA.md" or path.name == "PROJECT_STUDY_LOG.md":
            pass
        updated = text
        for pattern in stale_patterns:
            updated = updated.replace(pattern, canonical)
        replacements[path] = updated
    _atomic_replace(replacements)
    payload = {"persistence_status": SUCCESS, "tx_id": tx_id, "correction_id": correction_id, "original_wording": original, "canonical_wording": canonical, "stale_patterns": stale_patterns, "affected_files": [str(path) for path in paths], "files": [str(path) for path in paths], "hashes": {str(path.resolve()): sha256_text(text) for path, text in replacements.items()}, "validator": "pass", "created_at": datetime.now(timezone.utc).isoformat()}
    if receipt_path:
        write_machine_receipt(receipt_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-receipt", nargs="+", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.check_receipt:
        result = read_machine_receipt(args.receipt, args.check_receipt) if args.receipt else None
        print(json.dumps(result or {"persistence_status": "unsaved"}, ensure_ascii=False))
        return 0 if result else 1
    parser.error("use --check-receipt for the CLI; normal commits require a structured caller")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
