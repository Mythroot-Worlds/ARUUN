#!/usr/bin/env python3
"""ARUUN read-only continuity engine with version overlays and review queue."""
from __future__ import annotations
import argparse,difflib,json,re,subprocess
from pathlib import Path
IGNORE_PARTS={".git",".github","__pycache__"}; EXT={".md",".txt"}
REPORTS="TOOLS/REPOSITORY/REPORTS/"; MASTER="00_MASTER/"; TEST="TOOLS/REPOSITORY/CONTINUITY_TEST/"
WORDS={"zero":"0","one":"1","two":"2","three":"3","four":"4","five":"5","six":"6","seven":"7","eight":"8","nine":"9","ten":"10","eleven":"11","twelve":"12","thirteen":"13","fourteen":"14","fifteen":"15","sixteen":"16","seventeen":"17","eighteen":"18","nineteen":"19","twenty":"20"}
def git(*a): return subprocess.run(["git",*a],text=True,capture_output=True,check=True).stdout
def files(root,scope=None):
 b=root/scope if scope else root; out=[]
 if not b.exists(): return out
 for p in b.rglob("*"):
  if p.is_file() and p.suffix.lower() in EXT:
   r=p.relative_to(root).as_posix()
   if not any(x in IGNORE_PARTS for x in p.parts) and not r.startswith(REPORTS): out.append(p)
 return sorted(out)
def hist(p,root):
 try:return [x for x in git("log","--follow","--format=%H","-n20","--",p.relative_to(root).as_posix()).splitlines() if x]
 except subprocess.CalledProcessError:return []
def old(c,p,root):
 try:return git("show",f"{c}:{p.relative_to(root).as_posix()}")
 except subprocess.CalledProcessError:return None
def norm(s): return re.sub(r"\s+"," ",re.sub(r"[`*_#>-]"," ",s.lower())).strip()
def facts(t): return {x for x in (norm(y) for y in t.splitlines()) if len(x)>=35 and not x.startswith(("status:","scope:","source:","---"))}
def nums(s):
 s=norm(s)
 for w,d in WORDS.items(): s=re.sub(rf"\b{w}\b",d,s)
 return tuple(re.findall(r"\b\d+(?:\.\d+)?%?\b",s))
def skeleton(s):
 s=norm(s)
 for w in WORDS: s=re.sub(rf"\b{w}\b","<NUM>",s)
 s=re.sub(r"\b\d+(?:\.\d+)?(?:\s*(?:%|million|billion|thousand|m|km|kg|g|years?|months?|days?|people))?\b","<NUM>",s)
 return re.sub(r"\s+"," ",s).strip()
def numeric_changes(cur,prev):
 pm={}
 for raw in prev.splitlines():
  n=norm(raw)
  if len(n)>=20 and nums(n): pm.setdefault(skeleton(n),set()).update(nums(n))
 out=[]
 for raw in cur.splitlines():
  n=norm(raw)
  if len(n)>=20 and nums(n) and skeleton(n) in pm and set(nums(n))!=pm[skeleton(n)]: out.append({"statement":n,"previous":sorted(pm[skeleton(n)]),"current":sorted(set(nums(n)))})
 return out
def compare(cur,prev):
 cf,pf=facts(cur),facts(prev); common=cf&pf; up=pf-common; uc=cf-common; mods=[]; usedp=set(); usedc=set()
 for p in up:
  best=max(((difflib.SequenceMatcher(None,p,c).ratio(),c) for c in uc),default=(0,""))
  if best[0]>=.72: mods.append({"previous":p,"current":best[1],"similarity":round(best[0],3)}); usedp.add(p); usedc.add(best[1])
 return {"preserved":sorted(common),"added":sorted(uc-usedc),"potentially_dropped":sorted(up-usedp),"modified":mods,"numeric_fact_changes":numeric_changes(cur,prev),"similarity":round(difflib.SequenceMatcher(None,prev,cur).ratio(),4)}
def analyze(p,root):
 cur=p.read_text(encoding="utf-8",errors="replace"); versions=[]
 for c in hist(p,root)[1:]:
  prev=old(c,p,root)
  if prev is None or prev==cur: continue
  x=compare(cur,prev); x["commit"]=c; x["overlay"]=list(difflib.unified_diff(prev.splitlines(),cur.splitlines(),fromfile=f"previous:{c[:12]}",tofile="current",lineterm="")); versions.append(x)
  if len(versions)>=5: break
 return {"path":p.relative_to(root).as_posix(),"versions":versions}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--root",default="."); ap.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS"); ap.add_argument("--scope"); ap.add_argument("--include-test-fixtures",action="store_true"); a=ap.parse_args(); root=Path(a.root).resolve(); out=root/a.out; out.mkdir(parents=True,exist_ok=True)
 rs=[analyze(p,root) for p in files(root,a.scope)]; findings=[]
 for r in rs:
  rel=r["path"]; admin=rel.startswith(MASTER) or Path(rel).name in {"CHANGELOG.md","README.md"}; fixture=rel.startswith(TEST)
  if admin or (fixture and not a.include_test_fixtures) or ("TOOLS/" in rel and not fixture): continue
  for v in r["versions"]:
   pre="TEST_" if fixture else ""
   if v["potentially_dropped"]: findings.append({"type":pre+"POTENTIAL_CANON_LOSS","path":rel,"commit":v["commit"],"items":v["potentially_dropped"][:50]})
   if v["modified"]: findings.append({"type":pre+"MODIFIED_FACT","path":rel,"commit":v["commit"],"items":v["modified"][:50]})
   if v["numeric_fact_changes"]: findings.append({"type":pre+"NUMERIC_FACT_CHANGE","path":rel,"commit":v["commit"],"items":v["numeric_fact_changes"][:50]})
 data={"mode":"READ_ONLY","scope":a.scope or "ALL_ACTIVE_NON_GENERATED_CONTENT","documents":len(rs),"findings":len(findings),"findings_detail":findings}
 (out/"CONTINUITY_INDEX.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
 lines=["# ARUUN Continuity Report","",f"**Scope:** `{a.scope or 'ALL_ACTIVE_NON_GENERATED_CONTENT'}`","**Mode:** READ-ONLY","",f"Documents analyzed: {len(rs)}",f"Continuity findings: {len(findings)}","", "No canon continuity findings were generated." if not findings else "## Findings\n"]
 for i,f in enumerate(findings,1):
  lines.append(f"### {i}. {f['type']} — `{f['path']}`")
  lines.append(f"- Historical commit: `{f['commit']}`")
  for item in f["items"][:10]: lines.append(f"- {item}")
  lines.append("")
 (out/"CONTINUITY_REPORT.md").write_text("\n".join(lines),encoding="utf-8")
 overlays=[]
 for r in rs:
  for v in r["versions"]:
   if not (v["overlay"] or v["modified"] or v["potentially_dropped"] or v["added"]): continue
   overlays += [f"## {r['path']} — `{v['commit'][:12]}`","",f"Similarity: {v['similarity']}","","### Preserved"]+[f"- {x}" for x in v["preserved"][:20]]+["","### Added"]+[f"- {x}" for x in v["added"][:20]]+["","### Modified"]+[f"- {x['previous']} → {x['current']}" for x in v["modified"][:20]]+["","### Potentially Dropped"]+[f"- {x}" for x in v["potentially_dropped"][:20]]+["","### Unified Overlay","```diff"]+v["overlay"][:1200]+["```",""]
 (out/"CONTINUITY_OVERLAY.md").write_text("\n".join(overlays) if overlays else "# Continuity Overlay\n\nNo version differences require an overlay.\n",encoding="utf-8")
 queue=[f for f in findings if not f["type"].startswith("TEST_")]; (out/"REVIEW_QUEUE.json").write_text(json.dumps({"mode":"HUMAN_REVIEW_REQUIRED","items":queue},indent=2),encoding="utf-8")
if __name__=="__main__": main()
