#!/usr/bin/env python3
"""Build a read-only human review packet from lineage/assembly evidence."""
from __future__ import annotations
import argparse,json,re
from collections import defaultdict
from pathlib import Path
SKIP={".git",".github","node_modules","__pycache__"}
def norm(s): return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]+"," ",s.lower())).strip()
def units(text):
 out=[]
 for block in re.split(r"\n\s*\n",text):
  b=block.strip()
  if not b or b.startswith("#"): continue
  if b.startswith("- ") or b.startswith("* "):
   out.extend(x.strip("-* ") for x in b.splitlines() if x.strip())
  else: out.append(b)
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",default=".");ap.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS");a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out;out.mkdir(parents=True,exist_ok=True)
 sources=[]
 for p in root.rglob("*.md"):
  rel=p.relative_to(root).as_posix()
  if any(x in SKIP for x in p.parts) or rel.startswith("07_ARCHIVE/") or rel.startswith(a.out): continue
  t=p.read_text(encoding="utf-8",errors="replace"); sources.append((rel,units(t)))
 # Conservative exact normalized-unit grouping. Similar-but-not-identical units remain visible.
 buckets=defaultdict(list)
 for path,us in sources:
  for u in us:
   if len(u)<20: continue
   buckets[norm(u)].append((path,u))
 review=[]
 for key,occ in buckets.items():
  paths=sorted({p for p,_ in occ})
  if len(paths)<2: continue
  review.append({"unit":occ[0][1],"sources":paths,"occurrences":len(occ),"status":"SHARED_EVIDENCE","decision":"UNRESOLVED","provenance":[{"path":p,"text":u} for p,u in occ]})
 data={"mode":"READ_ONLY","review_only":True,"unit_count":len(review),"items":review,"decision_vocabulary":["KEEP","MERGE","MOVE","LINK","ARCHIVE","UNRESOLVED"]}
 (out/"CANONICAL_CONSOLIDATION_REVIEW.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
 lines=["# ARUUN Canonical Consolidation Review","","**Mode:** READ-ONLY / PROPOSE-ONLY","","This packet consolidates repeated evidence for human review. It does not declare canon, delete sources, or move files.","","## Decision vocabulary","`KEEP` · `MERGE` · `MOVE` · `LINK` · `ARCHIVE` · `UNRESOLVED`","",f"Shared evidence units: **{len(review)}**","",]
 for i,x in enumerate(review,1):
  lines += [f"## {i}. {x['unit']}",f"- **Status:** {x['status']}",f"- **Occurrences:** {x['occurrences']}",f"- **Sources:** {', '.join('`'+p+'`' for p in x['sources'])}","- **Decision:** `UNRESOLVED`","- **Provenance:**"]
  for pr in x["provenance"]: lines.append(f"  - `{pr['path']}`")
  lines.append("")
 (out/"CANONICAL_CONSOLIDATION_REVIEW.md").write_text("\n".join(lines),encoding="utf-8")
 print(f"Built {len(review)} shared-evidence review units.")
if __name__=="__main__": main()
