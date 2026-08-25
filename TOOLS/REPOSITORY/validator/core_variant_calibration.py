"""Small, shared calibration helpers for CORE VARIANT decisions.

This module keeps the operational definition in code so callers do not invent
relationship semantics independently.
"""

from __future__ import annotations


def variant_scope_compatible(a: dict, b: dict) -> tuple[bool, str]:
    """Return whether two resolved identities may be ordinary VARIANTs.

    Different resolved regions are never VARIANTs. Unknown scope is not an
    agreement; it is an unresolved identity condition and must be reviewed.
    """
    sa = a.get("scope") or a.get("region")
    sb = b.get("scope") or b.get("region")
    if not sa or not sb:
        return False, "scope_unresolved"
    if sa != sb:
        return False, "different_resolved_scope"
    return True, "same_resolved_scope"


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
    ok, reason = variant_scope_compatible(a, b)
    reasons.append(reason)
    if not ok:
        return False, reasons
    ok, reason = variant_information_compatible(a, b)
    reasons.append(reason)
    return ok, reasons
