#!/usr/bin/env python3
"""CORE artifact-aware identity adapter.

Keeps the existing structural identity resolver stable while adding the
artifact-role dimension required to distinguish world sources, references,
tools, audits, archives, and other repository artifacts.
"""
from __future__ import annotations
from pathlib import Path
from core_artifact_roles import infer_artifact_role
from core_identity_resolver import resolve_identity as resolve_structural_identity


def resolve_identity(root, rel):
    identity = resolve_structural_identity(root, rel)
    path = Path(rel)
    role = infer_artifact_role(
        layer=identity.get("layer"),
        authority=identity.get("authority"),
        path=rel,
        status=identity.get("status"),
    )
    return {**identity, "artifact_role": role}


def identity_match(left, right):
    reasons=[]
    keys=(
        ("entity","entity"),
        ("population","population"),
        ("region","region"),
        ("subregion","subregion"),
        ("subject","subject"),
        ("role","document role"),
        ("purpose","purpose"),
        ("artifact_role","artifact role"),
    )
    for key,label in keys:
        a,b=left.get(key),right.get(key)
        if a is not None and b is not None and a!=b:
            reasons.append(f"{label} mismatch: {a} != {b}")
    if left.get("region") and right.get("region") and left["region"]!=right["region"]:
        reasons.append("regional scope mismatch")
    return (not reasons, reasons)
