#!/usr/bin/env python3
"""CORE canonical-family identity layer.

A canonical family identifies the enduring subject lineage behind related
regional, supporting, revision, or historical documents. It is deliberately
structural: it does not merge content, decide canon, or infer lore.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from core_document_identity import identify

ALIASES = {
    "family_birth_childhood": ("birth", "childhood"),
    "family_partnership": ("partnership", "marriage"),
    "governance_authority": ("governance", "authority"),
    "food_subsistence": ("food", "subsistence"),
    "settlement_housing": ("settlement", "housing"),
}

def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")

def family_key(path: str, identity: dict | None = None) -> tuple[str | None, str]:
    """Return stable family key and evidence basis without semantic guessing."""
    ident = identity or identify(path)
    subject = normalize(ident.get("subject") or "")
    if subject:
        for key, terms in ALIASES.items():
            if subject == key or all(term in subject for term in terms):
                return key, "STRUCTURAL_SUBJECT_ALIAS"
        return subject, "STRUCTURAL_SUBJECT"
    stem = normalize(Path(path).stem)
    for key, terms in ALIASES.items():
        if all(term in stem for term in terms):
            return key, "FILENAME_TERMS"
    return None, "UNRESOLVED"

def canonical_family_id(family_key_value: str, content_type: str) -> str:
    digest = hashlib.sha1(f"{content_type}:{family_key_value}".encode()).hexdigest()[:12]
    return f"FAM-{digest}"

def resolve(path: str, identity: dict | None = None) -> dict:
    ident = identity or identify(path)
    key, basis = family_key(path, ident)
    family_id = canonical_family_id(key, ident.get("content_type", "UNKNOWN")) if key else None
    scope = ident.get("scope") or {}
    region = scope.get("region")
    if region:
        relation_to_family = "REGIONAL_SPECIALIZATION"
    elif ident.get("role") == "SUPPORTING":
        relation_to_family = "SUPPORTING_ARTIFACT"
    elif ident.get("role") == "HISTORICAL":
        relation_to_family = "HISTORICAL_ARTIFACT"
    else:
        relation_to_family = "FAMILY_ROOT_OR_UNSCOPED"
    return {
        "canonical_family_id": family_id,
        "canonical_family_key": key,
        "canonical_family_basis": basis,
        "canonical_domain": ident.get("content_type"),
        "scope": scope,
        "relation_to_family": relation_to_family,
        "identity": ident,
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    args = ap.parse_args()
    rows = [resolve(p) for p in args.paths]
    print(json.dumps({"engine": "CORE Canonical Family", "schema_version": "1.0", "mode": "READ_ONLY", "documents": rows, "safety": {"automatic_merge": False, "automatic_canon_change": False, "human_validation_required": True}}, indent=2))

if __name__ == "__main__":
    main()
