#!/usr/bin/env python3
"""CORE Semantic Arbitration — context gate for relationship resolution.

This layer sits between semantic evidence discovery and final adjudication. It
makes document role, authority, scope, temporal context, and evidence explicit
before a relationship can be resolved. Legacy VARIANT remains readable for
historical/Core-gen1 reports but is not a valid final resolution here.

The module is deliberately deterministic and dependency-free so it can be used
by validators, CI, and human-review tooling without changing canon.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Optional

FINAL_RELATIONSHIPS = frozenset({
    "DUPLICATE", "SUPPORTING", "HISTORICAL", "CONFLICT", "MISPLACED",
    "RELATED", "COINCIDENTAL", "REVIEW", "UNRESOLVED",
})
LEGACY_RELATIONSHIPS = frozenset({"VARIANT"})
ROLES = frozenset({
    "AUTHORITATIVE", "REFERENCE", "SUPPORTING", "HISTORICAL", "WORKING",
    "TOOL", "ARCHIVE",
})

@dataclass(frozen=True)
class Evidence:
    """A single explicit observation supporting or weakening a decision."""
    kind: str
    statement: str
    source: str = ""
    weight: float = 1.0

@dataclass(frozen=True)
class Context:
    """Context that must be considered before relationship arbitration."""
    role: str = "UNKNOWN"
    authority: str = "UNKNOWN"
    scope: str = "UNKNOWN"
    temporal_state: str = "UNKNOWN"
    subject: str = "UNKNOWN"
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class Arbitration:
    status: str
    resolution: str
    descriptors: tuple[str, ...]
    reasons: tuple[str, ...]
    blockers: tuple[str, ...]


def _norm(value: object) -> str:
    return str(value or "UNKNOWN").strip().upper().replace("-", "_")


def _context(raw: Mapping[str, object]) -> Context:
    ev = []
    for item in raw.get("evidence", ()) or ():
        if isinstance(item, Evidence):
            ev.append(item)
        elif isinstance(item, Mapping):
            ev.append(Evidence(
                kind=_norm(item.get("kind")),
                statement=str(item.get("statement", "")),
                source=str(item.get("source", "")),
                weight=float(item.get("weight", 1.0)),
            ))
    return Context(
        role=_norm(raw.get("role")), authority=_norm(raw.get("authority")),
        scope=_norm(raw.get("scope")), temporal_state=_norm(raw.get("temporal_state")),
        subject=str(raw.get("subject", "UNKNOWN")), evidence=tuple(ev),
    )


def arbitrate(left: Mapping[str, object], right: Mapping[str, object],
              proposed: Optional[str] = None) -> Arbitration:
    """Resolve only when context/evidence supports a defensible final label.

    Multiple semantic descriptors may coexist. A legacy VARIANT proposal is
    converted into a contextual investigation rather than accepted as truth.
    """
    a, b = _context(left), _context(right)
    proposal = _norm(proposed)
    reasons: list[str] = []
    blockers: list[str] = []
    descriptors: list[str] = []

    if a.role not in ROLES or b.role not in ROLES:
        blockers.append("UNKNOWN_DOCUMENT_ROLE")
    if a.authority == "UNKNOWN" or b.authority == "UNKNOWN":
        blockers.append("UNKNOWN_AUTHORITY")
    if not a.evidence and not b.evidence:
        blockers.append("NO_EXPLICIT_EVIDENCE")

    if a.scope != b.scope and a.scope != "UNKNOWN" and b.scope != "UNKNOWN":
        descriptors.append("SCOPE_DIFFERENTIATED")
        reasons.append(f"scope differs: {a.scope} vs {b.scope}")

    if a.role != b.role:
        descriptors.append("ROLE_DIFFERENTIATED")
        reasons.append(f"document roles differ: {a.role} vs {b.role}")

    if a.authority != b.authority:
        descriptors.append("AUTHORITY_DIFFERENTIATED")
        reasons.append(f"authority differs: {a.authority} vs {b.authority}")

    if a.temporal_state != b.temporal_state and a.temporal_state != "UNKNOWN" and b.temporal_state != "UNKNOWN":
        descriptors.append("TEMPORALLY_DIFFERENTIATED")
        reasons.append(f"temporal state differs: {a.temporal_state} vs {b.temporal_state}")

    conflict = any(e.kind == "CONFLICT" for e in (*a.evidence, *b.evidence))
    support = any(e.kind in {"SUPPORT", "SUPPORTING", "CONTEXT", "REFERENCE"} for e in (*a.evidence, *b.evidence))
    same_subject = a.subject != "UNKNOWN" and a.subject == b.subject

    if conflict and same_subject and not blockers:
        descriptors.append("EXPLICIT_CONFLICT_EVIDENCE")
        reasons.append("explicit conflict evidence exists for the same subject")
        return Arbitration("RESOLVED", "CONFLICT", tuple(dict.fromkeys(descriptors)), tuple(reasons), tuple(blockers))

    if support and not blockers:
        descriptors.append("EVIDENCE_BACKED")
        reasons.append("explicit supporting/contextual evidence is present")
        if a.role == "AUTHORITATIVE" or b.role == "AUTHORITATIVE":
            descriptors.append("AUTHORITATIVE_CONTEXT")
        return Arbitration("RESOLVED", "SUPPORTING", tuple(dict.fromkeys(descriptors)), tuple(reasons), tuple(blockers))

    if same_subject and a.scope == b.scope and a.role == b.role and not blockers:
        descriptors.append("SAME_CONTEXT")
        reasons.append("same subject, scope, and document role")
        return Arbitration("RESOLVED", "DUPLICATE", tuple(dict.fromkeys(descriptors)), tuple(reasons), tuple(blockers))

    if proposal == "VARIANT":
        reasons.append("legacy VARIANT proposal is non-final and requires contextual resolution")
        descriptors.append("LEGACY_VARIANT_REJECTED")

    if blockers:
        return Arbitration("UNRESOLVED", "UNRESOLVED", tuple(dict.fromkeys(descriptors)), tuple(reasons), tuple(blockers))

    if descriptors:
        return Arbitration("REVIEW", "REVIEW", tuple(dict.fromkeys(descriptors)), tuple(reasons), tuple(blockers))
    return Arbitration("UNRESOLVED", "UNRESOLVED", tuple(), tuple(reasons), tuple(blockers))


def validate_final_resolution(label: str) -> bool:
    """Return False for legacy/non-final relationship labels."""
    return _norm(label) in FINAL_RELATIONSHIPS


def normalize_legacy_resolution(label: str) -> str:
    """Map legacy VARIANT to a review state without inventing a relationship."""
    return "REVIEW" if _norm(label) in LEGACY_RELATIONSHIPS else _norm(label)
