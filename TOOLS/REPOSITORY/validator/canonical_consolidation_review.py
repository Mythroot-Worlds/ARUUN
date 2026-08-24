#!/usr/bin/env python3
"""Build a read-only, context-aware human consolidation review packet.

Repeated wording alone is not treated as evidence that two documents should be
consolidated. Folder/domain context, document role, and reusable boilerplate
signals are used to reduce false positives while preserving provenance.
"""
from __future__ import annotations
import argparse,json,re
from collections import defaultdict
from pathlib import Path

SKIP={".git",".github","node_modules","__pycache__"}
ARCHIVE_PREFIX="07_ARCHIVE/"
SYSTEM_PREFIXES=("TOOLS/REPOSITORY/","CHANGELOG.md","PROJECT_OPERATING_RULES.md")
ROLE_MARKERS={
 "tool": ("CREATION_MATRIX","CREATION_PACKAGE","FUNCTION_MATRIX","ALGORITHM","PROMPT","TEMPLATE","SCHEMA"),
 "reference": ("CHECKLIST","COMPARATIVE","REFERENCE"),
 "canon": ("WORLD_BIBLE","CURRENT_CANON","CANONICAL","/CULTURES/","/ECOLOGY/"),
}
# Common process language is useful for humans but weak evidence of shared world facts.
BOILERPLATE_PHRASES=(
 "status working canon","status broad working framework","documents record our decisions",
 "do not begin by asking","flagged rather than silently left out","decision unresolved",
 "not locked canon","working canon","human canon decision required",
)
DOMAIN_ORDER=("world","peoples","ecology","tools","system","reference","other")

def norm(s): return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]+"," ",s.lower())).strip()
def domain(rel):
 u="/"+rel.upper()+"/"
 if "/03_PEOPLES/" in u: return "peoples"
 if "/02_ECOLOGY/" in u: return "ecology"
 if "/01_WORLD/" in u: return "world"
 if "/TOOLS/" in u or rel.upper().startswith("PROJECT_OPERATING_RULES") or rel.upper().startswith("CHANGELOG"): return "tools"
 if "/00_MASTER/" in u: return "system"
 if any(x in u for x in ("COMPARATIVE","CHECKLIST","REFERENCE")): return "reference"
 return "other"
def role(rel):
 u="/"+rel.upper()+"/"
 for r,markers in ROLE_MARKERS.items():
  if any(m in u for m in markers): return r
 return "canon" if domain(rel) in ("peoples","ecology","world") else "other"
def context_compatible(a,b):
 da,db=domain(a),domain(b); ra,rb=role(a),role(b)
 if da==db: return True
 # Parallel world domains can share methodology/reference language, but not be
 # promoted to a canon lineage solely because a phrase repeats.
 if {ra,rb}=={"tool","reference"}: return True
 if ra==rb=="canon" and {da,db}<={"world","peoples","ecology"}: return False
 return False
def is_boilerplate(u):
 n=norm(u)
 return any(p in n for p in BOILERPLATE_PHRASES)
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
  if any(x in SKIP for x in p.parts) or rel.startswith(ARCHIVE_PREFIX) or rel.startswith(a.out) or any(rel.upper().startswith(x.upper()) for x in SYSTEM_PREFIXES): continue
  t=p.read_text(encoding="utf-8",errors="replace"); sources.append((rel,units(t),domain(rel),role(rel)))
 buckets=defaultdict(list)
 for path,us,dom,rol in sources:
  for u in us:
   if len(u)<20 or is_boilerplate(u): continue
   buckets[norm(u)].append((path,u,dom,rol))
 review=[]
 for key,occ in buckets.items():
  # Only compare occurrences whose document contexts are compatible.
  compatible=[]
  for item in occ:
   if any(context_compatible(item[0],other[0]) for other in occ if other[0]!=item[0]): compatible.append(item)
  if len({p for p,_,_,_ in compatible})<2: continue
  paths=sorted({p for p,_,_,_ in compatible})
  shared_domains=sorted({d for _,_,d,_ in compatible})
  shared_roles=sorted({r for _,_,_,r in compatible})
  review.append({"unit":compatible[0][1],"sources":paths,"occurrences":len(compatible),"context":{"domains":shared_domains,"roles":shared_roles},"status":"SHARED_EVIDENCE","decision":"UNRESOLVED","provenance":[{"path":p,"domain":d,"role":r,"text":u} for p,u,d,r in compatible]})
 data={"mode":"READ_ONLY","review_only":True,"context_aware":True,"unit_count":len(review),"items":review,"decision_vocabulary":["KEEP","MERGE","MOVE","LINK","ARCHIVE","UNRESOLVED"]}
 (out/"CANONICAL_CONSOLIDATION_REVIEW.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
 lines=["# ARUUN Canonical Consolidation Review","","**Mode:** READ-ONLY / PROPOSE-ONLY","**Context aware:** Yes","","Repeated wording is weak evidence by itself. Folder/domain context, document role, and common process language are used to reduce false positives.","","## Decision vocabulary","`KEEP` · `MERGE` · `MOVE` · `LINK` · `ARCHIVE` · `UNRESOLVED`","",f"Context-compatible shared evidence units: **{len(review)}**","",]
 for i,x in enumerate(review,1):
  lines += [f"## {i}. {x['unit']}",f"- **Status:** {x['status']}",f"- **Occurrences:** {x['occurrences']}",f"- **Domains:** {', '.join(x['context']['domains'])}",f"- **Roles:** {', '.join(x['context']['roles'])}",f"- **Sources:** {', '.join('`'+p+'`' for p in x['sources'])}","- **Decision:** `UNRESOLVED`","- **Provenance:**"]
  for pr in x["provenance"]: lines.append(f"  - `{pr['path']}` — {pr['domain']} / {pr['role']}")
  lines.append("")
 (out/"CANONICAL_CONSOLIDATION_REVIEW.md").write_text("\n".join(lines),encoding="utf-8")
 print(f"Built {len(review)} context-compatible shared-evidence review units.")
if __name__=="__main__": main()
