"""Shared identity/evidence gates for CORE VARIANT decisions.

The operational rule is structural identity first, semantic evidence second.
"""
from __future__ import annotations


def variant_scope_compatible(a: dict, b: dict) -> tuple[bool, str]:
    """Return whether two documents occupy the same resolved scope."""
    sa = a.get("scope") or a.get("region")
    sb = b.get("scope") or b.get("region")
    if not sa or not sb:
        return False, "scope_unresolved"
    if sa != sb:
        return False, "different_resolved_scope"
    return True, "same_resolved_scope"


def variant_identity_compatible(a: dict, b: dict) -> tuple[bool, list[str]]:
    """Check only authoritative VARIANT identity fields.

    Subject, scope and document type are hard identity gates. Role/purpose are
    compatibility signals and must not erase legitimate same-scope variants.
    """
    reasons: list[str] = []
    for key in ("subject", "content_type"):
        av, bv = a.get(key), b.get(key)
        if not av or not bv:
            reasons.append(f"{key}_unresolved")
        elif av != bv:
            reasons.append(f"different_{key}")
    ok, scope_reason = variant_scope_compatible(a, b)
    reasons.append(scope_reason)
    return not reasons or all(r == "same_resolved_scope" for r in reasons), reasons


def variant_information_compatible(a: dict, b: dict) -> tuple[bool, str]:
    """Require actual informational overlap; subject labels alone are insufficient."""
    subject_a = a.get("subject")
    subject_b = b.get("subject")
    if not subject_a or not subject_b:
        return False, "subject_unresolved"
    if subject_a != subject_b:
        return False, "different_subject"
    ta = a.get("document_type") or a.get("content_type")
    tb = b.get("document_type") or b.get("content_type")
    if ta and tb and ta != tb:
        return False, "different_document_type"
    overlap = a.get("informational_overlap", b.get("semantic_overlap", 0.0))
    try:
        overlap = float(overlap)
    except (TypeError, ValueError):
        overlap = 0.0
    if overlap < 0.80:
        return False, "insufficient_informational_overlap"
    return True, "same_information_with_wording_or_detail_difference"


def variant_gate(a: dict, b: dict) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    identity_ok, identity_reasons = variant_identity_compatible(a, b)
    reasons.extend(identity_reasons)
    if not identity_ok:
        return False, reasons
    ok, reason = variant_information_compatible(a, b)
    reasons.append(reason)
    return ok, reasons
