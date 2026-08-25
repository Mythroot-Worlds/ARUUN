#!/usr/bin/env python3
"""CORE deciding-factor audit for A.C.E. Detective cases.

Batman currently records a 15-dimension factor snapshot, but its investigative
questions use a smaller operational focus set. This patch audits every case and
makes the remaining dimensions explicit instead of silently treating them as
irrelevant. It is read-only and never resolves canon.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from core_foundations import DIMENSIONS

OPERATIONAL_DIMENSIONS = {
    "authority", "scope", "support", "temporal", "family", "specialist"
}


def load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
    except Exception:
        return default


def audit_case(case):
    factors = case.get("deciding_factors", {})
    rows=[]
    for name, (description, _) in DIMENSIONS.items():
        snapshot=factors.get(name, {})
        shared=snapshot.get("shared", [])
        different=snapshot.get("different", [])
        operational=name in OPERATIONAL_DIMENSIONS
        rows.append({
            "dimension": name,
            "description": description,
            "operational_focus": operational,
            "shared_signals": shared,
            "different_signals": different,
            "has_signal": bool(shared or different),
            "investigated": operational and bool(case.get("questions")),
            "status": "INVESTIGATED" if operational else ("SIGNAL_PRESENT_REQUIRES_REVIEW" if shared or different else "NO_SIGNAL"),
        })
    return {
        "relationship_id": case.get("relationship_id"),
        "documents": case.get("documents", {}),
        "factor_count": len(rows),
        "factors": rows,
        "coverage": {
            "total_dimensions": len(rows),
            "operational_dimensions": sum(r["operational_focus"] for r in rows),
            "dimensions_with_signals": sum(r["has_signal"] for r in rows),
            "non_operational_signals": sum((not r["operational_focus"]) and r["has_signal"] for r in rows),
        },
        "safety": {
            "purpose": "expose deciding-factor evidence gaps for later Detective expansion",
            "automatic_relationship_resolution": False,
            "automatic_canon_change": False,
        },
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=".")
    ap.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS")
    args=ap.parse_args()
    root=Path(args.root).resolve(); out=root/args.out
    report=load(out/"CORE_DETECTIVE_REPORT.json", {"cases": []})
    cases=[audit_case(c) for c in report.get("cases", [])]
    summary={
        "cases": len(cases),
        "factor_dimensions": len(DIMENSIONS),
        "operational_dimensions": len(OPERATIONAL_DIMENSIONS),
        "cases_with_non_operational_signals": sum(c["coverage"]["non_operational_signals"] > 0 for c in cases),
        "non_operational_signals": sum(c["coverage"]["non_operational_signals"] for c in cases),
    }
    payload={
        "engine":"CORE Deciding-Factor Audit",
        "schema_version":"1.0",
        "mode":"READ_ONLY",
        "purpose":"audit Detective coverage across the complete Mythroot deciding-factor ontology",
        "cases":cases,
        "summary":summary,
        "next_patch":"Expand Detective question generation for non-operational dimensions only when their factor evidence warrants investigation.",
    }
    out.mkdir(parents=True,exist_ok=True)
    (out/"CORE_DECIDING_FACTOR_AUDIT.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    md=['# CORE Deciding-Factor Audit','','This report exposes where Batman has factor evidence outside its current operational investigation focus.','',f'Cases: **{len(cases)}**',f'Ontology dimensions: **{len(DIMENSIONS)}**',f'Current operational dimensions: **{len(OPERATIONAL_DIMENSIONS)}**',f'Cases with non-operational signals: **{summary["cases_with_non_operational_signals"]}**',f'Non-operational signals: **{summary["non_operational_signals"]}**','', '**Read-only. No relationship or canon decision is made by this audit.**']
    (out/"CORE_DECIDING_FACTOR_AUDIT.md").write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    main()
