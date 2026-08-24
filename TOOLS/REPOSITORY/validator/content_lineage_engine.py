#!/usr/bin/env python3
"""ARUUN read-only subject-lineage/consolidation audit.

This engine identifies likely versions of the same subject and compares their
content at a coarse section level. It never chooses canon or modifies source
files. Its output is a review packet for KEEP/MERGE/MOVE/LINK/ARCHIVE/
UNRESOLVED decisions.
"""
from __future__ import annotations
import argparse,json,re
from difflib import SequenceMatcher
from pathlib import Path

SKIP={".git",".github","node_modules","__pycache__"}
ARCHIVE="07_ARCHIVE/"
REPORTS="TOOLS/REPOSITORY/REPORTS/"
ALIASES={
 "family_birth_childhood":("family_birth_childhood",("birth","childhood","family","household")),
 "family_partnership":("family_partnership",("partnership","marriage","bond","family")),
 "governance_authority":("governance_authority",("governance","authority","leadership","council")),
 "food_subsistence":("food_subsistence",("food","subsistence","diet","harvest")),
 "settlement_housing":("settlement_housing",("settlement","housing","shelter","village")),
}

def norm(s): return re.sub(r"[^a-z0-9]+","_",s.lower()).strip("_")
def sections(t):
 out=[]; cur="ROOT"; buf=[]
 for line in t.splitlines():
  if line.startswith("#"):
   if buf: out.append((cur,"\n".join(buf).strip()))
   cur=re.sub(r"^#+\s*","",line).strip();buf=[]
  else: buf.append(line)
 if buf: out.append((cur,"\n".join(buf).strip()))
 return [(h,b) for h,b in out if b]
def words(t): return set(re.findall(r"[a-z][a-z0-9'-]{3,}",t.lower()))
def similarity(a,b):
 return SequenceMatcher(None,sorted(words(a)),sorted(words(b))).ratio()
def subject_key(path,t):
 n=norm(path.stem)
 n=re.sub(r"_comparative$|_revision\d*$|_v\d+$|_draft\d*$","",n)
 for key,(base,terms) in ALIASES.items():
  if base in n or all(x in n for x in terms[:2]): return key
 low=t.lower()
 for key,(_,terms) in ALIASES.items():
  score=sum(low.count(x) for x in terms)
  if score>=8:return key
 return None
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--root",default=".");ap.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS");ap.add_argument("--scope");a=ap.parse_args();root=Path(a.root).resolve();base=root/a.scope if a.scope else root
 docs=[]
 for p in base.rglob("*.md"):
  rel=p.relative_to(root).as_posix()
  if any(x in SKIP for x in p.parts) or rel.startswith(ARCHIVE) or rel.startswith(REPORTS):continue
  t=p.read_text(encoding="utf-8",errors="replace");docs.append((rel,t,subject_key(p,t)))
 groups={}
 for rel,t,key in docs:
  if key: groups.setdefault(key,[]).append((rel,t))
 clusters=[]
 for key,items in groups.items():
  if len(items)<2:continue
  entries=[]
  for rel,t in items:
   entries.append({"path":rel,"sections":[h for h,_ in sections(t)],"word_count":len(words(t))})
  comparisons=[]
  for i,(ra,ta) in enumerate(items):
   for rb,tb in items[i+1:]:
    sa={norm(h):b for h,b in sections(ta)}; sb={norm(h):b for h,b in sections(tb)}
    added=sorted(set(sb)-set(sa)); removed=sorted(set(sa)-set(sb)); common=sorted(set(sa)&set(sb))
    changed=[h for h in common if similarity(sa[h],sb[h])<0.82]
    comparisons.append({"a":ra,"b":rb,"sections_only_in_a":removed,"sections_only_in_b":added,"changed_sections":changed,"overall_similarity":round(similarity(ta,tb),3)})
  clusters.append({"subject":key,"documents":entries,"comparisons":comparisons,"review_status":"UNRESOLVED"})
 out=root/a.out;out.mkdir(parents=True,exist_ok=True)
 data={"mode":"READ_ONLY","scope":a.scope or "ALL_ACTIVE_NON_GENERATED_CONTENT","clusters":len(clusters),"clusters_detail":clusters}
 (out/"CONTENT_LINEAGE_REPORT.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
 lines=["# ARUUN Content Lineage & Consolidation Audit","","**Mode:** READ-ONLY",f"**Scope:** `{a.scope or 'ALL_ACTIVE_NON_GENERATED_CONTENT'}`",f"**Lineage clusters:** {len(clusters)}","","## Review Protocol","","For each cluster, compare all source contributions before selecting an authoritative document. Allowed human decisions: `KEEP`, `MERGE`, `MOVE`, `LINK`, `ARCHIVE`, `UNRESOLVED`. No decision is made automatically.",""]
 for c in clusters:
  lines += [f"## {c['subject']}","", "### Sources"]+[f"- `{x['path']}` ({x['word_count']} indexed words; sections: {', '.join(x['sections']) or 'none'})" for x in c['documents']]
  for cmp in c['comparisons']:
   lines += ["",f"### Compare: `{cmp['a']}` ↔ `{cmp['b']}`",f"- Similarity: **{cmp['overall_similarity']}**",f"- Only in first: {', '.join(cmp['sections_only_in_a']) or 'none'}",f"- Only in second: {', '.join(cmp['sections_only_in_b']) or 'none'}",f"- Potentially changed sections: {', '.join(cmp['changed_sections']) or 'none'}"]
  lines += ["","**Human decision:** `UNRESOLVED`",""]
 (out/"CONTENT_LINEAGE_REPORT.md").write_text("\n".join(lines),encoding="utf-8")
 print(f"Identified {len(clusters)} subject lineage clusters.")
if __name__=="__main__":main()
