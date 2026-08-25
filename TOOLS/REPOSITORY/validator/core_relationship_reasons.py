#!/usr/bin/env python3
"""CORE human-readable relationship-reason translation.

Historical benchmark outputs use machine-oriented gate reasons. This adapter
translates those reasons into explicit deciding-factor language without changing
the underlying label or treating the historical benchmark as a current resolver.
"""
from __future__ import annotations

REASON_TRANSLATIONS = {
    "variant_gate_failed:subject": "The compared artifacts do not establish the same underlying subject.",
    "variant_gate_failed:scope": "The compared artifacts operate at different scopes.",
    "variant_gate_failed:time": "The applicable time state is different or explicitly unresolved.",
    "variant_gate_failed:purpose": "The artifacts perform different informational purposes.",
    "variant_gate_failed:role": "The artifacts have different document roles.",
    "variant_gate_failed:claims": "The available information does not establish sufficient substantive claim equivalence.",
    "same_subject_different_scope": "Same subject is insufficient because scope is a deciding factor and differs.",
    "same_subject_scope_different_document_role": "Same subject and scope are insufficient because the document roles differ.",
    "missing_information_evidence": "There is not enough information evidence to establish equivalence.",
    "time_unspecified_in_both_documents": "Time is unspecified in both artifacts; the benchmark records this as unresolved context rather than inventing a temporal match.",
}


def explain_reason(reason: str) -> str:
    return REASON_TRANSLATIONS.get(reason, reason.replace("_", " ").capitalize())


def explain_reasons(reasons):
    return [explain_reason(r) for r in reasons]


def historical_variant_explanation(assessment: dict):
    """Return a translated explanation while preserving benchmark provenance."""
    return {
        "source": "historical_variant_benchmark",
        "label": assessment.get("descriptor", "UNRESOLVED"),
        "reasons": explain_reasons(assessment.get("reasons", [])),
        "claim_overlap": assessment.get("claim_overlap", 0.0),
        "informational_equivalence": assessment.get("informational_equivalence", 0.0),
        "current_resolution_authority": "human_adjudication",
        "warning": "Historical VARIANT benchmark output is evidence for calibration only; it is not a current canon or relationship decision.",
    }
