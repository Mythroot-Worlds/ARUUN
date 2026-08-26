#!/usr/bin/env python3
"""Corrected relationship ontology calibration.

The historical blind annotations remain preserved as raw human choices. They are
not authoritative when they conflict with the now-defined layered ontology.
This calibration supplies explicit regression cases for VARIANT vs RELATED and
flags legacy cross-scope VARIANT labels for review rather than treating them as
training truth.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from core_layered_relationship import compare

CASES = (
    {
        "id": "variant_revision_same_context",
        "left": "07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/HEARTH_DESERT_PEOPLES_CULTURAL_BASE_v0.1.md",
        "right": "07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/HEARTH_DESERT_PEOPLES_CULTURAL_BASE_v0.2.md",
        "expected": "VARIANT",
        "reason": "same cultural base, same archive context, revision lineage",
    },
    {
        "id": "related_regional_siblings",
        "left": "03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md",
        "right": "03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md",
        "expected": "RELATED",
        "reason": "same conceptual subject, different regional context and information",
    },
    {
        "id": "related_broad_vs_regional",
        "left": "03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md",
        "right": "03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md",
        "expected": "RELATED",
        "reason": "broad Hearth framework versus Desert regional specialization",
    },
)

def read(root, path):
    p = root / path
    return p.read_text(encoding="utf-8") if p.exists() else ""

def load_json(path):
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("content"), str):
        return json.loads(data["content"])
    return data

def legacy_conflicts(annotations):
    flagged = []
    regions = {"DESERT", "RIVER", "COAST", "PLAINS", "MOUNTAINS", "WETLANDS"}
    for ann in annotations:
        choices = set(ann.get("raw_choices", []))
        if "VARIANT" not in choices:
            continue
        paths = (ann.get("left", "").upper(), ann.get("right", "").upper())
        found = [r for r in regions if any(re.search(rf"/{r}/", p) for p in paths)]
        if len(found) >= 2 and len(set(found)) >= 2:
            flagged.append({"left": ann.get("left"), "right": ann.get("right"), "raw_choices": ann.get("raw_choices", []), "reason": "legacy VARIANT label crosses distinct regional contexts; ontology requires RELATED unless evidence establishes same-context information identity"})
    return flagged

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    out = root / (sys.argv[2] if len(sys.argv) > 2 else "TOOLS/REPOSITORY/REPORTS")
    results = []
    failures = []
    for case in CASES:
        result = compare(case["left"], read(root, case["left"]), case["right"], read(root, case["right"]))
        ok = result.get("decision") == case["expected"]
        results.append({"id": case["id"], "expected": case["expected"], "actual": result.get("decision"), "passed": ok, "reason": case["reason"], "decision_basis": result.get("decision_basis", {}), "layers": result.get("layers", {})})
        if not ok:
            failures.append(case["id"])

    human = load_json(out / "CORE_HUMAN_ANNOTATIONS.json")
    flagged = legacy_conflicts(human.get("annotations", []))
    report = {
        "engine": "CORE A.C.E. Relationship Ontology Calibration v3",
        "mode": "READ_ONLY",
        "canonical_rule": "VARIANT requires same underlying information in the same relevant context; RELATED covers meaningful conceptual relationship with different context or information.",
        "cases": results,
        "passed": len(failures) == 0,
        "legacy_annotation_conflicts": flagged,
        "legacy_conflicts_are_not_training_truth": True,
        "safety": {"automatic_training": False, "automatic_rule_promotion": False, "automatic_canon_change": False, "human_validation_required": True},
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "CORE_RELATIONSHIP_ONTOLOGY_CALIBRATION_V3.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"cases": len(CASES), "passed": len(CASES) - len(failures), "failed": len(failures), "legacy_cross_scope_variant_labels_flagged": len(flagged)}, indent=2))
    if failures:
        raise SystemExit("Relationship ontology calibration failed: " + ", ".join(failures))

if __name__ == "__main__":
    main()
