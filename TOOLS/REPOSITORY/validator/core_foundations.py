#!/usr/bin/env python3
"""CORE foundational ontology: deciding factors behind document meaning."""
from __future__ import annotations
import re

DIMENSIONS = {
    "subject": ("what is being described", ()),
    "scope": ("how broadly or narrowly the information applies", ("CONTINENT", "CONTINENTAL", "HEARTH-WIDE", "REGIONAL", "REGION", "MOUNTAIN", "RIVER", "PLAINS", "SETTLEMENT", "VILLAGE", "LOCAL", "WETLANDS", "DESERT", "COAST")),
    "scale": ("the level at which the subject operates", ("PERSONAL", "LOCAL", "REGIONAL", "NATIONAL", "POLITICAL", "GLOBAL", "COSMIC")),
    "function": ("why the document or information exists", ("FAMILY", "BIRTH", "CHILDHOOD", "GOVERNANCE", "AUTHORITY", "LEADERSHIP", "SPECIALIST", "LINEAGE", "SUPPORT", "CHECKLIST", "AUDIT", "REFERENCE", "HISTORICAL", "ARCHIVE", "REVISION")),
    "depth": ("how deeply the subject is developed", ("LEVEL 0", "LEVEL 1", "LEVEL 2", "LEVEL 3", "LEVEL 4", "FOUNDATION", "FUNCTIONAL", "DEVELOPED", "DEEP")),
    "canon_status": ("whether information is established, flexible, open, or unknown", ("HARD CANON", "FLEXIBLE CANON", "OPEN", "UNKNOWN", "CANON")),
    "importance": ("how much the information matters to the world", ("CORE", "SUPPORTING", "OPTIONAL")),
    "development_state": ("whether an area is developed or intentionally unfinished", ("DEVELOPED", "PARTIAL", "OPEN", "N/A")),
    "relationship": ("how two information objects relate", ("RELATED", "VARIANT", "SUPPORTING", "HISTORICAL", "CONFLICT", "MISPLACED", "DUPLICATE", "COINCIDENTAL", "REVIEW")),
    "dependency": ("what other information this material relies upon", ("BASED ON", "BUILDS ON", "DERIVED FROM", "REFERENCES", "INFORMS")),
    "consequence": ("what other world systems this information affects", ("AFFECTS", "INFLUENCES", "CONSEQUENCE", "IMPACTS")),
    "provenance": ("where the information originated", ("SOURCE", "PROVENANCE", "AUTHOR", "VERSION", "LAST REVIEWED")),
    "intentionality": ("whether absence is deliberate", ("INTENTIONALLY OPEN", "DELIBERATELY OPEN", "CREATOR-EXPANDABLE", "UNEXPLORED", "WITHHELD")),
    "coherence": ("whether the element connects logically to surrounding systems", ("GEOGRAPHY", "SETTLEMENT", "ECONOMY", "POLITICS", "LAW", "HISTORY", "CULTURE", "DAILY LIFE", "ECOLOGY")),
    "usability": ("whether another creator can understand and use it", ("USABILITY", "CREATOR-READY", "LICENSE-READY", "WORLD USAGE GUIDE")),
    "story_relevance": ("whether the information generates creative consequences", ("STORY", "CONFLICT", "MYSTERY", "STORY OPPORTUNITY", "NARRATIVE", "STORY GENERATION")),
}

# VARIANT is intentionally narrow: same underlying information AND same scope,
# with wording/detail differences. Same subject across different regions is RELATED.
RELATIONSHIP_FACTORS = {
    "VARIANT": {"same_subject": True, "same_scope": True, "functional_continuity": True, "distinguishing": "same underlying information and scope expressed with wording/detail differences"},
    "SUPPORTING": {"support_function": True, "dependency_signal": True, "distinguishing": "one information object supplies context, evidence, reference, or operational support for another"},
    "HISTORICAL": {"same_subject": True, "temporal_difference": True, "functional_continuity": True, "distinguishing": "temporal state, revision, or precedence explains the relationship"},
    "CONFLICT": {"same_subject": True, "same_scope": True, "functional_continuity": True, "incompatible_claims": True, "distinguishing": "same subject and scope but substantively incompatible claims"},
    "MISPLACED": {"scope_mismatch": True, "location_function_mismatch": True, "distinguishing": "information appears in a location or document where it does not belong"},
    "DUPLICATE": {"same_subject": True, "same_scope": True, "functional_continuity": True, "distinguishing": "substantially the same information with no meaningful contextual distinction"},
    "RELATED": {"meaningful_connection": True, "distinguishing": "meaningfully connected subject matter without a stronger defining relationship"},
}

def hits(text: str):
    u = text.upper()
    return {k: sorted({term for term in terms if re.search(r"\b" + re.escape(term) + r"\b", u)}) for k, (_, terms) in DIMENSIONS.items()}

def factor_snapshot(left_text: str, right_text: str):
    a, b = hits(left_text), hits(right_text)
    return {"dimensions": {k: {"a": a[k], "b": b[k], "shared": sorted(set(a[k]) & set(b[k])), "different": sorted(set(a[k]) ^ set(b[k]))} for k in DIMENSIONS}, "principle": "A deciding factor must explain the relationship; a shared word is evidence only when it supports a meaningful dimension."}

def relationship_test(label: str, factors: dict):
    rule = RELATIONSHIP_FACTORS.get(label, {})
    return {"relationship": label, "expected_factors": rule, "observed_factors": factors, "decision_basis": rule.get("distinguishing", "requires human adjudication"), "status": "candidate" if rule else "unknown_relationship"}
