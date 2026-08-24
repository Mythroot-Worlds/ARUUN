#!/usr/bin/env python3
"""Build a context-aware, read-only human consolidation review packet."""
from __future__ import annotations
import argparse,json,re
from collections import defaultdict
from pathlib import Path
SKIP={".git",".github","node_modules","__pycache__"}
DOMAINS={"01_WORLD":"WORLD","02_ECOLOGY":"ECOLOGY","03_PEOPLES":"PEOPLES","04_REGIONS":"REGIONS","05_HISTORY":"HISTORY","06_MAGIC":"MAGIC","00_MASTER":"MASTER","TOOLS":"TOOLS"}
ROLE_HINTS={"TOOLS":"TOOL","CHECKLIST":"REFERENCE","SCHEMA":"SYSTEM","OPERATING_RULES":"SYSTEM","COMPARATIVE":"REFERENCE","COMPARISON":"REFERENCE","MATRIX":"TOOL","CREATION_PACKAGE":"TOOL"}
BOILERPLATE=("working canon","not locked canon","decision unresolved","documents record our decisions","flagged rather than silently","review only","human canon decision")
def norm(s): return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]+"," ",s.lower())).strip()
def context(path):
 parts=path.split("/"); domain=DOMAINS.get(parts[0],"OTHER"); role="CANON"
 up=path.upper()
 for hint,r in ROLE_HINTS.items():
  if hint in up: role=r; break
 return domain,role,parts[:-1]
def units(text):
 out=[]
 for block in re.split(r"\n\s*\n",text):
  b=block.strip()
  if not b or b.startswith("#"): continue
  if b.startswith(("- ","* ")): out.extend(x.strip("-* ") for x in b.splitlines() if x.strip())
  else: out.append(b)
 return out
def is_process(u): return any(x in norm(u) for x in BOILERPLATE)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",default=".");ap.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS");a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out;out.mkdir(parents=True,exist_ok=True)
 sources=[]
 for p in root.rglob("*.md"):
  rel=p.relative_to(root).as_posix()
  if any(x in SKIP for x in p.parts) or rel.startswith("07_ARCHIVE/") or rel.startswith(a.out): continue
  domain,role,folder=context(rel); t=p.read_text(encoding="utf-8",errors="replace"); sources.append((rel,domain,role,folder,units(t)))
 buckets=defaultdict(list)
 for path,domain,role,folder,us in sources:
  for u in us:
   if len(u)<20 or is_process(u): continue
   buckets[norm(u)].append((path,domain,role,folder,u))
 review=[]
 for key,occ in buckets.items():
  contexts={(d,r) for _,d,r,_,_ in occ}; paths=sorted({p for p,_,_,_,_ in occ})
  # Same text is only a consolidation candidate when contextual relationship supports it.
  if len(paths)<2 or len(contexts)>1 and not any(r=="CANON" for _,_,r,_,_ in occ): continue
  review.append({"unit":occ[0][4],"sources":paths,"occurrences":len(occ),"contexts":[{"path":p,"domain":d,"role":r,"folder":f} for p,d,r,f,_ in occ],"status":"SHARED_EVIDENCE","decision":"UNRESOLVED","provenance":[{"path":p,"domain":d,"role":r,"text":u} for p,d,r,_,u in occ]})
 data={"mode":"READ_ONLY","review_only":True,"unit_count":len(review),"context_model":{"domains":sorted(set(DOMAINS.values())),"roles":["CANON","TOOL","REFERENCE","SYSTEM"]},"items":review,"decision_vocabulary":["KEEP","MERGE","MOVE","LINK","ARCHIVE","UNRESOLVED"]}
 (out/"CANONICAL_CONSOLIDATION_REVIEW.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
 lines=["# ARUUN Canonical Consolidation Review","","**Mode:** READ-ONLY / PROPOSE-ONLY","","Repeated wording is not treated as canon overlap unless document context supports consolidation. Process/boilerplate language is excluded. Titles are corroborating metadata, not primary evidence.","","## Decision vocabulary","`KEEP` · `MERGE` · `MOVE` · `LINK` · `ARCHIVE` · `UNRESOLVED`","",f"Context-qualified shared evidence units: **{len(review)}**","",]
 for i,x in enumerate(review,1):
  lines += [f"## {i}. {x['unit']}",f"- **Status:** {x['status']}",f"- **Occurrences:** {x['occurrences']}","- **Contexts:"]+[f"  - `{c['path']}` — {c['domain']} / {c['role']}" for c in x["contexts"]]+["- **Decision:** `UNRESOLVED`","- **Provenance:"]+[f"  - `{p['path']}`" for p in x["provenance"]]+[""]
 (out/"CANONICAL_CONSOLIDATION_REVIEW.md").write_text("\n".join(lines),encoding="utf-8")
 print(f"Built {len(review)} context-qualified shared-evidence review units.")
if __name__=="__main__": main()
