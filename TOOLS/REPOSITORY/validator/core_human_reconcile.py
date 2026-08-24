#!/usr/bin/env python3
"""Reconcile human annotations to the exact CORE blind-test relationship IDs.

This layer is deliberately read-only. It matches by normalized exact file pair,
keeps raw human choices and reasoning, detects duplicate annotations, and never
writes to the decision ledger or promotes a rule.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def load_json(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("content"), str):
        try:
            return json.loads(data["content"])
        except json.JSONDecodeError:
            pass
    return data


def key(left: str, right: str):
    return tuple(sorted((left.strip(), right.strip())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="TOOLS/REPOSITORY/REPORTS")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    out = root / args.out
    out.mkdir(parents=True, exist_ok=True)

    blind = load_json(out / "CORE_BLIND_TEST.json")
    human = load_json(out / "CORE_HUMAN_ANNOTATIONS.json")
    predictions = blind.get("predictions", [])
    annotations = human.get("annotations", [])

    holdout = {key(p["left"], p["right"]): p for p in predictions}
    seen = {}
    matched = []
    unmatched = []
    duplicates = []

    for ann in annotations:
        k = key(ann["left"], ann["right"])
        if k in seen:
            duplicates.append({"annotation": ann, "first_index": seen[k]})
            continue
        seen[k] = len(seen)
        pred = holdout.get(k)
        if pred is None:
            unmatched.append(ann)
            continue
        matched.append({
            "relationship_id": pred["relationship_id"],
            "left": pred["left"],
            "right": pred["right"],
            "machine_prediction": pred.get("predicted_classification"),
            "machine_confidence": pred.get("confidence"),
            "match_strength": pred.get("match_strength"),
            "human_raw_choices": ann.get("raw_choices", []),
            "human_reasoning": ann.get("reasoning", ""),
            "requires_human_validation": pred.get("requires_human_validation", True),
        })

    matched_ids = {m["relationship_id"] for m in matched}
    remaining = [p for p in predictions if p["relationship_id"] not in matched_ids]

    report = {
        "engine": "CORE A.C.E. Human Reconciliation",
        "mode": "READ_ONLY",
        "holdout_size": len(predictions),
        "annotation_count": len(annotations),
        "unique_annotation_pairs": len(seen),
        "matched_count": len(matched),
        "unmatched_annotation_count": len(unmatched),
        "duplicate_annotation_count": len(duplicates),
        "remaining_holdout_count": len(remaining),
        "matched": matched,
        "unmatched_annotations": unmatched,
        "duplicates": duplicates,
        "remaining_holdout_relationships": [
            {
                "relationship_id": p["relationship_id"],
                "left": p["left"],
                "right": p["right"],
                "machine_prediction": p.get("predicted_classification"),
                "machine_confidence": p.get("confidence"),
            }
            for p in remaining
        ],
        "safety": {
            "automatic_training": False,
            "automatic_rule_promotion": False,
            "automatic_canon_change": False,
            "provenance_loss_is_failure": True,
            "machine_predictions_remain_frozen": True,
        },
    }
    (out / "CORE_HUMAN_RECONCILIATION.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    md = [
        "# CORE A.C.E. Human Reconciliation",
        "",
        "Read-only reconciliation of human annotations against exact blind-test relationship IDs.",
        "",
        f"- Holdout relationships: **{len(predictions)}**",
        f"- Human annotations: **{len(annotations)}**",
        f"- Unique annotation pairs: **{len(seen)}**",
        f"- Exact-ID matches: **{len(matched)}**",
        f"- Unmatched annotations: **{len(unmatched)}**",
        f"- Duplicate annotations: **{len(duplicates)}**",
        f"- Remaining holdout relationships: **{len(remaining)}**",
        "",
        "## Safety",
        "- Human judgments are not written into the decision ledger.",
        "- Machine predictions remain frozen.",
        "- No rule is promoted automatically.",
        "- No canon content is changed automatically.",
        "",
        "## Matched relationships",
    ]
    for m in matched:
        md.append(f"- `{m['relationship_id']}` — `{m['machine_prediction']}` vs human `{', '.join(m['human_raw_choices'])}`")
    md += ["", "## Remaining holdout relationships"]
    for p in remaining:
        md.append(f"- `{p['relationship_id']}` — `{p['left']}` ↔ `{p['right']}`")
    (out / "CORE_HUMAN_RECONCILIATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"CORE reconciliation: {len(matched)} matched, {len(remaining)} remaining, {len(unmatched)} unmatched, {len(duplicates)} duplicates.")


if __name__ == "__main__":
    main()
