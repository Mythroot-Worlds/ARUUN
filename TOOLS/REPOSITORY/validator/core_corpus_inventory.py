#!/usr/bin/env python3
"""CORE A.C.E. Phase 1 — deterministic, read-only ARUUN corpus inventory.

This inventory observes source documents and writes only to the designated report
area. It intentionally excludes generated reports/releases/tooling from the
source-of-truth corpus. No canon, working material, or holdout is modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from core_document_identity import identify

EXCLUDED_TOP = {"TOOLS", ".GITHUB", ".GIT"}
EXCLUDED_RELEASE_PARTS = {"08_RELEASES", "REPORTS"}
INCLUDED_EXTENSIONS = {".md", ".yaml", ".yml", ".json"}


def eligible(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if path.suffix.lower() not in INCLUDED_EXTENSIONS:
        return False
    parts = {p.upper() for p in rel.parts[:-1]}
    if rel.parts[0].upper() in EXCLUDED_TOP:
        return False
    if parts & EXCLUDED_RELEASE_PARTS:
        return False
    return True


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def front_matter(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {}
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
        data[key.strip()] = value.strip().strip('"\'')
    return data


def authority_layer(identity: dict, meta: dict) -> str:
    status = str(meta.get("status", "")).upper()
    if status in {"CANON", "C"}:
        return "CANON"
    if status in {"PROVISIONAL", "P"}:
        return "PROVISIONAL"
    if status in {"OPEN", "O"}:
        return "OPEN"
    if status in {"CONFLICTED", "X"}:
        return "CONFLICTED"
    if status in {"DEPRECATED", "D"}:
        return "DEPRECATED"
    return identity.get("role", "UNKNOWN")


def inventory(root: Path):
    docs = []
    for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix().lower()):
        if not path.is_file() or not eligible(path, root):
            continue
        rel = path.relative_to(root).as_posix()
        identity = identify(rel)
        meta = front_matter(path)
        docs.append({
            "path": rel,
            "front_matter": meta,
            "status": meta.get("status") or meta.get("lifecycle") or None,
            "domain": meta.get("domain") or (Path(rel).parts[1] if len(Path(rel).parts) > 1 else None),
            "cultural_scope": meta.get("scope") or identity.get("scope"),
            "subject": identity.get("subject"),
            "content_type": identity.get("content_type"),
            "role": identity.get("role"),
            "identity_layer": identity.get("identity_layer"),
            "authority_layer": authority_layer(identity, meta),
            "naming": identity.get("naming"),
            "identity_basis": identity.get("identity_basis"),
            "identity_confidence": identity.get("identity_confidence"),
            "provenance": {"source_path": rel, "sha256": sha256(path)},
        })
    return docs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="TOOLS/REPOSITORY/REPORTS")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)
    docs = inventory(root)
    payload = {
        "engine": "CORE A.C.E.",
        "phase": "PHASE_1_CORPUS_INVENTORY",
        "mode": "READ_ONLY",
        "source_policy": {
            "included": "eligible corpus documents outside generated releases, reports, tooling, and repository metadata",
            "excluded": ["TOOLS", "08_RELEASES", "TOOLS/REPOSITORY/REPORTS", ".github", ".git"],
        },
        "document_count": len(docs),
        "documents": docs,
        "safety": {
            "source_mutation": False,
            "canon_mutation": False,
            "working_material_promotion": False,
            "holdout_mutation": False,
            "automatic_placement": False,
        },
    }
    raw = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    digest = hashlib.sha256(raw.encode()).hexdigest()
    payload["inventory_sha256"] = digest
    (out / "CORE_CORPUS_INVENTORY.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    by_domain = {}
    by_type = {}
    by_role = {}
    for d in docs:
        for table, key in ((by_domain, d["domain"] or "UNKNOWN"), (by_type, d["content_type"] or "UNKNOWN"), (by_role, d["role"] or "UNKNOWN")):
            table[key] = table.get(key, 0) + 1
    lines = [
        "# CORE A.C.E. Corpus Inventory",
        "",
        "**Phase:** 1 — Corpus Inventory  ",
        "**Mode:** READ-ONLY  ",
        f"**Documents in source corpus:** {len(docs)}  ",
        f"**Inventory SHA-256:** `{digest}`",
        "",
        "## Safety",
        "- Source mutation: **OFF**",
        "- Canon mutation: **OFF**",
        "- Working-material promotion: **OFF**",
        "- Holdout mutation: **OFF**",
        "- Automatic placement: **OFF**",
        "",
        "## Source policy",
        "Generated releases, validator reports, tooling, repository metadata, and GitHub workflow material are excluded from source-of-truth inventory.",
        "",
        "## Summary by domain",
    ]
    lines += [f"- `{k}`: **{v}**" for k, v in sorted(by_domain.items())]
    lines += ["", "## Summary by content type"]
    lines += [f"- `{k}`: **{v}**" for k, v in sorted(by_type.items())]
    lines += ["", "## Summary by role"]
    lines += [f"- `{k}`: **{v}**" for k, v in sorted(by_role.items())]
    lines += ["", "## Inventory entries"]
    for d in docs:
        lines.append(f"- `{d['path']}` — subject=`{d['subject']}`, type=`{d['content_type']}`, role=`{d['role']}`, authority=`{d['authority_layer']}`")
    (out / "CORE_CORPUS_INVENTORY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"CORE A.C.E. Phase 1: inventoried {len(docs)} source documents; inventory digest {digest}.")


if __name__ == "__main__":
    main()
