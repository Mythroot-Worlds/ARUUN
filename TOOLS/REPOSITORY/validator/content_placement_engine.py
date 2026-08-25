#!/usr/bin/env python3
"""ARUUN read-only content placement audit."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from core_document_identity import identify

SKIP={".git",".github","node_modules","__pycache__"}; ARCHIVE="07_ARCHIVE/"; REPORTS="TOOLS/REPOSITORY/REPORTS/"
TOOL_HINTS=("algorithm","formula","simulation","creation package","design sheet","design brief","necessity sheet","predictive evolution")
SUBJECT_RULES={"family_birth_childhood":("family.birth_childhood","FAMILY_BIRTH_CHILDHOOD.md"),"family_partnership":("family.partnership","FAMILY_PARTNERSHIP.md"),"governance_authority":("governance.authority","GOVERNANCE_AUTHORITY.md"),"governance_and_authority":("governance.authority","GOVERNANCE_AUTHORITY.md"),"food_subsistence":("food.subsistence","FOOD_SUBSISTENCE.md"),"settlement_housing":("settlement.housing","SETTLEMENT_HOUSING.md")}
REGIONS=("PLAINS","MOUNTAINS","RIVER","WETLANDS","DESERT","COAST")

def text(p): return p.read_text(encoding="utf-8",errors="replace")
def front(t):
 if not t.startswith("---\n"): return {}
 e=t.find("\n---",4)
 if e<0:return {}
 d={}
 for line in t[4:e].splitlines():
  if ":" in line:k,v=line.split(":",1);d[k.strip().lower()]=v.strip().strip("\"'")
 return d

def score_region(body,region):
 aliases={"PLAINS":("plains","grassland","woodland mosaic","great plains"),"MOUNTAINS":("mountain","highland","upland","ridgehorn","aegir","frostward","southward"),"RIVER":("river","floodplain","delta","riverland","silverpine"),"WETLANDS":("wetland","marsh","lake","greenmarsh","waterlogged"),"DESERT":("desert","dry interior","rain shadow","sunscour","arid","basin"),"COAST":("coast","coastal","marine","shore","gulf","peninsula","isle")}
 return sum(body.lower().count(x) for x in aliases[region])

def expected_region(path,t):
 u=path.upper();fm=front(t)
 for r in REGIONS:
  if f"/{r}/" in "/"+u+"/" or u.endswith(f"/{r}.MD"): return r
  if fm.get("people","").upper()==r or fm.get("region","").upper()==r:return r
 return None

def subject_from_name(path):
 s=path.stem.lower().replace("-","_")
 if s.endswith("_comparative"):s=s[:-12]
 return SUBJECT_RULES.get(s,(None,None))[0]

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",default=".");ap.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS");ap.add_argument("--scope");a=ap.parse_args();root=Path(a.root).resolve();base=root/a.scope if a.scope else root
 docs=[]
 for p in base.rglob("*.md"):
  if any(x in SKIP for x in p.parts):continue
  rel=p.relative_to(root).as_posix()
  if rel.startswith(REPORTS) or rel.startswith(ARCHIVE):continue
  t=text(p);docs.append((rel,t,front(t),identify(rel)))
 findings=[]
 for rel,t,fm,identity in docs:
  upper=rel.upper();low=t.lower();region=expected_region(rel,t);tool_hits=[h for h in TOOL_HINTS if h in low];is_tool_path=upper.startswith("TOOLS/");is_world_library=(upper=="02_ECOLOGY/FAUNA/CANONICAL_CREATURE_LIBRARY.MD")
  if len(tool_hits)>=2 and not is_tool_path and not is_world_library and not upper.startswith("00_MASTER/"):
   findings.append({"type":"CONSTRUCTION_METHOD_CANDIDATE","path":rel,"identity":identity,"confidence":"medium","signals":tool_hits[:8],"recommendation":"Review whether this is construction methodology. If so, link it from the world artifact rather than treating the world artifact itself as a tool."})
  # Do not route a document into a semantic regional culture folder merely because its body mentions a region.
  # Structural content type is authoritative for placement heuristics.
  if identity["content_type"] not in {"GEOGRAPHY","ECOLOGY","MASTER","TOOLING"}:
   region_scores={r:score_region(t,r) for r in REGIONS};ranked=sorted(region_scores.items(),key=lambda x:x[1],reverse=True)
   if ranked and ranked[0][1]>=8 and ranked[0][1]>=max(1,ranked[1][1])*1.5 and "/HEARTH/" in upper and "/"+ranked[0][0]+"/" not in "/"+upper+"/" and not upper.startswith("03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/"):
    r,sc=ranked[0];findings.append({"type":"REGIONAL_PLACEMENT_CANDIDATE","path":rel,"identity":identity,"confidence":"medium","candidate_region":r,"score":sc,"other_region_score":ranked[1][1],"recommendation":f"Review whether region-specific {identity['content_type'].lower()} content belongs under 03_PEOPLES/CULTURES/HEARTH/{r}/."})
  subj=subject_from_name(Path(rel))
  if subj and "/COMPARATIVE/" not in upper:
   if region and "/"+region+"/" not in "/"+upper+"/":findings.append({"type":"SUBJECT_PLACEMENT_CANDIDATE","path":rel,"identity":identity,"subject":subj,"confidence":"high","recommendation":"Review regional placement against the one-region/one-authoritative-subject architecture."})
   if Path(rel).stem.lower() in {"family_birth_childhood","family_partnership","governance_and_authority"} and region is None:findings.append({"type":"LEGACY_FLAT_REGIONAL_FILE","path":rel,"identity":identity,"subject":subj,"confidence":"high","recommendation":"Likely legacy flat file; compare against regional source files before migration."})
  meta_region=(fm.get("people") or fm.get("region") or "").upper()
  if meta_region in REGIONS and "/"+meta_region+"/" not in "/"+upper+"/":findings.append({"type":"METADATA_PATH_MISMATCH","path":rel,"identity":identity,"declared_region":meta_region,"confidence":"high","recommendation":"Review metadata or move candidate; do not auto-correct."})
 byname={}
 for rel,t,fm,identity in docs:
  key=Path(rel).stem.lower().replace("_comparative","")
  if key in SUBJECT_RULES:byname.setdefault(key,[]).append((rel,identity))
 for key,items in byname.items():
  if len(items)>1:findings.append({"type":"SUBJECT_LINEAGE_CLUSTER","subject":key,"paths":[x[0] for x in items],"identity_types":sorted({x[1]['content_type'] for x in items}),"confidence":"high","recommendation":"Review these same-type files as one subject lineage; regional siblings should be treated as scope variants rather than automatic replacement candidates."})
 out=root/a.out;out.mkdir(parents=True,exist_ok=True);data={"mode":"READ_ONLY","scope":a.scope or "ALL_ACTIVE_NON_GENERATED_CONTENT","documents":len(docs),"findings":len(findings),"findings_detail":findings,"identity_first":True}
 (out/"CONTENT_PLACEMENT_REPORT.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
 lines=["# ARUUN Content Placement Audit","","**Mode:** READ-ONLY",f"**Scope:** `{a.scope or 'ALL_ACTIVE_NON_GENERATED_CONTENT'}`","",f"Documents analyzed: {len(docs)}",f"Placement candidates: {len(findings)}","","Structural document identity is evaluated before semantic regional routing. Geography is not redirected into culture solely from body-language overlap.","","## Review Candidates"]
 for i,f in enumerate(findings,1):
  lines += [f"### {i}. {f['type']}",f"- **Path:** `{f.get('path','—')}`",f"- **Confidence:** {f.get('confidence','—')}",f"- **Recommendation:** {f.get('recommendation','—')}"]
  if 'candidate_region' in f:lines.append(f"- **Candidate region:** {f['candidate_region']}")
  if 'paths' in f:lines.append("- **Lineage candidates:** "+", ".join(f['paths']))
  if 'signals' in f:lines.append("- **Signals:** "+", ".join(f['signals']))
  lines.append("")
 (out/"CONTENT_PLACEMENT_REPORT.md").write_text("\n".join(lines),encoding="utf-8");print(f"Scanned {len(docs)} documents; generated {len(findings)} placement candidates.")
if __name__=="__main__":main()
