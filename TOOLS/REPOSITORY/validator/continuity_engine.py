#!/usr/bin/env python3
"""ARUUN read-only continuity engine.

Folder-dependent document continuity analysis for Git repositories.

The engine reports preserved, added, modified, and potentially dropped
information. It never decides canon or mutates world content.
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
TEST_PREFIXES = ("TOOLS/REPOSITORY/CONTINUITY_TEST/",)
NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
    "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
    "eighteen": "18", "nineteen": "19", "twenty": "20",
}


def git(*args: str) -> str:
    p = subprocess.run(["git", *args], text=True, capture_output=True, check=True)
    return p.stdout


def current_files(root: Path, scope: str | None = None) -> list[Path]:
    base = root / scope if scope else root
    if not base.exists():
        return []
    out = []
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
    try:
        return [x for x in git("log", "--follow", "--format=%H", f"-n{limit}", "--", path.relative_to(root).as_posix()).splitlines() if x]
    except subprocess.CalledProcessError:
        return []


def old_content(commit: str, path: Path, root: Path) -> str | None:
    try:
        return git("show", f"{commit}:{path.relative_to(root).as_posix()}")
    except subprocess.CalledProcessError:
        return None


def normalize(line: str) -> str:
    line = re.sub(r"[`*_#>-]", " ", line.lower())
    return re.sub(r"\s+", " ", line).strip()


def facts(text: str) -> set[str]:
    result = set()
    for raw in text.splitlines():
        line = normalize(raw)
        if len(line) >= 35 and not line.startswith(("status:", "scope:", "source:", "---")):
            result.add(line)
    return result


def numeric_tokens(text: str) -> tuple[str, ...]:
    t = normalize(text)
    for word, digit in NUMBER_WORDS.items():
        t = re.sub(rf"\b{word}\b", digit, t)
    return tuple(re.findall(r"\b\d+(?:\.\d+)?%?\b", t))


def number_skeleton(line: str) -> str:
    t = normalize(line)
    for word in NUMBER_WORDS:
        t = re.sub(rf"\b{word}\b", "<NUM>", t)
    t = re.sub(r"\b\d+(?:\.\d+)?(?:\s*(?:%|million|billion|thousand|m|km|kg|g|years?|months?|days?|people))?\b", "<NUM>", t)
    return re.sub(r"\s+", " ", t).strip()


def factual_numeric_changes(current_text: str, previous_text: str) -> list[dict]:
    previous = {}
    for raw in previous_text.splitlines():
        n = normalize(raw)
        if len(n) < 20:
            continue
        tokens = numeric_tokens(n)
        if tokens:
            previous.setdefault(number_skeleton(n), set()).update(tokens)
    changes = []
    for raw in current_text.splitlines():
        n = normalize(raw)
        if len(n) < 20:
            continue
        tokens = numeric_tokens(n)
        skeleton = number_skeleton(n)
        if tokens and skeleton in previous and set(tokens) != previous[skeleton]:
            changes.append({"statement": n, "previous": sorted(previous[skeleton]), "current": sorted(set(tokens))})
    return changes


def classify(current: Path, root: Path) -> dict:
    rel = current.relative_to(root).as_posix()
    parts = current.relative_to(root).parts
    return {
        "path": rel,
        "folder": "/".join(parts[:-1]),
        "filename": current.name,
        "archive": "07_ARCHIVE" in parts or "ARCHIVE" in parts,
        "tool": "TOOLS" in parts,
        "test_fixture": rel.startswith(TEST_PREFIXES),
        "administrative": rel.startswith(ADMIN_PATH_PREFIXES) or current.name in ADMIN_FILENAMES,
        "scope_tokens": [p.lower() for p in parts[:-1]],
    }


def compare(current_text: str, previous_text: str) -> dict:
    cf, pf = facts(current_text), facts(previous_text)
    modified = []
    unmatched_previous = set(pf)
    unmatched_current = set(cf)
    # Exact matches are preserved first.
    preserved = cf & pf
    unmatched_previous -= preserved
    unmatched_current -= preserved
    # Similar factual statements are modifications, not loss + addition.
    pairs = []
    for p in unmatched_previous:
        best, score = "", 0.0
        for c in unmatched_current:
            s = difflib.SequenceMatcher(None, p, c).ratio()
            if s > score:
                best, score = c, s
        if best and score >= 0.72:
            pairs.append((p, best, score))
    used_p, used_c = set(), set()
    for p, c, score in sorted(pairs, key=lambda x: x[2], reverse=True):
        if p in used_p or c in used_c:
            continue
        used_p.add(p); used_c.add(c)
        modified.append({"previous": p, "current": c, "similarity": round(score, 3)})
    numeric_changes = factual_numeric_changes(current_text, previous_text)
    return {
        "preserved": sorted(preserved),
        "added": sorted(unmatched_current - used_c),
        "potentially_dropped": sorted(unmatched_previous - used_p),
        "modified": modified,
        "numeric_fact_changes": numeric_changes,
        "similarity": round(difflib.SequenceMatcher(None, previous_text, current_text).ratio(), 4),
    }


def analyze(path: Path, root: Path) -> dict:
    current_text = path.read_text(encoding="utf-8", errors="replace")
    info = classify(path, root)
    versions = []
    for commit in history_for(path, root)[1:]:
        previous = old_content(commit, path, root)
        if previous is None or previous == current_text:
            continue
        cmp = compare(current_text, previous)
        overlay = list(difflib.unified_diff(previous.splitlines(), current_text.splitlines(), fromfile=f"previous:{commit[:12]}", tofile="current", lineterm=""))
        versions.append({"commit": commit, **cmp, "overlay": overlay})
        if len(versions) >= 5:
            break
    return {**info, "history_versions_checked": len(versions), "versions": versions}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="TOOLS/REPOSITORY/REPORTS")
    ap.add_argument("--scope", default=None)
    ap.add_argument("--include-test-fixtures", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve(); out = root / args.out; out.mkdir(parents=True, exist_ok=True)
    records = [analyze(p, root) for p in current_files(root, args.scope)]
    records = [r for r in records if not r["archive"]]
    findings = []
    for r in records:
        if r["administrative"] or (r["tool"] and not (args.include_test_fixtures and r["test_fixture"])):
            continue
        for v in r["versions"]:
            prefix = "TEST_" if r["test_fixture"] else ""
            if v["potentially_dropped"]:
                findings.append({"type": prefix+"POTENTIAL_CANON_LOSS", "severity": "REVIEW", "path": r["path"], "folder": r["folder"], "commit": v["commit"], "dropped": v["potentially_dropped"][:50]})
            if v["modified"]:
                findings.append({"type": prefix+"MODIFIED_FACT", "severity": "REVIEW", "path": r["path"], "folder": r["folder"], "commit": v["commit"], "changes": v["modified"][:50]})
            if v["numeric_fact_changes"]:
                findings.append({"type": prefix+"NUMERIC_FACT_CHANGE", "severity": "REVIEW", "path": r["path"], "folder": r["folder"], "commit": v["commit"], "changes": v["numeric_fact_changes"][:50]})
    report = {"mode":"READ_ONLY","scope":args.scope or "ALL_ACTIVE_NON_GENERATED_CONTENT","generated_reports_excluded":True,"administrative_documents_excluded_from_canon_findings":True,"test_fixtures_included":bool(args.include_test_fixtures),"documents":len(records),"findings":len(findings),"records":records,"findings_detail":findings}
    (out/"CONTINUITY_INDEX.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    lines=["# ARUUN Continuity Report","","**Mode:** READ-ONLY",f"**Scope:** `{args.scope or 'ALL_ACTIVE_NON_GENERATED_CONTENT'}`","**Generated reports excluded:** yes","**Administrative/master documents excluded from canon findings:** yes",f"**Test fixtures included:** {'yes' if args.include_test_fixtures else 'no'}","",f"Documents analyzed: {len(records)}",f"Continuity findings: {len(findings)}","",("No canon continuity findings were generated." if not findings else "## Findings\n")]
    for i,f in enumerate(findings,1):
        lines += [f"### {i}. {f['type']} — `{f['path']}`",f"- Historical commit: `{f['commit']}`"]
        if "dropped" in f: lines += [f"- Potentially dropped: {len(f['dropped'])}"]+[f"  - {x}" for x in f['dropped'][:10]]
        if "changes" in f:
            for c in f['changes'][:10]: lines.append(f"- {c}")
        lines.append("")
    (out/"CONTINUITY_REPORT.md").write_text("\n".join(lines),encoding="utf-8")
    # Separate machine-readable review queue; human review is required before any canon action.
    queue = [f for f in findings if not f["type"].startswith("TEST_")]
    qpath = out / "REVIEW_QUEUE.json"
    qpath.write_text(json.dumps({"mode":"HUMAN_REVIEW_REQUIRED","items":queue},indent=2),encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
