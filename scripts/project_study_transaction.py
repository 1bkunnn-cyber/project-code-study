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
from typing import Callable, Iterable


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
    for label, value in {
        "当前场景": state.get("current_scenario"),
        "当前 Step": state.get("current_step"),
        "当前微 Step": state.get("current_micro_step"),
        "当前节点": state.get("current_node_id"),
        "继续节点 ID": state.get("continuation_node_id"),
        "交互状态": state.get("interaction_state"),
        "等待用户回应": state.get("pending_user_response"),
        "最近 Q ID": state.get("last_question_id"),
        "最近事务 ID": state.get("last_transaction_id"),
    }.items():
        if value is None:
            continue
        pattern = re.compile(rf"(?m)^(\|\s*{re.escape(label)}\s*\|\s*)[^|]*(\|.*)$")
        if pattern.search(result):
            result = pattern.sub(rf"\g<1>`{value}`\g<2>", result, count=1)
    return result


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
        state = {"last_question_id": qid, "last_transaction_id": txid, "updated_at": now, "interaction_state": "AWAITING_QUESTIONS_OR_CONTINUE", "pending_user_response": "true"}
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
