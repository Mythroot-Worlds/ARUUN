#!/usr/bin/env python3
"""VARIANT arbitration for Mythroot CORE.

VARIANT is a narrow relationship: two artifacts perform essentially the same
informational job and express substantially the same underlying claims. Wording,
presentation, formatting, and modest added/omitted detail may differ.

Subject similarity alone can never produce VARIANT.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Iterable

REQUIRED_GATES = ("subject", "scope", "time", "purpose", "role", "claims")

@dataclass
class VariantAssessment:
    eligible: bool
    descriptor: str
    gates: dict[str, bool]
    reasons: list[str]
    claim_overlap: float
    informational_equivalence: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

def _norm(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, (list, tuple, set)):
        return "|".join(sorted(str(x).strip().lower() for x in v))
    return str(v).strip().lower()

def _same(a: Any, b: Any) -> bool:
    na, nb = _norm(a), _norm(b)
    return na is not None and nb is not None and na == nb

def _claim_key(c: Any) -> str:
    if isinstance(c, str):
        return c.strip().lower()
    if isinstance(c, dict):
        return "|".join(_norm(c.get(k)) or "" for k in ("subject", "verb", "object", "scope", "time"))
    return str(c).strip().lower()

def claim_overlap(claims_a: Iterable[Any], claims_b: Iterable[Any]) -> float:
    a = {_claim_key(x) for x in claims_a if _claim_key(x)}
    b = {_claim_key(x) for x in claims_b if _claim_key(x)}
    if not a or not b:
        return 0.0
    return len(a & b) / max(len(a), len(b))

def assess_variant(a: dict[str, Any], b: dict[str, Any], min_claim_overlap: float = 0.75) -> VariantAssessment:
    gates = {
        "subject": _same(a.get("subject"), b.get("subject")),
        "scope": _same(a.get("scope"), b.get("scope")),
        "time": _same(a.get("time"), b.get("time")),
        "purpose": _same(a.get("purpose"), b.get("purpose")),
        "role": _same(a.get("role"), b.get("role")),
        "claims": False,
    }
    overlap = claim_overlap(a.get("claims", []), b.get("claims", []))
    gates["claims"] = overlap >= min_claim_overlap
    reasons: list[str] = []
    for k, ok in gates.items():
        if not ok:
            reasons.append(f"variant_gate_failed:{k}")
    if not a.get("claims") or not b.get("claims"):
        reasons.append("missing_semantic_claims")
    if gates["subject"] and not gates["scope"]:
        reasons.append("same_subject_different_scope")
    if gates["subject"] and gates["scope"] and not gates["role"]:
        reasons.append("same_subject_scope_different_document_role")
    eligible = all(gates.values()) and not any(r in reasons for r in ("missing_semantic_claims",))
    # Informational equivalence is intentionally conservative: claim overlap is
    # the strongest signal; all structural gates must also agree.
    equivalence = overlap if eligible else min(overlap, 0.74)
    return VariantAssessment(
        eligible=eligible,
        descriptor="VARIANT" if eligible else "UNRESOLVED",
        gates=gates,
        reasons=reasons or ["same informational job and substantially equivalent claims"],
        claim_overlap=round(overlap, 4),
        informational_equivalence=round(equivalence, 4),
    )

def resolve_relationship(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Return a conservative relationship assessment.

    This function only resolves VARIANT eligibility. Other descriptors should be
    supplied by the broader semantic arbitration layer. If VARIANT is not proven,
    the caller receives UNRESOLVED rather than a forced legacy classification.
    """
    result = assess_variant(a, b)
    return result.as_dict()
