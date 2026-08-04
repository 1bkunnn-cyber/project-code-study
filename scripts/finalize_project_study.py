#!/usr/bin/env python3
"""The only formal document finalization entry point.

It validates a fresh LOG/QA readiness manifest, assembles a candidate in a
same-directory temporary file, runs preflight and final validation, and only
then atomically replaces the formal target. A failed gate never touches it.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import validate_finalization_bundle
import validate_learning_ledger

DOC_VALIDATOR = Path(__file__).resolve().parents[1] / "skills" / "project-study-document" / "scripts" / "validate_study_document.py"


def _set_frontmatter(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"(?m)^{re.escape(key)}:\s*.*$")
    if len(pattern.findall(text)) != 1:
        raise ValueError(f"frontmatter key must occur once: {key}")
    return pattern.sub(f'{key}: "{value}"', text, count=1)


def _candidate_text(candidate: Path, *, status: str, readiness_status: str, validation_status: str) -> str:
    text = candidate.read_text(encoding="utf-8-sig")
    for key, value in (("status", status), ("readiness_status", readiness_status), ("validation_status", validation_status)):
        text = _set_frontmatter(text, key, value)
    generated = re.search(r"(?m)^generated_at:\s*[\"']?([^\"'\n]+)", text)
    if status == "complete" and (
        generated is None
        or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2})",
            generated.group(1).strip(),
        )
    ):
        text = _set_frontmatter(text, "generated_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    return text


def _run_document_validator(
    path: Path,
    ledger: Path,
    qa: Path,
    *,
    preflight: bool,
    repo_root: Path | None = None,
    publication: bool = False,
    cold_start_report: Path | None = None,
) -> list[str]:
    import subprocess
    args = [sys.executable, str(DOC_VALIDATOR), str(path), "--ledger", str(ledger), "--qa", str(qa)]
    if preflight:
        args.append("--preflight")
    if repo_root and repo_root.is_dir():
        args.extend(["--repo-root", str(repo_root)])
    if publication:
        args.append("--publication")
    if cold_start_report is not None:
        args.extend(["--cold-start-report", str(cold_start_report)])
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        return [line.removeprefix("ERROR: ").strip() for line in result.stderr.splitlines() if line.strip()]
    return []


def finalize(
    ledger: Path,
    qa: Path,
    candidate: Path,
    target: Path,
    *,
    draft: bool = False,
    publication: bool = False,
    cold_start_report: Path | None = None,
) -> dict[str, object]:
    manifest = validate_finalization_bundle.evaluate_bundle(
        ledger,
        qa,
        publication=publication,
    )
    if draft:
        if target.name == "PROJECT_STUDY_DOCUMENT.md":
            return {"status": "blocked", "reason": "incomplete-draft cannot target the formal document"}
        text = _candidate_text(candidate, status="incomplete-draft", readiness_status="not-ready", validation_status="pending")
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_name(f".{target.name}.draft-tmp")
        temp.write_text(text, encoding="utf-8", newline="\n")
        os.replace(temp, target)
        return {"status": "incomplete-draft", "target": str(target), "blockers": manifest}
    if not manifest.get("ready"):
        return {"status": "blocked", "reason": "readiness=false", "manifest": manifest}
    pending = _candidate_text(candidate, status="complete", readiness_status="ready", validation_status="pending")
    try:
        candidate_fm, _ = validate_learning_ledger.frontmatter_of(pending)
        repo_root = Path(candidate_fm.get("project_path", "")) if candidate_fm.get("project_path") else None
    except Exception:
        repo_root = None
    with tempfile.TemporaryDirectory(prefix="project-study-finalize-", dir=target.parent) as tmp:
        temp = Path(tmp) / target.name
        temp.write_text(pending, encoding="utf-8", newline="\n")
        errors = _run_document_validator(
            temp,
            ledger,
            qa,
            preflight=True,
            repo_root=repo_root,
            publication=publication,
        )
        if errors:
            return {"status": "blocked", "reason": "preflight-failed", "errors": errors, "target_unchanged": True}
        validated = _set_frontmatter(pending, "validation_status", "validated")
        temp.write_text(validated, encoding="utf-8", newline="\n")
        errors = _run_document_validator(
            temp,
            ledger,
            qa,
            preflight=False,
            repo_root=repo_root,
            publication=publication,
            cold_start_report=cold_start_report,
        )
        if errors:
            return {"status": "blocked", "reason": "final-validation-failed", "errors": errors, "target_unchanged": True}
        backup = target.with_name(f".{target.name}.finalizer-backup")
        if backup.exists():
            backup.unlink()
        if target.exists():
            os.replace(target, backup)
        try:
            os.replace(temp, target)
        except Exception:
            if backup.exists() and not target.exists():
                os.replace(backup, target)
            raise
        backup.unlink(missing_ok=True)
    if publication:
        return {
            "status": "release-pending",
            "target": str(target),
            "document_hash": hashlib.sha256(target.read_bytes()).hexdigest(),
            "readiness": manifest,
            "validation_status": "validated",
            "next_action": "prepare and commit unified schema 6.0 release receipt",
        }
    return {"status": "saved", "target": str(target), "readiness": manifest, "validation_status": "validated"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--publication", action="store_true")
    parser.add_argument("--cold-start-report", type=Path)
    args = parser.parse_args()
    result = finalize(
        args.ledger,
        args.qa,
        args.candidate,
        args.target,
        draft=args.draft,
        publication=args.publication,
        cold_start_report=args.cold_start_report,
    )
    print(result)
    return 0 if result.get("status") in {"saved", "incomplete-draft", "release-pending"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
