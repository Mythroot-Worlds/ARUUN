#!/usr/bin/env python3
"""ARUUN read-only continuity engine.

Folder-dependent document continuity analysis for Git repositories.

The engine is intentionally conservative: it reports possible information loss
and meaningful fact changes for review; it never decides canon or mutates world
content.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
from pathlib import Path

IGNORE_PARTS = {".git", ".github", "__pycache__"}
DOC_EXTENSIONS = {".md", ".txt"}
GENERATED_PREFIXES = ("TOOLS/REPOSITORY/REPORTS/",)
ADMIN_PATH_PREFIXES = ("00_MASTER/",)
ADMIN_FILENAMES = {"CHANGELOG.md", "README.md"}


def git(*args: str) -> str:
    p = subprocess.run(["git", *args], text=True, capture_output=True, check=True)
    return p.stdout


def current_files(root: Path, scope: str | None = None) -> list[Path]:
    base = root / scope if scope else root
    out: list[Path] = []
    if not base.exists():
        return out
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in DOC_EXTENSIONS:
            continue
        rel = p.relative_to(root).as_posix()
        if any(part in IGNORE_PARTS for part in p.parts):
            continue
        if rel.startswith(GENERATED_PREFIXES):
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
    return re.sub(r"\s+", " ", line).strip()


def facts(text: str) -> set[str]:
    result: set[str] = set()
    for raw in text.splitlines():
        line = normalize(raw)
        if len(line) >= 35 and not line.startswith(("status:", "scope:", "source:", "---")):
            result.add(line)
    return result


def number_skeleton(line: str) -> str:
    """Normalize a factual line while replacing numeric values with a marker."""
    line = normalize(line)
    line = re.sub(r"\b\d+(?:\.\d+)?(?:\s*(?:%|million|billion|thousand|m|km|kg|g|years?|months?|days?|people))?\b", "<NUM>", line)
    return re.sub(r"\s+", " ", line).strip()


def factual_numeric_changes(current_text: str, previous_text: str) -> list[dict]:
    """Find numeric changes only when the surrounding factual statement persists."""
    previous: dict[str, set[str]] = {}
    for raw in previous_text.splitlines():
        n = normalize(raw)
        if len(n) < 20 or n.startswith(("status:", "scope:", "source:", "---")):
            continue
        skeleton = number_skeleton(raw)
        nums = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", n))
        if nums:
            previous.setdefault(skeleton, set()).update(nums)

    changes: list[dict] = []
    for raw in current_text.splitlines():
        n = normalize(raw)
        if len(n) < 20 or n.startswith(("status:", "scope:", "source:", "---")):
            continue
        skeleton = number_skeleton(raw)
        nums = set(re.findall(r"\b\d+(?:\.\d+)?%?\b", n))
        if not nums or skeleton not in previous:
            continue
        old_nums = sorted(previous[skeleton])
        new_nums = sorted(nums)
        if old_nums != new_nums:
            changes.append({"statement": n, "previous": old_nums, "current": new_nums})
    return changes


def classify(current: Path, root: Path) -> dict:
    rel = current.relative_to(root).as_posix()
    parts = current.relative_to(root).parts
    administrative = (
        rel.startswith(ADMIN_PATH_PREFIXES)
        or current.name in ADMIN_FILENAMES
    )
    return {
        "path": rel,
        "folder": "/".join(parts[:-1]),
        "filename": current.name,
        "archive": "07_ARCHIVE" in parts or "ARCHIVE" in parts,
        "tool": "TOOLS" in parts,
        "administrative": administrative,
        "scope_tokens": [p.lower() for p in parts[:-1]],
    }


def compare(current_text: str, previous_text: str) -> dict:
    cf, pf = facts(current_text), facts(previous_text)
    return {
        "preserved": sorted(cf & pf),
        "added": sorted(cf - pf),
        "potentially_dropped": sorted(pf - cf),
        "numeric_fact_changes": factual_numeric_changes(current_text, previous_text),
        "similarity": round(difflib.SequenceMatcher(None, previous_text, current_text).ratio(), 4),
    }


def analyze(path: Path, root: Path) -> dict:
    current_text = path.read_text(encoding="utf-8", errors="replace")
    info = classify(path, root)
    commits = history_for(path, root)
    versions = []
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
    ap.add_argument("--scope", default=None, help="Repository-relative folder to analyze, e.g. 03_PEOPLES/CULTURES/HEARTH")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)

    docs = current_files(root, args.scope)
    records = [analyze(p, root) for p in docs]
    records = [r for r in records if not r["archive"]]

    findings = []
    for r in records:
        # Administrative/master documents are useful reference material, but
        # are not treated as world-canon lineage by this engine.
        if r["tool"] or r["administrative"]:
            continue
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
            if v["numeric_fact_changes"]:
                findings.append({
                    "type": "NUMERIC_FACT_CHANGE",
                    "severity": "REVIEW",
                    "path": r["path"],
                    "folder": r["folder"],
                    "commit": v["commit"],
                    "changes": v["numeric_fact_changes"][:50],
                })

    report = {
        "mode": "READ_ONLY",
        "scope": args.scope or "ALL_ACTIVE_NON_GENERATED_CONTENT",
        "generated_reports_excluded": True,
        "administrative_documents_excluded_from_canon_findings": True,
        "documents": len(records),
        "findings": len(findings),
        "records": records,
        "findings_detail": findings,
    }
    (out / "CONTINUITY_INDEX.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# ARUUN Continuity Report", "", "**Mode:** READ-ONLY", "",
        f"**Scope:** `{args.scope or 'ALL ACTIVE NON-GENERATED CONTENT'}`",
        "**Generated audit reports excluded:** yes",
        "**Administrative/master documents excluded from canon findings:** yes", "",
        f"Documents analyzed: {len(records)}", f"Continuity findings: {len(findings)}", "",
    ]
    if not findings:
        lines.append("No canon continuity findings were generated.")
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
                for change in f['changes'][:10]:
                    lines.append(f"- `{change['statement']}`: {change['previous']} → {change['current']}")
            lines.append("")
    (out / "CONTINUITY_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
