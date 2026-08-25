#!/usr/bin/env python3
"""Evidence-gated VARIANT arbitration for Mythroot CORE.

VARIANT means the same canonical family within the same regional/scope identity
and same document type, with substantially overlapping information. Role/purpose
are compatibility signals rather than hard identity requirements.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Iterable
import re

_STOP={"the","and","that","with","from","this","their","they","are","for","into","have","has","its","was","were","been","being","than","then","only","also","often","typically","generally"}
@dataclass
class VariantAssessment:
    eligible: bool; descriptor: str; gates: dict[str,bool]; reasons: list[str]; claim_overlap: float; informational_equivalence: float; comparison_basis: str="semantic_claims"
    def as_dict(self): return asdict(self)
def _norm(v):
    if v is None:return None
    if isinstance(v,(list,tuple,set)):return "|".join(sorted(str(x).strip().lower() for x in v))
    return str(v).strip().lower()
def _same(a,b):
    na,nb=_norm(a),_norm(b);return na is not None and nb is not None and na==nb
def _same_or_unspecified(a,b):
    na,nb=_norm(a),_norm(b)
    if na is None and nb is None:return True
    if na is None or nb is None:return False
    return na==nb
def _tokens(text):return {x for x in re.findall(r"[a-z0-9']+",text.lower()) if len(x)>2 and x not in _STOP}
def _claim_key(c):
    if isinstance(c,str):return c.strip().lower()
    if isinstance(c,dict):
        if c.get("text") or c.get("normalized"):return _norm(c.get("normalized") or c.get("text")) or ""
        return "|".join(_norm(c.get(k)) or "" for k in ("subject","verb","object","scope","time"))
    return str(c).strip().lower()
def claim_overlap(claims_a:Iterable[Any],claims_b:Iterable[Any])->float:
    a={_claim_key(x) for x in claims_a if _claim_key(x)};b={_claim_key(x) for x in claims_b if _claim_key(x)}
    if not a or not b:return 0.0
    exact=len(a&b)/max(len(a),len(b))
    if exact>=.75:return exact
    def best(x,other):
        xt=_tokens(x);return max((len(xt&_tokens(y))/len(xt|_tokens(y)) for y in other if xt and _tokens(y)),default=0.0)
    semantic=(sum(best(x,b) for x in a)/len(a)+sum(best(y,a) for y in b)/len(b))/2
    return round(max(exact,semantic),4)
def _claims_from_units(units):return [u.get("normalized") or u.get("text") or u for u in units if isinstance(u,dict)]

def assess_variant(a:dict[str,Any],b:dict[str,Any],min_claim_overlap=.65):
    claims_a=a.get("claims") or _claims_from_units(a.get("information_units",[]));claims_b=b.get("claims") or _claims_from_units(b.get("information_units",[]))
    family_a=a.get("canonical_family_id");family_b=b.get("canonical_family_id")
    family_gate=_same(family_a,family_b) if family_a is not None and family_b is not None else _same(a.get("subject"),b.get("subject"))
    gates={"canonical_family":family_gate,"subject":_same(a.get("subject"),b.get("subject")),"scope":_same(a.get("scope"),b.get("scope")),"content_type":_same(a.get("content_type"),b.get("content_type")),"time":_same_or_unspecified(a.get("time"),b.get("time")),"claims":False}
    overlap=claim_overlap(claims_a,claims_b);gates["claims"]=overlap>=min_claim_overlap
    reasons=[]
    for k,ok in gates.items():
        if not ok:reasons.append(f"variant_gate_failed:{k}")
    ra,rb=_norm(a.get("role")),_norm(b.get("role"));pa,pb=_norm(a.get("purpose")),_norm(b.get("purpose"))
    if {ra,rb} & {"historical","audit_support"} and ra!=rb:reasons.append("incompatible_document_role")
    if {pa,pb} & {"audit_support","historical"} and pa!=pb:reasons.append("incompatible_document_purpose")
    compatible=not any(x in reasons for x in ("incompatible_document_role","incompatible_document_purpose"))
    eligible=all(gates.values()) and compatible and bool(claims_a) and bool(claims_b)
    if gates["subject"] and not gates["scope"]:reasons.append("same_subject_different_scope")
    basis="semantic_claims" if a.get("claims") and b.get("claims") else "information_units"
    return VariantAssessment(eligible,"VARIANT" if eligible else "UNRESOLVED",gates,reasons or ["same canonical family, same subject, same scope, same document type, and substantially equivalent information"],round(overlap,4),round(overlap,4),basis)
def resolve_relationship(a,b):return assess_variant(a,b).as_dict()
