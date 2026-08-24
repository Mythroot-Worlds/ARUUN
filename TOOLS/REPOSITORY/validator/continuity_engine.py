#!/usr/bin/env python3
"""ARUUN read-only continuity engine.

Folder-dependent document continuity analysis for Git repositories.

This first implementation deliberately avoids deciding canon. It reports
possible information loss, additions, modifications, and scope anomalies so a
creator can review them before consolidation.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
from pathlib import Path
from typing import Iterable

IGNORE_PARTS = {".git", ".github", "__pycache__"}
DOC_EXTENSIONS = {".md", ".txt"}


def git(*args: str) -> str:
    p = subprocess.run(["git", *args], text=True, capture_output=True, check=True)
    return p.stdout


def current_files(root: Path) -> list[Path]:
    out = []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in DOC_EXTENSIONS:
            continue
        if any(part in IGNORE_PARTS for part in p.parts):
            continue
        out.append(p)
    return sorted(out)


def history_for(path: Path, root: Path, limit: int = 20) -> list[str]:
    rel = path.relative_to(root).as_posix()
    try:
        text = git("log", "--follow", "--format=%H", f"-n{limit}", "--", rel)
    except subprocess.CalledProcessError:
        return []
    return [x for x in text.splitlines() if x]


def old_content(commit: str, path: Path, root: Path) -> str | None:
    rel = path.relative_to(root).as_posix()
    try:
        return git("show", f"{commit}:{rel}")
    except subprocess.CalledProcessError:
        return None


def normalize(line: str) -> str:
    line = re.sub(r"[`*_#>-]", " ", line.lower())
    line = re.sub(r"\s+", " ", line).strip()
    return line


def facts(text: str) -> set[str]:
    result = set()
    for raw in text.splitlines():
        line = normalize(raw)
        if len(line) >= 35 and not line.startswith(("status:", "scope:", "source:", "---")):
            result.add(line)
    return result


def numbers(text: str) -> set[str]:
    return set(re.findall(r"\b\d+(?:\.\d+)?%?\b", text))


def classify(current: Path, root: Path) -> dict:
    rel = current.relative_to(root).as_posix()
    parts = current.relative_to(root).parts
    return {
        "path": rel,
        "folder": "/".join(parts[:-1]),
        "filename": current.name,
        "archive": "07_ARCHIVE" in parts or "ARCHIVE" in parts,
        "tool": "TOOLS" in parts,
        "scope_tokens": [p.lower() for p in parts[:-1]],
    }


def compare(current_text: str, previous_text: str) -> dict:
    cf, pf = facts(current_text), facts(previous_text)
    return {
        "preserved": sorted(cf & pf),
        "added": sorted(cf - pf),
        "potentially_dropped": sorted(pf - cf),
        "numbers_current": sorted(numbers(current_text)),
        "numbers_previous": sorted(numbers(previous_text)),
        "similarity": round(difflib.SequenceMatcher(None, previous_text, current_text).ratio(), 4),
    }


def analyze(path: Path, root: Path) -> dict:
    current_text = path.read_text(encoding="utf-8", errors="replace")
    info = classify(path, root)
    commits = history_for(path, root)
    versions = []
    # Current HEAD is represented by the file itself; compare up to the latest
    # historical state that differs from current content.
    for commit in commits[1:]:
        previous = old_content(commit, path, root)
        if previous is None or previous == current_text:
            continue
        cmp = compare(current_text, previous)
        versions.append({"commit": commit, **cmp})
        if len(versions) >= 5:
            break
    return {**info, "history_versions_checked": len(versions), "versions": versions}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="TOOLS/REPOSITORY/REPORTS")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)

    docs = current_files(root)
    records = [analyze(p, root) for p in docs]
    records = [r for r in records if not r["archive"]]

    findings = []
    for r in records:
        for v in r["versions"]:
            if v["potentially_dropped"]:
                findings.append({
                    "type": "POTENTIAL_CANON_LOSS",
                    "severity": "REVIEW",
                    "path": r["path"],
                    "folder": r["folder"],
                    "commit": v["commit"],
                    "dropped_count": len(v["potentially_dropped"]),
                    "dropped": v["potentially_dropped"][:50],
                })
            if v["numbers_current"] != v["numbers_previous"]:
                findings.append({
                    "type": "NUMERIC_CHANGE",
                    "severity": "REVIEW",
                    "path": r["path"],
                    "folder": r["folder"],
                    "commit": v["commit"],
                    "previous": v["numbers_previous"],
                    "current": v["numbers_current"],
                })

    report = {
        "mode": "READ_ONLY",
        "documents": len(records),
        "findings": len(findings),
        "records": records,
        "findings_detail": findings,
    }
    (out / "CONTINUITY_INDEX.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = ["# ARUUN Continuity Report", "", "**Mode:** READ-ONLY", "", f"Documents analyzed: {len(records)}", f"Continuity findings: {len(findings)}", ""]
    if not findings:
        lines.append("No continuity findings were generated.")
    else:
        lines += ["## Findings", ""]
        for i, f in enumerate(findings, 1):
            lines.append(f"### {i}. {f['type']} — {f['path']}")
            lines.append(f"- Folder: `{f['folder']}`")
            lines.append(f"- Historical commit: `{f['commit']}`")
            if f['type'] == 'POTENTIAL_CANON_LOSS':
                lines.append(f"- Potentially dropped statements: {f['dropped_count']}")
                for x in f['dropped'][:10]:
                    lines.append(f"  - {x}")
            else:
                lines.append(f"- Previous numbers: {f['previous']}")
                lines.append(f"- Current numbers: {f['current']}")
            lines.append("")
    (out / "CONTINUITY_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
