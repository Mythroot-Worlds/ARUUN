#!/usr/bin/env python3
"""CORE A.C.E. relationship synthesis.

Robin supplies the deciding-factor matrix. Batman uses this layer to determine
which unknowns actually matter to the case. An unknown supporting factor is
not allowed to force REVIEW; an unknown required/blocking/disqualifying factor
is a decisive unknown and can prevent a safe classification.
"""
from __future__ import annotations

RELATIONSHIP_MODELS = {
    "VARIANT": {
        "required": {"subject": "SAME"},
        "supports": {"function": {"SAME", "MIXED"}, "scale": {"SAME", "MIXED"}, "depth": {"SAME", "MIXED"}},
        "supports_difference": {"scope": {"DIFFERENT", "MIXED"}},
        "blocks": {"subject": {"DIFFERENT", "UNKNOWN"}},
        "disqualifiers": {"dependency": {"DIFFERENT"}, "provenance": {"DIFFERENT"}},
        "description": "same underlying subject expressed as a meaningful contextual or scoped variant",
    },
    "RELATED": {
        "required": {},
        "supports": {"subject": {"SAME", "MIXED", "DIFFERENT"}, "scope": {"DIFFERENT", "MIXED"}, "coherence": {"SAME", "MIXED"}, "consequence": {"MIXED", "SAME"}},
        "blocks": {}, "disqualifiers": {},
        "decisive": {"subject", "scope", "coherence", "dependency"},
        "description": "meaningfully connected material without a stronger defining relationship",
    },
    "SUPPORTING": {
        "required": {},
        "supports": {"function": {"SUPPORT"}, "dependency": {"SAME", "MIXED"}, "importance": {"MIXED"}},
        "blocks": {}, "disqualifiers": {},
        "decisive": {"function", "dependency", "provenance"},
        "description": "one artifact supplies context, evidence, reference, or operational support for another",
    },
    "HISTORICAL": {
        "required": {"subject": "SAME"},
        "supports": {"canon_status": {"MIXED", "DIFFERENT"}, "development_state": {"MIXED", "DIFFERENT"}, "function": {"MIXED", "DIFFERENT"}},
        "blocks": {"subject": {"DIFFERENT"}}, "disqualifiers": {},
        "description": "a temporal state, revision, or precedence relationship explains the difference",
    },
    "CONFLICT": {
        "required": {"subject": "SAME"},
        "supports": {"scope": {"SAME", "MIXED"}, "function": {"SAME", "MIXED"}, "canon_status": {"SAME", "MIXED"}},
        "blocks": {"subject": {"DIFFERENT", "UNKNOWN"}},
        "disqualifiers": {"scope": {"DIFFERENT"}},
        "description": "compatible context but substantively incompatible claims",
    },
    "MISPLACED": {
        "required": {},
        "supports": {"scope": {"DIFFERENT", "MIXED"}, "coherence": {"DIFFERENT"}, "function": {"DIFFERENT", "MIXED"}},
        "blocks": {}, "disqualifiers": {},
        "decisive": {"scope", "coherence", "function"},
        "description": "information appears in a location or document where its role or scope does not belong",
    },
    "DUPLICATE": {
        "required": {"subject": "SAME"},
        "supports": {"scope": {"SAME"}, "function": {"SAME"}, "scale": {"SAME"}, "depth": {"SAME"}},
        "blocks": {"subject": {"DIFFERENT", "UNKNOWN"}},
        "disqualifiers": {"scope": {"DIFFERENT"}, "function": {"DIFFERENT"}},
        "description": "substantially the same information with no meaningful contextual distinction",
    },
    "COINCIDENTAL": {
        "required": {},
        "supports": {"subject": {"DIFFERENT"}, "scope": {"DIFFERENT"}, "function": {"DIFFERENT"}},
        "blocks": {}, "disqualifiers": {},
        "decisive": {"subject", "scope", "function", "dependency"},
        "description": "surface similarity without meaningful informational dependency or shared subject",
    },
    "REVIEW": {
        "required": {}, "supports": {}, "blocks": {}, "disqualifiers": {}, "decisive": set(),
        "description": "evidence is insufficient or materially ambiguous for a safe automatic classification",
    },
}


def _state(robin, dimension):
    cell = robin.get(dimension) or {}
    return str(cell.get("relationship_state", "UNKNOWN")).upper()


def _decisive_dimensions(model):
    dims=set(model.get("decisive", set()))
    dims.update(model.get("required", {}).keys())
    dims.update(model.get("blocks", {}).keys())
    dims.update(model.get("disqualifiers", {}).keys())
    return dims


def evaluate_relationships(robin_factor_investigation: dict) -> dict:
    """Evaluate relationship models while separating decisive from incidental unknowns."""
    candidates=[]
    all_dimensions=set(robin_factor_investigation)
    for label,model in RELATIONSHIP_MODELS.items():
        reasons=[];blockers=[];support=[];decisive_unknown=[];non_decisive_unknown=[]
        decisive_dims=_decisive_dimensions(model)
        for dim,expected in model.get("required", {}).items():
            observed=_state(robin_factor_investigation,dim)
            if observed==expected: reasons.append(f"required {dim}={observed}")
            elif observed=="UNKNOWN": decisive_unknown.append(f"required {dim}={expected} is UNKNOWN")
            else: blockers.append(f"required {dim}={expected}, observed {observed}")
        for dim,states in model.get("blocks", {}).items():
            observed=_state(robin_factor_investigation,dim)
            if observed in states: blockers.append(f"blocked by {dim}={observed}")
            elif observed=="UNKNOWN" and dim in decisive_dims: decisive_unknown.append(f"blocking factor {dim} is UNKNOWN")
        for dim,states in model.get("disqualifiers", {}).items():
            observed=_state(robin_factor_investigation,dim)
            if observed in states: blockers.append(f"disqualified by {dim}={observed}")
            elif observed=="UNKNOWN" and dim in decisive_dims: decisive_unknown.append(f"disqualifier {dim} is UNKNOWN")
        for dim,states in model.get("supports", {}).items():
            observed=_state(robin_factor_investigation,dim)
            if observed in states: support.append(f"{dim}={observed}")
        for dim,states in model.get("supports_difference", {}).items():
            observed=_state(robin_factor_investigation,dim)
            if observed in states: support.append(f"{dim}={observed} (meaningful contextual difference)")
        for dim in all_dimensions:
            if _state(robin_factor_investigation,dim)=="UNKNOWN" and dim not in decisive_dims:
                non_decisive_unknown.append(dim)
        score=len(reasons)*3+len(support)-len(blockers)*5-len(decisive_unknown)*4
        status="DISQUALIFIED" if blockers else ("UNCERTAIN" if decisive_unknown else "VIABLE")
        candidates.append({"relationship":label,"status":status,"score":score,"description":model["description"],"required_factors":reasons,"supporting_factors":support,"blocking_factors":blockers,"decisive_dimensions":sorted(decisive_dims),"decisive_unknowns":sorted(decisive_unknown),"non_decisive_unknowns":sorted(non_decisive_unknown)})
    candidates.sort(key=lambda x:(x["status"]=="VIABLE",x["score"]),reverse=True)
    viable=[c for c in candidates if c["status"]=="VIABLE"]
    uncertain=[c for c in candidates if c["status"]=="UNCERTAIN"]
    if viable:
        best=viable[0];second=viable[1] if len(viable)>1 else None
        if second and best["score"] < second["score"]+3:
            decision="REVIEW";confidence="MEDIUM"
        else:
            decision=best["relationship"];confidence="HIGH" if best["score"]>=4 else "MEDIUM"
    elif uncertain:
        decision="REVIEW";confidence="LOW"
    else:
        decision="REVIEW";confidence="LOW"
    return {"decision":decision,"confidence":confidence,"decision_basis":"Robin factor matrix evaluated against relationship gates; only decisive unknowns block automatic classification; non-decisive unknowns remain visible but do not force REVIEW.","candidates":candidates,"viable_relationships":[c["relationship"] for c in viable],"uncertain_relationships":[c["relationship"] for c in uncertain],"decisive_unknowns":sorted({u for c in candidates for u in c["decisive_unknowns"]}),"non_decisive_unknowns":sorted({u for c in candidates for u in c["non_decisive_unknowns"]}),"unresolved_dimensions":sorted(d for d in all_dimensions if _state(robin_factor_investigation,d)=="UNKNOWN")}
