#!/usr/bin/env python3
"""Strict validator for the optional project-study protocol memory store."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


KINDS = {"feedback", "correction", "project", "reference"}
REQUIRED = {"memory_id", "name", "description", "kind", "source_transaction", "source_path", "created", "updated", "status"}
SOFT_LINES, HARD_LINES = 150, 200
SOFT_BYTES, HARD_BYTES = 20 * 1024, 25 * 1024


def frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}, ["missing or invalid memory frontmatter"]
    values: dict[str, str] = {}
    errors: list[str] = []
    for line in match.group(1).splitlines():
        item = re.fullmatch(r"([A-Za-z0-9_-]+):\s*(.*)", line)
        if not item:
            errors.append("frontmatter must use single-line key: value fields")
            continue
        key, value = item.groups()
        if key in values:
            errors.append(f"duplicate frontmatter key: {key}")
        values[key] = value.strip().strip('"').strip("'")
    return values, errors


def pointers(text: str) -> tuple[dict[str, str], list[str]]:
    result: dict[str, str] = {}
    errors: list[str] = []
    current = ""
    if not re.search(r"(?m)^# Memory Index\s*$", text):
        errors.append("missing '# Memory Index'")
    for line in text.splitlines():
        heading = re.fullmatch(r"##\s+(feedback|correction|project|reference)\s*", line.strip())
        if heading:
            current = heading.group(1)
        elif line.lstrip().startswith("-"):
            match = re.fullmatch(r"\s*-\s*\[([^\]]+)\]\(([^)]+)\)\s+—\s+(.+)\s*", line)
            if not match:
                errors.append("index list item is not a one-line pointer")
                continue
            hook, target, _ = match.groups()
            if not current:
                errors.append(f"pointer outside kind heading: {target}")
            if target in result:
                errors.append(f"duplicate pointer: {target}")
            if not hook.strip():
                errors.append(f"empty pointer hook: {target}")
            result[target] = current
    return result, errors


def validate_store(root: Path, *, allow_soft_over: bool = False) -> list[str]:
    errors: list[str] = []
    index = root / "MEMORY.md"
    if not root.is_dir():
        return [f"memory root not found: {root}"]
    if not index.is_file():
        return ["MEMORY.md is missing"]
    index_text = index.read_text(encoding="utf-8-sig")
    live, index_errors = pointers(index_text)
    errors.extend(index_errors)
    lines, byte_count = len(index_text.splitlines()), len(index_text.encode("utf-8"))
    if lines > HARD_LINES or byte_count > HARD_BYTES:
        errors.append(f"hard index cap exceeded: {lines} lines / {byte_count} bytes")
    elif not allow_soft_over and (lines > SOFT_LINES or byte_count > SOFT_BYTES):
        errors.append(f"soft index cap exceeded: {lines} lines / {byte_count} bytes")
    files = {path.name for path in root.glob("*.md") if path.name != "MEMORY.md"}
    memory_ids: set[str] = set()
    for target, kind in live.items():
        path = (root / target).resolve()
        if path.parent != root.resolve() or path.suffix != ".md":
            errors.append(f"invalid or escaping memory target: {target}")
            continue
        if not path.is_file():
            errors.append(f"missing memory target: {target}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        values, fm_errors = frontmatter(text)
        errors.extend(f"{target}: {item}" for item in fm_errors)
        for key in REQUIRED:
            if not values.get(key):
                errors.append(f"{target}: missing {key}")
        if values.get("name") != path.stem:
            errors.append(f"{target}: name does not match filename")
        if values.get("kind") != kind or values.get("kind") not in KINDS:
            errors.append(f"{target}: invalid or mismatched kind")
        if values.get("status") != "active":
            errors.append(f"{target}: indexed memory must be active")
        if not re.fullmatch(r"MEM-\d+", values.get("memory_id", "")):
            errors.append(f"{target}: invalid memory_id")
        if values.get("memory_id") in memory_ids:
            errors.append(f"duplicate memory_id: {values.get('memory_id')}")
        memory_ids.add(values.get("memory_id", ""))
        if not re.fullmatch(r"TX-\d+", values.get("source_transaction", "")):
            errors.append(f"{target}: source_transaction must be a TX ID")
        body = text.split("---", 2)[-1]
        if kind in {"feedback", "project"}:
            if not re.search(r"(?im)^\s*(?:\*\*)?Why:\s*\S+", body):
                errors.append(f"{target}: missing Why:")
            if not re.search(r"(?im)^\s*(?:\*\*)?How to apply:\s*\S+", body):
                errors.append(f"{target}: missing How to apply:")
        if kind == "correction":
            for label in ("Original:", "Canonical:", "Stale patterns:", "Impact:"):
                if not re.search(rf"(?im)^\s*{re.escape(label)}\s*\S+", body):
                    errors.append(f"{target}: correction missing {label}")
    errors.extend(f"orphan memory file: {name}" for name in sorted(files - set(live)))
    errors.extend(f"indexed file not found: {name}" for name in sorted(set(live) - files))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("memory_root", type=Path)
    parser.add_argument("--allow-soft-over", action="store_true")
    args = parser.parse_args()
    errors = validate_store(args.memory_root, allow_soft_over=args.allow_soft_over)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    text = (args.memory_root / "MEMORY.md").read_text(encoding="utf-8-sig")
    print(f"Valid protocol memory: {args.memory_root}")
    print(f"Index size: {len(text.splitlines())} lines / {len(text.encode('utf-8'))} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
