#!/usr/bin/env python3
"""Lightweight pairwise semantic comparison for CORE/Robin.

This is deliberately dependency-free. It combines normalized lexical overlap,
small domain-neutral synonym families, section alignment, and bidirectional
coverage. It is a comparator/evidence producer, not a final adjudicator.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, asdict
from typing import Iterable, Any

STOP = {"the","and","that","with","from","this","their","they","are","for","into","have","has","its","was","were","been","being","than","then","only","also","often","typically","generally","through","about","very","more","most"}
SYNONYMS = {
    "children": "youth", "child": "youth", "young": "youth", "youngpeople": "youth",
    "families": "family", "households": "family", "household": "family",
    "learn": "teach", "learns": "teach", "learning": "teach", "taught": "teach",
    "rotate": "cycle", "rotates": "cycle", "rotation": "cycle", "rotating": "cycle",
    "community": "communal", "communities": "communal", "communal": "communal",
    "region": "regional", "regional": "regional",
    "village": "settlement", "villages": "settlement", "settlements": "settlement",
}

def tokens(text: str) -> set[str]:
    raw = re.findall(r"[a-z0-9]+", text.lower())
    return {SYNONYMS.get(x, x) for x in raw if len(x) > 2 and x not in STOP}

def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0

def best_coverage(units_a: list[dict], units_b: list[dict]) -> tuple[float, list[dict]]:
    if not units_a or not units_b:
        return 0.0, []
    align=[]
    for a in units_a:
        at=tokens(a.get("text", ""))
        best=(0.0,None)
        for b in units_b:
            bt=tokens(b.get("text", ""))
            score=jaccard(at,bt)
            if (a.get("section") or "").strip().lower() == (b.get("section") or "").strip().lower() and a.get("section"):
                score=min(1.0,score+0.10)
            if score > best[0]: best=(score,b)
        if best[1] is not None:
            align.append({"a":a.get("text",""),"b":best[1].get("text",""),"score":round(best[0],4),"same_section":bool((a.get("section") or "").strip().lower()==(best[1].get("section") or "").strip().lower() and a.get("section"))})
    return (sum(x["score"] for x in align)/len(align) if align else 0.0), align

@dataclass
class Comparison:
    score: float
    a_to_b: float
    b_to_a: float
    same_information: bool
    contradiction_signal: bool
    unmatched_a: int
    unmatched_b: int
    alignments: list[dict]
    explanation: list[str]

    def as_dict(self): return asdict(self)

def compare_units(units_a: Iterable[dict], units_b: Iterable[dict], threshold: float = 0.72) -> Comparison:
    a=list(units_a); b=list(units_b)
    a_to_b, ab=best_coverage(a,b); b_to_a, ba=best_coverage(b,a)
    score=round((a_to_b+b_to_a)/2,4)
    unmatched_a=sum(1 for x in ab if x["score"] < threshold)
    unmatched_b=sum(1 for x in ba if x["score"] < threshold)
    # A simple polarity check prevents obvious opposite statements from being
    # treated as equivalent. This remains a signal for later arbitration.
    polarity_a={"not","never","no","without","cannot"}&tokens(" ".join(x.get("text","") for x in a))
    polarity_b={"not","never","no","without","cannot"}&tokens(" ".join(x.get("text","") for x in b))
    contradiction_signal=bool(polarity_a != polarity_b and score >= threshold)
    same=score >= threshold and a_to_b >= threshold and b_to_a >= threshold and not contradiction_signal
    explanation=[]
    if same: explanation.append("bidirectional information coverage is above threshold")
    if a_to_b >= threshold: explanation.append("A is substantially covered by B")
    else: explanation.append("B does not fully cover A")
    if b_to_a >= threshold: explanation.append("B is substantially covered by A")
    else: explanation.append("A does not fully cover B")
    if contradiction_signal: explanation.append("polarity mismatch requires contradiction review")
    return Comparison(score,round(a_to_b,4),round(b_to_a,4),same,contradiction_signal,unmatched_a,unmatched_b,ab+ba,explanation)
