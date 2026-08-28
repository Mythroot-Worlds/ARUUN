#!/usr/bin/env python3
"""CORE A.C.E. corpus observer: read-only inventory/orchestration boundary.

The observer does not decide canon, mutate source material, or infer authority
from filenames alone. It records document-derived context first, then attaches
existing structural/artifact identity as contextual evidence for downstream
CORE engines.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from core_artifact_identity import resolve_identity as resolve_artifact_identity
from core_artifact_roles import infer_artifact_role

EXCLUDED_DIRS = {".git", ".github", "node_modules", "__pycache__"}
EXCLUDED_PREFIXES = (
    "TOOLS/REPOSITORY/REPORTS/",
    "TOOLS/REPOSITORY/CONTINUITY_TEST/",
)
EXCLUDED_RELEASE_MARKERS = ("/RELEASE/", "/RELEASES/", "_RELEASE")

FIELD_RE = re.compile(
    r"^\s*(?:[-#]\s*)?(subject|domain|scope|cultural[_ ]scope|population|region|subregion|entity|purpose|role|document[_ ]role|status|canonical[_ ]status|authority|authority[_ ]layer)\s*[:=-]\s*(.*?)\s*$",
    re.I,
)


def normalize(value: str | None) -> str | None:
    if value is None:
        return None
    value = re.sub(r"\s+", " ", value.strip())
    return value or None


def document_context(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    sample = text[:40000]
    lines = sample.splitlines()
    fields: dict[str, str] = {}
    in_frontmatter = bool(lines and lines[0].strip() == "---")
    scan = lines[1:] if in_frontmatter else lines[:160]
    if in_frontmatter:
        for line in scan:
            if line.strip() == "---":
                break
            match = FIELD_RE.match(line)
            if match:
                key = re.sub(r"\s+", "_", match.group(1).lower())
                fields[key] = normalize(match.group(2)) or ""
    else:
        for line in scan:
            match = FIELD_RE.match(line)
            if match:
                key = re.sub(r"\s+", "_", match.group(1).lower())
                fields.setdefault(key, normalize(match.group(2)) or "")

    headings = [re.sub(r"^#+\s*", "", line).strip() for line in lines if line.startswith("#")][:8]
    return {
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "bytes": len(text.encode("utf-8")),
        "fields": fields,
        "headings": headings,
        "content_evidence": bool(fields or headings),
    }


def in_source_scope(root: Path, path: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    upper = "/" + rel.upper() + "/"
    if any(marker in upper for marker in EXCLUDED_RELEASE_MARKERS):
        return False
    return path.suffix.lower() == ".md"


def observe(root: Path) -> list[dict]:
    records = []
    for path in sorted(root.rglob("*.md")):
        if not in_source_scope(root, path):
            continue
        rel = path.relative_to(root).as_posix()
        ctx = document_context(path)
        identity = resolve_artifact_identity(root, rel)
        fields = ctx["fields"]
        explicit_authority = fields.get("authority") or fields.get("authority_layer")
        explicit_status = fields.get("status") or fields.get("canonical_status")
        artifact_role = infer_artifact_role(
            layer=identity.get("layer"),
            authority=explicit_authority,
            path=rel,
            status=explicit_status,
        )
        records.append(
            {
                "path": rel,
                "document": {
                    "subject": fields.get("subject"),
                    "domain": fields.get("domain"),
                    "cultural_scope": fields.get("cultural_scope") or fields.get("scope"),
                    "population": fields.get("population"),
                    "region": fields.get("region"),
                    "subregion": fields.get("subregion"),
                    "entity": fields.get("entity"),
                    "purpose": fields.get("purpose"),
                    "role": fields.get("role") or fields.get("document_role"),
                    "status": explicit_status,
                    "authority": explicit_authority,
                },
                "content_evidence": {
                    "fields_observed": sorted(fields),
                    "headings": ctx["headings"],
                    "content_evidence_present": ctx["content_evidence"],
                },
                "identity": identity,
                "artifact_role": artifact_role,
                "provenance": {
                    "content_sha256": ctx["sha256"],
                    "identity_basis": identity.get("identity_basis", []),
                    "identity_source": identity.get("identity_source", {}),
                },
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="TOOLS/REPOSITORY/REPORTS")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)

    records = observe(root)
    payload = {
        "engine": "CORE A.C.E. Corpus Observer",
        "phase": "1 — Corpus Inventory / observation boundary",
        "mode": "READ_ONLY",
        "documents_in_scope": len(records),
        "documents": records,
        "safety": {
            "source_mutation": False,
            "canon_mutation": False,
            "working_material_promotion": False,
            "holdout_mutation": False,
            "automatic_placement": False,
            "generated_releases_as_sources": False,
            "filename_as_deciding_factor": False,
        },
        "operating_principle": "Document information is primary evidence; path/filename identity is contextual evidence, never a deciding factor by itself.",
    }
    (out / "CORE_CORPUS_OBSERVER.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md = [
        "# CORE A.C.E. Corpus Observer",
        "",
        "**Mode:** READ-ONLY",
        "**Phase:** 1 — Corpus Inventory / observation boundary",
        "",
        f"Documents in scope: **{len(records)}**",
        "",
        "## Safety",
        "- Source mutation: **OFF**",
        "- Canon mutation: **OFF**",
        "- Working-material promotion: **OFF**",
        "- Holdout mutation: **OFF**",
        "- Automatic placement: **OFF**",
        "- Generated releases used as sources: **OFF**",
        "- Filename as deciding factor: **OFF**",
        "",
        "## Observation contract",
        "Document-derived information is recorded first. Existing structural and artifact identity is retained as contextual evidence for downstream engines; unresolved information remains unresolved.",
        "",
        "## Inventory",
    ]
    for record in records:
        doc = record["document"]
        md.append(
            f"- `{record['path']}` — subject=`{doc['subject'] or 'UNRESOLVED'}`, domain=`{doc['domain'] or 'UNRESOLVED'}`, cultural_scope=`{doc['cultural_scope'] or 'UNRESOLVED'}`, authority=`{doc['authority'] or 'UNRESOLVED'}`, artifact_role=`{record['artifact_role']}`"
        )
    (out / "CORE_CORPUS_OBSERVER.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"CORE observer: {len(records)} source documents observed; source mutation OFF.")


if __name__ == "__main__":
    main()
