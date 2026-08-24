#!/usr/bin/env python3
"""CORE semantic relationship vocabulary for Mythroot.

The library is deliberately descriptor-first: terms describe evidenced relations;
no single term is a forced classification. VARIANT is not a valid resolution.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

LIBRARY = {
  "SUPPORTING": {
    "color": "blue", "verb": ["supports", "substantiates", "corroborates", "reinforces"],
    "meaning": "B provides evidence or context that strengthens or explains A.",
    "conditions": ["B contributes evidence/context relevant to A", "the support is about the same claim or decision"],
    "examples": [
      "Lab results support a medical diagnosis.",
      "A cited court precedent supports a legal argument.",
      "A canonical regional framework supports interpretation of a regional entry."
    ],
    "counterexamples": ["Two documents merely mentioning the same topic.", "A later copy that adds no supporting evidence."],
    "near_misses": ["CORROBORATIVE", "DUPLICATE", "DERIVED"]
  },
  "HISTORICAL": {
    "color": "gold", "verb": ["precedes", "supersedes", "records", "replaces", "descends_from"],
    "meaning": "The relationship is explained by a change in time, version, or historical state.",
    "conditions": ["same or materially connected subject", "distinct temporal/version state"],
    "examples": ["A current city charter supersedes its 1820 predecessor.", "A product manual records an older hardware revision."],
    "counterexamples": ["Two unrelated documents that both contain dates."],
    "near_misses": ["CURRENT", "DUPLICATE", "CONFLICT"]
  },
  "CONFLICT": {
    "color": "red", "verb": ["contradicts", "disputes", "excludes", "incompatible_with"],
    "meaning": "Two claims cannot both be true under the same applicable scope, time, authority, and conditions.",
    "conditions": ["same subject", "same applicable scope/time", "claims are mutually incompatible"],
    "examples": ["The same store schedule says closed Sunday and open Sunday at noon for the same version.", "One canonical rule permits an action while another applicable canonical rule forbids it."],
    "counterexamples": ["Regional practices that differ intentionally.", "Historical versions with different rules."],
    "near_misses": ["DIFFERENT", "HISTORICAL", "SCOPE_SPECIALIZATION"]
  },
  "COMPLEMENTARY": {
    "color": "green", "verb": ["complements", "contextualizes", "extends", "elaborates"],
    "meaning": "Documents cover different dimensions of a larger subject and are more useful together.",
    "conditions": ["shared subject or dependency", "different information roles or dimensions", "no contradiction required"],
    "examples": ["Hardware specifications complement software architecture documentation.", "A world-wide framework complements a regional cultural entry."],
    "counterexamples": ["Two identical policy copies with no meaningful distinction."],
    "near_misses": ["SUPPORTING", "DERIVED", "DUPLICATE"]
  },
  "SCOPE_SPECIALIZATION": {
    "color": "purple", "verb": ["specializes", "narrows", "localizes", "implements"],
    "meaning": "B applies a broader concept at a narrower, local, organizational, or otherwise specialized scope.",
    "conditions": ["B has a narrower scope than A", "the narrower scope is intentional", "core subject remains connected"],
    "examples": ["A national tax framework is specialized by one state's implementation rules.", "A continent-wide cultural framework is specialized by a regional entry."],
    "counterexamples": ["Two documents covering unrelated subjects."],
    "near_misses": ["CONFLICT", "COMPLEMENTARY", "DUPLICATE"]
  },
  "DUPLICATE": {
    "color": "gray", "verb": ["duplicates", "copies", "repeats"],
    "meaning": "Two artifacts have substantially the same subject, role, scope, and substantive content without a meaningful reason to coexist.",
    "conditions": ["same intended role", "same applicable scope", "substantive equivalence", "no meaningful lifecycle distinction"],
    "examples": ["Two copies of the same policy with identical version and scope."],
    "counterexamples": ["Regional entries that intentionally share a category but differ by region."],
    "near_misses": ["COMPLEMENTARY", "HISTORICAL", "DERIVED"]
  },
  "DERIVED": {
    "color": "teal", "verb": ["derives_from", "summarizes", "aggregates", "compiles"],
    "meaning": "B is constructed from or summarizes information from A or multiple source artifacts.",
    "conditions": ["provenance points to source material", "B has a distinct synthesis/reference role"],
    "examples": ["A quarterly report aggregates individual department reports.", "A comparative cultural sheet derives from regional entries."],
    "counterexamples": ["Two independent documents that merely discuss the same topic."],
    "near_misses": ["SUPPORTING", "DUPLICATE", "COMPLEMENTARY"]
  },
  "CORROBORATIVE": {
    "color": "cyan", "verb": ["corroborates", "confirms", "independently_attests"],
    "meaning": "B independently provides evidence consistent with a claim in A without merely being a derivative or duplicate.",
    "conditions": ["independent source/provenance", "same claim or compatible claim", "evidence is materially relevant"],
    "examples": ["An independent audit confirms a financial figure.", "A second independent archival source confirms an event."],
    "counterexamples": ["A copied document repeating the same claim."],
    "near_misses": ["SUPPORTING", "DUPLICATE", "DERIVED"]
  },
}

CLAIM_FIELDS = ["subject", "verb", "object", "modifiers", "scope", "time", "authority", "context", "source"]
FORBIDDEN_RESOLUTION = {"VARIANT"}

def build_library_report(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    report = {"engine":"CORE Semantic Relationship Library", "schema_version":"1.0", "descriptors":LIBRARY,
              "claim_fields":CLAIM_FIELDS, "forbidden_final_resolutions":sorted(FORBIDDEN_RESOLUTION),
              "principles":["descriptors may co-occur","similarity is not a relationship","difference is not a conflict","unresolved means evidence is insufficient"],
              "safety":{"read_only":True,"automatic_canon_change":False,"automatic_rule_promotion":False}}
    (out/"CORE_SEMANTIC_LIBRARY.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    md=["# CORE Semantic Relationship Library","","Descriptors are evidence-based relationship language, not forced single classes.","","| Color | Identifier | Meaning |","|---|---|---|"]
    colors={v['color'] for v in LIBRARY.values()}
    for k,v in LIBRARY.items(): md.append(f"| {v['color']} | **{k}** | {v['meaning']} |")
    md += ["","## Claim model","","`entity + verb + object + modifiers + scope + time + authority + context + source`","","## Rule","","**VARIANT is not a final resolution.** If evidence does not establish a more specific relationship, the case remains **UNRESOLVED** with a missing-evidence reason."]
    (out/"CORE_SEMANTIC_LIBRARY.md").write_text('\n'.join(md)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS'); a=ap.parse_args(); build_library_report(Path(a.out))
    print(f"CORE semantic library: {len(LIBRARY)} descriptors, {len(CLAIM_FIELDS)} claim fields.")
if __name__=='__main__': main()
