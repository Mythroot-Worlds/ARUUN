#!/usr/bin/env python3
"""Evidence-gated VARIANT arbitration for Mythroot CORE.

VARIANT is narrow: two artifacts perform essentially the same informational job
and express substantially the same underlying information. Wording, presentation,
formatting, and modest added/omitted detail may differ. Subject similarity alone
never produces VARIANT.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Iterable
import re

REQUIRED_GATES = ("subject", "scope", "time", "purpose", "role", "claims")
_STOP = {"the","and","that","with","from","this","their","they","are","for","into","have","has","its","was","were","been","being","than","then","only","also","often","typically","generally"}

@dataclass
class VariantAssessment:
    eligible: bool
    descriptor: str
    gates: dict[str, bool]
    reasons: list[str]
    claim_overlap: float
    informational_equivalence: float
    comparison_basis: str = "semantic_claims"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

def _norm(v: Any) -> str | None:
    if v is None: return None
    if isinstance(v, (list, tuple, set)): return "|".join(sorted(str(x).strip().lower() for x in v))
    return str(v).strip().lower()

def _same(a: Any, b: Any) -> bool:
    na, nb = _norm(a), _norm(b)
    return na is not None and nb is not None and na == nb

def _tokens(text: str) -> set[str]:
    return {x for x in re.findall(r"[a-z0-9']+", text.lower()) if len(x) > 2 and x not in _STOP}

def _claim_key(c: Any) -> str:
    if isinstance(c, str): return c.strip().lower()
    if isinstance(c, dict):
        if c.get("text") or c.get("normalized"): return _norm(c.get("normalized") or c.get("text")) or ""
        return "|".join(_norm(c.get(k)) or "" for k in ("subject","verb","object","scope","time"))
    return str(c).strip().lower()

def claim_overlap(claims_a: Iterable[Any], claims_b: Iterable[Any]) -> float:
    """Compare semantic claims, falling back to conservative information-unit similarity."""
    a = {_claim_key(x) for x in claims_a if _claim_key(x)}; b = {_claim_key(x) for x in claims_b if _claim_key(x)}
    if not a or not b: return 0.0
    # Exact normalized claims remain strongest evidence.
    exact = len(a & b) / max(len(a), len(b))
    if exact >= 0.75: return exact
    # Information units are prose evidence. Use bidirectional best-match Jaccard,
    # which tolerates wording changes while requiring substantive token overlap.
    def best(x, other):
        xt = _tokens(x); best_score = 0.0
        for y in other:
            yt = _tokens(y)
            if not xt or not yt: continue
            best_score = max(best_score, len(xt & yt) / len(xt | yt))
        return best_score
    semantic = (sum(best(x,b) for x in a)/len(a) + sum(best(y,a) for y in b)/len(b)) / 2
    return round(max(exact, semantic), 4)

def _claims_from_units(units: Iterable[Any]) -> list[Any]:
    out=[]
    for u in units:
        if isinstance(u, dict): out.append(u.get("normalized") or u.get("text") or u)
        else: out.append(u)
    return out

def assess_variant(a: dict[str, Any], b: dict[str, Any], min_claim_overlap: float = 0.75) -> VariantAssessment:
    claims_a = a.get("claims") or _claims_from_units(a.get("information_units", []))
    claims_b = b.get("claims") or _claims_from_units(b.get("information_units", []))
    gates = {"subject": _same(a.get("subject"), b.get("subject")),"scope": _same(a.get("scope"), b.get("scope")),"time": _same(a.get("time"), b.get("time")),"purpose": _same(a.get("purpose"), b.get("purpose")),"role": _same(a.get("role"), b.get("role")),"claims": False}
    overlap = claim_overlap(claims_a, claims_b); gates["claims"] = overlap >= min_claim_overlap
    reasons=[]
    for k,ok in gates.items():
        if not ok: reasons.append(f"variant_gate_failed:{k}")
    if not claims_a or not claims_b: reasons.append("missing_information_evidence")
    if gates["subject"] and not gates["scope"]: reasons.append("same_subject_different_scope")
    if gates["subject"] and gates["scope"] and not gates["role"]: reasons.append("same_subject_scope_different_document_role")
    eligible=all(gates.values()) and bool(claims_a) and bool(claims_b)
    basis="semantic_claims" if a.get("claims") and b.get("claims") else "information_units"
    return VariantAssessment(eligible,"VARIANT" if eligible else "UNRESOLVED",gates,reasons or ["same informational job and substantially equivalent information"],round(overlap,4),round(overlap if eligible else min(overlap,.74),4),basis)

def resolve_relationship(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    return assess_variant(a,b).as_dict()
