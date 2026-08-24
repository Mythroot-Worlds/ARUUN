#!/usr/bin/env python3
"""CORE A.C.E. — Adaptive Calibration Engine.

Read-only calibration scaffolding: human decisions become labeled examples and
candidate heuristics, but no learned rule is promoted automatically.
"""
from __future__ import annotations
import argparse,json,re
from collections import Counter,defaultdict
from pathlib import Path
LABELS={"DUPLICATE","VARIANT","SUPPORTING","HISTORICAL","COINCIDENTAL","MISPLACED","CONFLICT","RELATED","REVIEW"}
PROMOTION_THRESHOLD=5

def norm(s): return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]+"," ",s.lower())).strip()
def load(path,default):
 if not path.exists(): return default
 try: return json.loads(path.read_text(encoding="utf-8"))
 except Exception: return default

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--root",default="."); ap.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS"); args=ap.parse_args()
 root=Path(args.root).resolve(); out=root/args.out; out.mkdir(parents=True,exist_ok=True)
 ledger=load(out/"CORE_DECISION_LEDGER.json",{"decisions":[]})
 decisions=ledger.get("decisions",[])
 valid=[d for d in decisions if d.get("label") in LABELS]
 by_rule=defaultdict(Counter)
 for d in valid:
  ctx=d.get("context",{}); key=(ctx.get("domain","UNKNOWN"),ctx.get("role","UNKNOWN"),d.get("proposed","UNKNOWN"),d.get("label")); by_rule[key]["count"]+=1
 heuristics=[]
 for (domain,role,proposed,label),c in sorted(by_rule.items()):
  n=c["count"]
  heuristics.append({"domain":domain,"role":role,"proposed":proposed,"observed_label":label,"support":n,"status":"CANDIDATE" if n<PROMOTION_THRESHOLD else "ELIGIBLE_FOR_HUMAN_REVIEW","auto_apply":False})
 report={"engine":"CORE A.C.E.","mode":"READ_ONLY","decision_count":len(valid),"label_vocabulary":sorted(LABELS),"promotion_threshold":PROMOTION_THRESHOLD,"heuristic_candidates":heuristics,"safety":{"automatic_rule_promotion":False,"automatic_canon_change":False,"provenance_loss_is_failure":True}}
 (out/"CORE_ACE_CALIBRATION_REPORT.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
 md=["# CORE A.C.E. Calibration Report","","**Adaptive Calibration Engine** — read-only training/calibration layer.","","Human decisions are evidence for calibration, not automatic permission to change canon or rules.","",f"Labeled decisions: **{len(valid)}**",f"Heuristic candidates: **{len(heuristics)}**","", "## Safety invariants", "- Automatic rule promotion: **OFF**", "- Automatic canon changes: **OFF**", "- Provenance loss: **HARD FAILURE**", "", "## Candidate heuristics"]
 for h in heuristics: md.append(f"- `{h['domain']}/{h['role']}` proposed `{h['proposed']}` → observed `{h['observed_label']}` ({h['support']} examples): **{h['status']}**")
 if not valid: md += ["","No labeled decisions exist yet. Populate `CORE_DECISION_LEDGER.json` with human-adjudicated examples from the Hearth Family/Birth/Childhood calibration set before promoting any heuristic."]
 (out/"CORE_ACE_CALIBRATION_REPORT.md").write_text("\n".join(md)+"\n",encoding="utf-8")
 print(f"CORE A.C.E.: {len(valid)} labeled decisions; {len(heuristics)} heuristic candidates.")
if __name__=="__main__": main()
