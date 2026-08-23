#!/usr/bin/env python3
"""ARUUN repository audit validator.

Read-only by design. Scans the repository, infers document identity from paths
and metadata, and writes audit reports. It never renames or rewrites files.

Usage:
    python TOOLS/REPOSITORY/validate_repo.py
    python TOOLS/REPOSITORY/validate_repo.py --root . --out TOOLS/REPOSITORY/REPORTS
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

IGNORE_DIRS = {".git", ".github", "node_modules"}
ACTIVE_TOP = {"00_MASTER", "01_WORLD", "02_ECOLOGY", "03_PEOPLES", "04_HISTORY", "05_SYSTEMS", "06_WORKING", "08_RELEASES"}
ARCHIVE_TOP = "07_ARCHIVE"
VALID_LAYERS = {"world", "tool", "reference", "audit", "archive", "release"}
VALID_STATUS = {"canon", "working_model", "inference", "proposal", "open", "unknown", "retired", "canon_reference", "working", "provisional"}
VALID_AUTHORITY = {"world", "regional", "continental", "tool", "reference", "supporting", "historical", "audit"}

SUBJECT_ALIASES = {
    "family_birth_childhood": "family.birth_childhood",
    "birth_childhood": "family.birth_childhood",
    "childhood_and_birth": "family.birth_childhood",
    "family_partnership": "family.partnership",
    "governance_and_authority": "governance.authority",
    "governance_authority": "governance.authority",
    "food_subsistence": "food.subsistence",
    "settlement_housing": "settlement.housing",
}

@dataclass
class Finding:
    id: str
    severity: str
    category: str
    path: str
    message: str
    recommendation: str = ""

@dataclass
class Document:
    path: str
    filename: str
    title: str = ""
    id: str = ""
    domain: str = ""
    layer: str = ""
    scope: str = ""
    status: str = ""
    authority: str = ""
    world: str = ""
    continent: str = ""
    people: str = ""
    subject: str = ""
    source_of_truth: Optional[bool] = None
    archive: bool = False


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    data = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"\'')
        data[key] = value
    return data


def inline_status(text: str) -> str:
    m = re.search(r"\*\*Status:\*\*\s*([^\n]+)", text, re.I)
    return m.group(1).strip().lower() if m else ""


def first_heading(text: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def normalized_subject(stem: str) -> str:
    key = stem.lower().replace("-", "_").replace(" ", "_")
    if key.endswith("_comparative"):
        key = key[:-12]
    if key in SUBJECT_ALIASES:
        return SUBJECT_ALIASES[key]
    parts = [p for p in key.split("_") if p]
    return ".".join(parts)


def expected_from_path(rel: Path) -> dict[str, str]:
    p = rel.parts
    out = {}
    if p and p[0] == "03_PEOPLES":
        out["domain"] = "peoples"
        if len(p) >= 3 and p[1] == "CULTURES":
            out["continent"] = p[2].title()
            if len(p) >= 4 and p[3] != "COMPARATIVE":
                out["people"] = p[3].title()
                out["scope"] = "people"
            elif len(p) >= 4 and p[3] == "COMPARATIVE":
                out["scope"] = "subject"
        out["layer"] = "reference" if "COMPARATIVE" in p else "world"
    elif p and p[0] == "02_ECOLOGY":
        out["domain"] = "ecology"
        out["layer"] = "tool" if any(x in rel.name.upper() for x in ("MATRIX", "CREATION", "PREDICTIVE", "NECESSITY", "PACKAGE")) else "world"
    elif p and p[0] == "01_WORLD":
        out["domain"] = "world"
        out["layer"] = "world"
    elif p and p[0] == "00_MASTER":
        out["domain"] = "master"
        out["layer"] = "reference"
    elif p and p[0] == "TOOLS":
        out["domain"] = "repository"
        out["layer"] = "tool"
    elif p and p[0] == ARCHIVE_TOP:
        out["layer"] = "archive"
    return out


def scan(root: Path) -> tuple[list[Document], list[Finding]]:
    docs: list[Document] = []
    findings: list[Finding] = []
    counter = 1

    for path in sorted(root.rglob("*.md")):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        rel = path.relative_to(root)
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        exp = expected_from_path(rel)
        archive = bool(rel.parts and rel.parts[0] == ARCHIVE_TOP)
        stem = path.stem
        doc = Document(
            path=str(rel), filename=path.name,
            title=fm.get("title", first_heading(text)), id=fm.get("id", ""),
            domain=fm.get("domain", exp.get("domain", "")),
            layer=fm.get("layer", exp.get("layer", "")),
            scope=fm.get("scope", ""), status=fm.get("status", inline_status(text)),
            authority=fm.get("authority", ""), world=fm.get("world", ""),
            continent=fm.get("continent", exp.get("continent", "")),
            people=fm.get("people", exp.get("people", "")),
            subject=fm.get("subject", normalized_subject(stem)),
            source_of_truth=(fm.get("source_of_truth", "").lower() == "true") if "source_of_truth" in fm else None,
            archive=archive,
        )
        docs.append(doc)

        if archive:
            continue
        if not doc.id:
            findings.append(Finding(f"META-{counter:04d}", "WARNING", "metadata", str(rel), "Missing stable document id.", "Assign a stable ID during migration.")); counter += 1
        if not fm and not inline_status(text):
            findings.append(Finding(f"META-{counter:04d}", "WARNING", "metadata", str(rel), "No recognized frontmatter or inline Status metadata.", "Infer metadata from path/content and migrate when actively edited.")); counter += 1
        if doc.layer not in VALID_LAYERS:
            findings.append(Finding(f"META-{counter:04d}", "WARNING", "metadata", str(rel), f"Unknown layer: {doc.layer or '<missing>'}.", "Use the schema layer vocabulary.")); counter += 1
        if doc.status and doc.status not in VALID_STATUS:
            findings.append(Finding(f"META-{counter:04d}", "INFO", "status", str(rel), f"Unnormalized status: {doc.status}.", "Map it to the target status vocabulary during migration.")); counter += 1
        if doc.authority and doc.authority not in VALID_AUTHORITY:
            findings.append(Finding(f"META-{counter:04d}", "WARNING", "authority", str(rel), f"Unknown authority: {doc.authority}.", "Map it to the target authority vocabulary.")); counter += 1

        # Path ↔ metadata checks.
        for field in ("domain", "layer", "continent", "people"):
            if field in exp and getattr(doc, field) and getattr(doc, field).lower() != exp[field].lower():
                findings.append(Finding(f"PATH-{counter:04d}", "ERROR", "path_metadata", str(rel), f"{field}={getattr(doc, field)!r} conflicts with path expectation {exp[field]!r}.", "Review the path and metadata; do not auto-rewrite.")); counter += 1

        # Filename rules.
        upper = stem.upper()
        suspicious = any(token in upper for token in ("FINAL", "FINAL2", "BATCH", "TEMP", "NEW_", "UPDATED", "REVISION"))
        if suspicious:
            findings.append(Finding(f"NAME-{counter:04d}", "WARNING", "filename", str(rel), "Filename contains a production/temporary naming pattern.", "Rename to the subject-based convention after reference/collision review.")); counter += 1
        if "COMPARATIVE" in rel.parts and not stem.endswith("_COMPARATIVE"):
            findings.append(Finding(f"NAME-{counter:04d}", "WARNING", "filename", str(rel), "Comparative document is not explicitly marked as comparative in its filename.", "Use <SUBJECT>_COMPARATIVE.md.")); counter += 1

    return docs, findings


def duplicate_findings(docs: list[Document], findings: list[Finding]) -> None:
    groups: dict[tuple[str, str, str, str], list[Document]] = {}
    for d in docs:
        if d.archive:
            continue
        key = (d.continent.lower(), d.people.lower(), d.subject.lower(), d.scope.lower())
        groups.setdefault(key, []).append(d)
    n = sum(1 for f in findings if f.id.startswith("DUP-")) + 1
    for key, items in groups.items():
        if len(items) > 1 and key[2] and key[1] and "comparative" not in " ".join(x.path.lower() for x in items):
            findings.append(Finding(f"DUP-{n:04d}", "WARNING", "duplicate_subject", items[0].path, f"Multiple active documents appear to represent subject {key[2]!r} for {key[1]}.", "Review source-of-truth authority and legacy aliases.")); n += 1


def write_reports(root: Path, out: Path, docs: list[Document], findings: list[Finding]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    duplicate_findings(docs, findings)
    index = "# ARUUN Repository Index\n\nGenerated by the read-only validator.\n\n| Path | ID | Layer | Scope | Status | Authority | Source of Truth |\n|---|---|---|---|---|---|---|\n"
    for d in docs:
        index += f"| `{d.path}` | `{d.id}` | `{d.layer}` | `{d.scope}` | `{d.status}` | `{d.authority}` | `{d.source_of_truth}` |\n"
    (out / "REPOSITORY_INDEX.md").write_text(index, encoding="utf-8")

    naming = "# ARUUN Naming Report\n\nFilename/path findings from the read-only audit.\n\n"
    for f in findings:
        if f.category == "filename":
            naming += f"## {f.id} — {f.severity}\n- **Path:** `{f.path}`\n- **Finding:** {f.message}\n- **Recommendation:** {f.recommendation}\n\n"
    (out / "NAMING_REPORT.md").write_text(naming, encoding="utf-8")

    ledger = "# ARUUN Discrepancy Ledger\n\nRead-only findings. Nothing here is automatically treated as a canon correction.\n\n"
    for f in findings:
        if f.category != "filename":
            ledger += f"## {f.id} — {f.severity}\n- **Category:** {f.category}\n- **Path:** `{f.path}`\n- **Finding:** {f.message}\n- **Recommendation:** {f.recommendation}\n- **Status:** open\n\n"
    (out / "DISCREPANCY_LEDGER.md").write_text(ledger, encoding="utf-8")

    summary = {"documents_scanned": len(docs), "findings": len(findings), "errors": sum(f.severity == "ERROR" for f in findings), "warnings": sum(f.severity == "WARNING" for f in findings), "info": sum(f.severity == "INFO" for f in findings)}
    lines = ["# ARUUN Repository Audit Summary", "", "**Mode:** READ-ONLY", "", "| Metric | Count |", "|---|---:|"] + [f"| {k.replace('_',' ').title()} | {v} |" for k, v in summary.items()]
    (out / "AUDIT_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="TOOLS/REPOSITORY/REPORTS")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    out = (root / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)
    docs, findings = scan(root)
    write_reports(root, out, docs, findings)
    print(f"Scanned {len(docs)} Markdown documents; generated {len(findings)} findings.")
    print(f"Reports: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
