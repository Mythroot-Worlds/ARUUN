#!/usr/bin/env python3
"""ARUUN read-only subject-lineage/consolidation audit with identity-first grouping."""
from __future__ import annotations
import argparse,json,re
from difflib import SequenceMatcher
from pathlib import Path
from core_document_identity import identify
SKIP={".git",".github","node_modules","__pycache__"};ARCHIVE="07_ARCHIVE/";REPORTS="TOOLS/REPOSITORY/REPORTS/";SYSTEM_PREFIXES=("PROJECT_OPERATING_RULES.md","TOOLS/REPOSITORY/ARUUN_REPOSITORY_SCHEMA","TOOLS/REPOSITORY/CONTENT_LINEAGE_SPEC","TOOLS/REPOSITORY/PLACEMENT_CALIBRATION","TOOLS/REPOSITORY/REPORTS/");REFERENCE_NAMES=("CULTURAL_AUDIT_CHECKLIST.md","COMPARATIVE_REFERENCE","COMPARATIVE_MODEL","CHECKLIST","SCHEMA","OPERATING_RULES")
ALIASES={"family_birth_childhood":("family_birth_childhood",("birth","childhood")),"family_partnership":("family_partnership",("partnership","marriage")),"governance_authority":("governance_authority",("governance","authority")),"food_subsistence":("food_subsistence",("food","subsistence")),"settlement_housing":("settlement_housing",("settlement","housing"))}
def norm(s):return re.sub(r"[^a-z0-9]+","_",s.lower()).strip("_")
def words(t):return set(re.findall(r"[a-z][a-z0-9'-]{3,}",t.lower()))
def similarity(a,b):return SequenceMatcher(None,sorted(words(a)),sorted(words(b))).ratio()
def sections(t):
 out=[];cur="ROOT";buf=[]
 for line in t.splitlines():
  if line.startswith("#"):
   if buf:out.append((cur,"\n".join(buf).strip()))
   cur=re.sub(r"^#+\s*","",line).strip();buf=[]
  else:buf.append(line)
 if buf:out.append((cur,"\n".join(buf).strip()))
 return [(h,b) for h,b in out if b]
def units(body):
 raw=[];buf=[]
 for line in body.splitlines():
  s=line.strip()
  if not s:
   if buf:raw.append(" ".join(buf));buf=[]
   continue
  if s.startswith(('-', '*', '•')):
   if buf:raw.append(" ".join(buf));buf=[]
   raw.append(re.sub(r"^[-*•]\s*","",s))
  else:buf.append(s)
 if buf:raw.append(" ".join(buf))
 return [x for x in raw if len(words(x))>=4]
def unit_similarity(a,b):
 wa,wb=words(a),words(b)
 if not wa or not wb:return 0.0
 overlap=len(wa&wb)/max(1,min(len(wa),len(wb)));seq=SequenceMatcher(None,a.lower(),b.lower()).ratio();return .65*overlap+.35*seq
def likely_system_or_reference(rel):
 u=rel.upper();return any(u.startswith(x.upper()) for x in SYSTEM_PREFIXES) or any(x in u for x in REFERENCE_NAMES)
def subject_key(path,t):
 identity=identify(path);key=identity['subject']
 if key:return key,"STRUCTURAL_IDENTITY"
 n=norm(path.stem);n=re.sub(r"_comparative$|_revision\d*$|_v\d+$|_draft\d*$","",n)
 for k,(base,terms) in ALIASES.items():
  if base in n:return k,"DIRECT_NAME"
  if all(x in n for x in terms):return k,"DIRECT_TERMS"
 low=t.lower()
 for k,(_,terms) in ALIASES.items():
  if sum(low.count(x) for x in terms)>=10:return k,"CONTENT_STRONG"
 return None,None
def compare_units(sa,sb):
 ua,ub=units(sa),units(sb);matches=[];matched_b=set()
 for a in ua:
  best=(-1,-1.0)
  for j,b in enumerate(ub):
   if j in matched_b:continue
   score=unit_similarity(a,b)
   if score>best[1]:best=(j,score)
  if best[0]>=0 and best[1]>=.48:matched_b.add(best[0]);matches.append({"a":a,"b":ub[best[0]],"score":round(best[1],3),"status":"LIKELY_SHARED" if best[1]>=.72 else "POSSIBLY_SHARED"})
 unmatched_a=[x for x in ua if not any(m["a"]==x for m in matches)];unmatched_b=[x for j,x in enumerate(ub) if j not in matched_b];conflicts=[{"a":m["a"],"b":m["b"],"reason":"similar evidence unit with material wording/content difference; human review required"} for m in matches if .48<=m["score"]<.72]
 return {"units_a":len(ua),"units_b":len(ub),"shared_units":matches,"unique_to_a":unmatched_a,"unique_to_b":unmatched_b,"possible_conflicts":conflicts}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",default=".");ap.add_argument("--out",default=REPORTS);ap.add_argument("--scope");a=ap.parse_args();root=Path(a.root).resolve();base=root/a.scope if a.scope else root;docs=[]
 for p in base.rglob("*.md"):
  rel=p.relative_to(root).as_posix()
  if any(x in SKIP for x in p.parts) or rel.startswith(ARCHIVE) or rel.startswith(REPORTS) or likely_system_or_reference(rel):continue
  t=p.read_text(encoding="utf-8",errors="replace");identity=identify(rel);key,reason=subject_key(p,t);docs.append((rel,t,key,reason,identity))
 groups={}
 for rel,t,key,reason,identity in docs:
  # Identity type is a hard grouping boundary. Regional scope remains a
  # property of each sibling, not a reason to collapse different document types.
  if key and (reason.startswith("STRUCTURAL") or reason.startswith("DIRECT")):groups.setdefault((key,identity['content_type']),[]).append((rel,t,reason,identity))
 clusters=[]
 for (key,ctype),items in groups.items():
  if len(items)<2:continue
  entries=[{"path":r,"match_basis":reason,"identity":identity,"sections":[h for h,_ in sections(t)],"word_count":len(words(t))} for r,t,reason,identity in items];comparisons=[]
  for i,(ra,ta,_,ia) in enumerate(items):
   for rb,tb,_,ib in items[i+1:]:
    sa={norm(h):b for h,b in sections(ta)};sb={norm(h):b for h,b in sections(tb)};common=sorted(set(sa)&set(sb));unit_results={h:compare_units(sa[h],sb[h]) for h in common};comparisons.append({"a":ra,"b":rb,"scope_a":ia['scope'],"scope_b":ib['scope'],"regional_scope_relation":"SAME_SCOPE" if ia['scope']==ib['scope'] else "REGIONAL_SIBLINGS","sections_only_in_a":sorted(set(sa)-set(sb)),"sections_only_in_b":sorted(set(sb)-set(sa)),"unit_analysis":unit_results,"overall_similarity":round(similarity(ta,tb),3)})
  clusters.append({"subject":key,"content_type":ctype,"documents":entries,"comparisons":comparisons,"review_status":"UNRESOLVED"})
 out=root/a.out;out.mkdir(parents=True,exist_ok=True);data={"mode":"READ_ONLY","identity_first":True,"scope":a.scope or "ALL_ACTIVE_NON_GENERATED_CONTENT","clusters":len(clusters),"clusters_detail":clusters};(out/"CONTENT_LINEAGE_REPORT.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
 lines=["# ARUUN Content Lineage & Consolidation Audit","","**Mode:** READ-ONLY",f"**Scope:** `{a.scope or 'ALL_ACTIVE_NON_GENERATED_CONTENT'}`",f"**Lineage clusters:** {len(clusters)}","","First-class document identity (subject + content type + scope) is resolved before lineage grouping. Regional siblings are compared as variants/contributors, not assumed to replace one another.","","Human decisions only: `KEEP`, `MERGE`, `MOVE`, `LINK`, `ARCHIVE`, `UNRESOLVED",""]
 for c in clusters:
  lines += [f"## {c['subject']} ({c['content_type']})","","### Sources"]+[f"- `{x['path']}` — `{x['match_basis']}`; scope `{x['identity']['scope']}`; role `{x['identity']['role']}`" for x in c['documents']]
  for cmp in c['comparisons']:
   lines += ["",f"### Compare: `{cmp['a']}` ↔ `{cmp['b']}`",f"- Scope relation: **{cmp['regional_scope_relation']}**",f"- Overall similarity: **{cmp['overall_similarity']}**"]
   for h,r in cmp['unit_analysis'].items():lines += [f"- **Section:** `{h}`",f"  - Shared/possible units: {len(r['shared_units'])}",f"  - Unique to first: {len(r['unique_to_a'])}",f"  - Unique to second: {len(r['unique_to_b'])}",f"  - Possible conflicts: {len(r['possible_conflicts'])}"]
  lines += ["","**Human decision:** `UNRESOLVED`",""]
 (out/"CONTENT_LINEAGE_REPORT.md").write_text("\n".join(lines),encoding="utf-8");print(f"Identified {len(clusters)} identity-bounded subject lineage clusters with information-unit comparison.")
if __name__=="__main__":main()
