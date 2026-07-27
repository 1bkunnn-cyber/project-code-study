#!/usr/bin/env python3
"""Reject positive persistence/readiness claims without matching receipts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PERSISTENCE_PATTERNS = [r"(?i)(?:已|已经|成功)?保存(?:成功|完成|好了)", r"(?i)\bsaved\b", r"(?i)(?:已|已经|成功)?校验(?:通过|完成)", r"(?i)\bvalidated\b"]
FINAL_PATTERNS = [r"(?i)(?:正式)?文档(?:已|已经)?(?:生成|完成)", r"(?i)readiness_status\s*:\s*ready"]
NEGATED_LINE = re.compile(r"(?i)(?:不能|不得|不要|未|尚未|without|not|unsaved).{0,20}(?:保存|saved|校验|validated|生成|ready)")


def validate(text: str, receipt: Path | None) -> list[str]:
    persistence_claim = any(re.search(pattern, text) for pattern in PERSISTENCE_PATTERNS)
    final_claim = any(re.search(pattern, text) for pattern in FINAL_PATTERNS)
    if not persistence_claim and not final_claim:
        return []
    if not final_claim and not persistence_claim:
        return []
    if all(NEGATED_LINE.search(line) for line in text.splitlines() if line.strip()):
        return []
    if receipt is None or not receipt.is_file():
        return ["positive persistence/readiness claim has no machine receipt"]
    try:
        payload = json.loads(receipt.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ["machine receipt is unreadable"]
    persistence_ok = persistence_claim and payload.get("persistence_status") == "saved" and payload.get("validator") == "pass"
    memory_ok = persistence_claim and payload.get("memory_status") == "saved" and payload.get("validator") == "pass"
    final_ok = payload.get("finalizer_status") == "validated" or payload.get("readiness_status") == "ready"
    if (final_claim and not final_ok) or (persistence_claim and not (persistence_ok or memory_ok or final_ok)):
        return ["machine receipt does not prove the claim"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text_file", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    errors = validate(args.text_file.read_text(encoding="utf-8"), args.receipt)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Response claim guard: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
