#!/usr/bin/env python3
"""CORE artifact-role ontology.

Artifact role describes what an information artifact *is for* in the repository;
it is deliberately distinct from world subject, scope, authority, and status.
The ontology is descriptive and read-only: it never promotes a document to canon.
"""
from __future__ import annotations

ARTIFACT_ROLES = {
    "WORLD_SOURCE": {
        "description": "authoritative built-world source describing what exists",
        "layers": {"world"},
        "authorities": {"world", "regional", "continental"},
    },
    "OVERVIEW": {
        "description": "compiled orientation or summary of deeper world material",
        "layers": {"world", "reference"},
        "authorities": {"reference", "world", "continental", "regional"},
    },
    "REFERENCE": {
        "description": "derived navigation or comparative reference material",
        "layers": {"reference"},
        "authorities": {"reference"},
    },
    "TOOL": {
        "description": "methodology or machinery used to build, validate, or generate material",
        "layers": {"tool"},
        "authorities": {"tool"},
    },
    "AUDIT": {
        "description": "diagnostic, discrepancy, validation, or QA artifact",
        "layers": {"audit"},
        "authorities": {"audit"},
    },
    "ARCHIVE": {
        "description": "historical or superseded development material",
        "layers": {"archive"},
        "authorities": {"historical"},
    },
    "RELEASE": {
        "description": "controlled packaged distribution artifact",
        "layers": {"release"},
        "authorities": {"reference", "world", "tool"},
    },
    "SUPPORTING": {
        "description": "supporting material that informs another artifact without being its source of truth",
        "layers": {"world", "reference", "audit", "tool"},
        "authorities": {"supporting"},
    },
}


def normalize(value):
    if value is None:
        return None
    return str(value).strip().lower()


def infer_artifact_role(*, layer=None, authority=None, path=None, status=None):
    """Infer a conservative artifact role from explicit metadata, then path.

    Explicit layer/authority wins. Path is only a fallback. Unknown remains
    UNKNOWN rather than being guessed from document prose.
    """
    layer_n = normalize(layer)
    authority_n = normalize(authority)
    path_n = normalize(path) or ""

    if layer_n == "archive" or "07_archive/" in path_n:
        return "ARCHIVE"
    if layer_n == "audit" or "/reports/" in path_n or "audit" in path_n:
        return "AUDIT"
    if layer_n == "tool" or "/tools/" in path_n:
        return "TOOL"
    if layer_n == "release" or "/release" in path_n:
        return "RELEASE"
    if authority_n == "supporting":
        return "SUPPORTING"
    if authority_n == "reference" or layer_n == "reference":
        return "REFERENCE"
    if layer_n == "world" and authority_n in {"world", "regional", "continental"}:
        return "WORLD_SOURCE"
    if layer_n == "world" and authority_n == "reference":
        return "OVERVIEW"
    if "world_bible" in path_n or "overview" in path_n:
        return "OVERVIEW"
    if layer_n or authority_n or status:
        return "UNKNOWN"
    return "UNKNOWN"


def role_compatibility(left: str | None, right: str | None):
    """Return whether two artifacts can be treated as the same artifact role."""
    a, b = normalize(left), normalize(right)
    if not a or not b:
        return {"same_role": False, "known": False, "reason": "artifact_role_unspecified"}
    same = a == b
    return {
        "same_role": same,
        "known": a.upper() in ARTIFACT_ROLES and b.upper() in ARTIFACT_ROLES,
        "reason": "same_artifact_role" if same else "different_artifact_roles",
    }
