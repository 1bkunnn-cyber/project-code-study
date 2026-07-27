#!/usr/bin/env python3
"""Receipt-gated, staged memory promotion for project-code-study."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from validate_protocol_memory import HARD_BYTES, HARD_LINES, validate_store


class MemoryTransactionError(ValueError):
    pass


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_receipt(receipt: Path, files: list[Path]) -> dict[str, object]:
    try:
        payload = json.loads(receipt.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise MemoryTransactionError(f"invalid machine receipt: {exc}") from exc
    if payload.get("persistence_status") != "saved" or payload.get("validator") != "pass":
        raise MemoryTransactionError("source receipt is not a validated saved receipt")
    if not re.fullmatch(r"TX-\d+", str(payload.get("tx_id", ""))):
        raise MemoryTransactionError("source receipt has no TX ID")
    hashes = payload.get("hashes")
    if not isinstance(hashes, dict):
        raise MemoryTransactionError("source receipt has no file hashes")
    for path in files:
        if not path.is_file() or hashes.get(str(path.resolve())) != sha256_text(path.read_text(encoding="utf-8")):
            raise MemoryTransactionError(f"source receipt is stale for {path}")
    return payload


def parse_values(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8-sig")
    match = re.match(r"\A---\s*\n(.*?)\n---", text, re.DOTALL)
    result: dict[str, str] = {}
    if match:
        for line in match.group(1).splitlines():
            item = re.fullmatch(r"([A-Za-z0-9_-]+):\s*(.*)", line)
            if item:
                result[item.group(1)] = item.group(2).strip().strip('"').strip("'")
    return result


def next_id(root: Path) -> str:
    ids = []
    for path in root.glob("*.md"):
        if path.name != "MEMORY.md":
            match = re.search(r"(?m)^memory_id:\s*['\"]?(MEM-\d+)", path.read_text(encoding="utf-8-sig"))
            if match:
                ids.append(int(match.group(1).split("-")[1]))
    return f"MEM-{max(ids, default=0) + 1:03d}"


def atomic_replace(files: dict[Path, str]) -> None:
    stages: list[tuple[Path, Path]] = []
    backups: list[tuple[Path, Path]] = []
    try:
        for path, text in files.items():
            fd, raw = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
            os.close(fd)
            stage = Path(raw)
            stage.write_text(text, encoding="utf-8", newline="\n")
            stages.append((path, stage))
        for path, _ in stages:
            backup = path.with_name(path.name + ".memory-backup")
            backup.unlink(missing_ok=True)
            if path.exists():
                os.replace(path, backup)
                backups.append((path, backup))
        for path, stage in stages:
            os.replace(stage, path)
        for _, backup in backups:
            backup.unlink(missing_ok=True)
    except Exception:
        for _, stage in stages:
            stage.unlink(missing_ok=True)
        for path, backup in backups:
            if not path.exists() and backup.exists():
                os.replace(backup, path)
        raise


def init_store(root: Path, template: Path, *, user_consent: bool) -> None:
    if not user_consent:
        raise MemoryTransactionError(
            "explicit user consent is required before creating the project memory store"
        )
    if root.exists() and any(root.iterdir()):
        raise MemoryTransactionError("memory root exists and is not empty")
    root.mkdir(parents=True, exist_ok=True)
    (root / "archive").mkdir(exist_ok=True)
    shutil.copyfile(template, root / "MEMORY.md")
    errors = validate_store(root)
    if errors:
        raise MemoryTransactionError("template failed validation: " + "; ".join(errors))


def upsert(args: argparse.Namespace) -> dict[str, object]:
    receipt = read_receipt(args.receipt, args.source_files)
    if validate_store(args.memory_root):
        raise MemoryTransactionError("memory store is invalid; repair before syncing")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.name):
        raise MemoryTransactionError("memory name must be stable kebab-case")
    if args.kind not in {"feedback", "correction", "project", "reference"}:
        raise MemoryTransactionError("invalid memory kind")
    body = args.body_file.read_text(encoding="utf-8").strip()
    if not args.description.strip() or not body:
        raise MemoryTransactionError("description and body are required")
    if args.kind in {"feedback", "project"} and (not re.search(r"(?im)^\s*Why:\s*\S+", body) or not re.search(r"(?im)^\s*How to apply:\s*\S+", body)):
        raise MemoryTransactionError("feedback/project entries require Why: and How to apply:")
    if args.kind == "correction" and any(not re.search(rf"(?im)^\s*{label}\s*\S+", body) for label in ("Original:", "Canonical:", "Stale patterns:", "Impact:")):
        raise MemoryTransactionError("correction entries require Original, Canonical, Stale patterns, and Impact")
    root, index = args.memory_root, args.memory_root / "MEMORY.md"
    target = root / f"{args.name}.md"
    old_index = index.read_text(encoding="utf-8-sig")
    old = parse_values(target)
    now = datetime.now(timezone.utc).date().isoformat()
    values = {
        "memory_id": old.get("memory_id") or next_id(root), "name": args.name,
        "description": args.description.strip(), "kind": args.kind,
        "source_transaction": str(receipt["tx_id"]), "source_path": args.source_path,
        "created": old.get("created") or now, "updated": now, "status": "active",
    }
    entry = "---\n" + "\n".join(f'{key}: "{value}"' for key, value in values.items()) + "\n---\n\n" + body + "\n"
    if target.is_file():
        new_index = re.sub(rf"(?m)^\s*-\s*\[[^\]]+\]\({re.escape(args.name)}\.md\)\s+—\s+.*$", f"- [{args.description.strip()}]({args.name}.md) — {args.description.strip()}", old_index)
        action = "updated"
    else:
        heading = f"## {args.kind}"
        if len(re.findall(rf"(?m)^{re.escape(heading)}\s*$", old_index)) != 1:
            raise MemoryTransactionError(f"missing unique index heading: {heading}")
        new_index = old_index.replace(heading, heading + f"\n- [{args.description.strip()}]({args.name}.md) — {args.description.strip()}", 1)
        action = "added"
    if len(new_index.splitlines()) > HARD_LINES or len(new_index.encode("utf-8")) > HARD_BYTES:
        raise MemoryTransactionError("index hard cap would be exceeded; compact first")
    with tempfile.TemporaryDirectory(prefix="protocol-memory-stage-") as temp:
        staged = Path(temp) / "memory"
        shutil.copytree(root, staged)
        (staged / "MEMORY.md").write_text(new_index, encoding="utf-8")
        (staged / target.name).write_text(entry, encoding="utf-8")
        errors = validate_store(staged, allow_soft_over=True)
        if errors:
            raise MemoryTransactionError("staged validation failed: " + "; ".join(errors))
    atomic_replace({index: new_index, target: entry})
    result = {
        "memory_status": "saved", "action": action, "memory_id": values["memory_id"],
        "source_transaction": receipt["tx_id"], "files": [str(index), str(target)],
        "hashes": {str(index.resolve()): sha256_text(new_index), str(target.resolve()): sha256_text(entry)},
        "validator": "pass", "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if args.receipt_out:
        args.receipt_out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("memory_root", type=Path)
    init.add_argument("--template", type=Path, required=True)
    init.add_argument(
        "--user-consent",
        action="store_true",
        help="confirm that the learner explicitly approved creating the memory store",
    )
    up = sub.add_parser("upsert")
    up.add_argument("memory_root", type=Path)
    up.add_argument("--receipt", type=Path, required=True)
    up.add_argument("--source-files", type=Path, nargs="+", required=True)
    up.add_argument("--name", required=True)
    up.add_argument("--description", required=True)
    up.add_argument("--kind", required=True)
    up.add_argument("--source-path", required=True)
    up.add_argument("--body-file", type=Path, required=True)
    up.add_argument("--receipt-out", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "init":
            init_store(args.memory_root, args.template, user_consent=args.user_consent)
            result = {"memory_status": "initialized"}
        else:
            result = upsert(args)
    except (OSError, MemoryTransactionError) as exc:
        print(json.dumps({"memory_status": "unsaved-memory", "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
