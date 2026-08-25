#!/usr/bin/env python3
"""CORE A.C.E. relationship synthesis.

Turns Robin's deciding-factor matrix into an auditable set of relationship
candidates. This is a reasoning layer, not automatic canon authority.
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
        "supports": {"subject": {"SAME", "MIXED"}, "scope": {"DIFFERENT", "MIXED"}, "coherence": {"SAME", "MIXED"}, "consequence": {"MIXED", "SAME"}},
        "blocks": {}, "disqualifiers": {},
        "description": "meaningfully connected material without a stronger defining relationship",
    },
    "SUPPORTING": {
        "required": {},
        "supports": {"function": {"SUPPORT"}, "dependency": {"SAME", "MIXED"}, "importance": {"MIXED"}},
        "blocks": {}, "disqualifiers": {},
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
        "description": "surface similarity without meaningful informational dependency or shared subject",
    },
    "REVIEW": {
        "required": {}, "supports": {}, "blocks": {}, "disqualifiers": {},
        "description": "evidence is insufficient or materially ambiguous for a safe automatic classification",
    },
}


def _state(robin, dimension):
    cell = robin.get(dimension) or {}
    return str(cell.get("relationship_state", "UNKNOWN")).upper()


def evaluate_relationships(robin_factor_investigation: dict) -> dict:
    """Evaluate all relationship models against Robin's matrix.

    Required/blocking/disqualifying factors are gates. Supporting factors add
    explanatory weight. No model can override a hard disqualifier.
    """
    candidates = []
    for label, model in RELATIONSHIP_MODELS.items():
        reasons = []
        blockers = []
        support = []
        for dim, expected in model.get("required", {}).items():
            observed = _state(robin_factor_investigation, dim)
            if observed == expected:
                reasons.append(f"required {dim}={observed}")
            else:
                blockers.append(f"required {dim}={expected}, observed {observed}")
        for dim, states in model.get("blocks", {}).items():
            observed = _state(robin_factor_investigation, dim)
            if observed in states:
                blockers.append(f"blocked by {dim}={observed}")
        for dim, states in model.get("disqualifiers", {}).items():
            observed = _state(robin_factor_investigation, dim)
            if observed in states:
                blockers.append(f"disqualified by {dim}={observed}")
        for dim, states in model.get("supports", {}).items():
            observed = _state(robin_factor_investigation, dim)
            if observed in states:
                support.append(f"{dim}={observed}")
        for dim, states in model.get("supports_difference", {}).items():
            observed = _state(robin_factor_investigation, dim)
            if observed in states:
                support.append(f"{dim}={observed} (meaningful contextual difference)")
        score = len(reasons) * 3 + len(support) - len(blockers) * 5
        status = "DISQUALIFIED" if blockers else "VIABLE"
        candidates.append({"relationship": label, "status": status, "score": score, "description": model["description"], "required_factors": reasons, "supporting_factors": support, "blocking_factors": blockers})
    candidates.sort(key=lambda x: (x["status"] == "VIABLE", x["score"]), reverse=True)
    viable = [c for c in candidates if c["status"] == "VIABLE"]
    if not viable or viable[0]["relationship"] == "REVIEW":
        decision = "REVIEW"
        confidence = "LOW"
    elif len(viable) == 1 or viable[0]["score"] >= viable[1]["score"] + 3:
        decision = viable[0]["relationship"]
        confidence = "HIGH" if viable[0]["score"] >= 4 else "MEDIUM"
    else:
        decision = "REVIEW"
        confidence = "MEDIUM"
    return {"decision": decision, "confidence": confidence, "decision_basis": "Robin factor matrix evaluated against explicit relationship gates and support factors; this layer does not alter canon.", "candidates": candidates, "viable_relationships": [c["relationship"] for c in viable], "unresolved_dimensions": [d for d in robin_factor_investigation if _state(robin_factor_investigation, d) == "UNKNOWN"]}
