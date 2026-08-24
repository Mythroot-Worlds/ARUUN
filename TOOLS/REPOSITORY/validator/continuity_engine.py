#!/usr/bin/env python3
"""ARUUN read-only continuity engine.

Folder-dependent continuity analysis. It reports preserved, added, modified,
and potentially dropped information without deciding canon or mutating lore.
"""
from __future__ import annotations
import argparse, difflib, json, re, subprocess
from pathlib import Path

IGNORE_PARTS={".git",".github","__pycache__"}; DOC_EXTENSIONS={".md",".txt"}
GENERATED_PREFIXES=("TOOLS/REPOSITORY/REPORTS/",); ADMIN_PATH_PREFIXES=("00_MASTER/",)
ADMIN_FILENAMES={"CHANGELOG.md","README.md"}; TEST_PREFIXES=("TOOLS/REPOSITORY/CONTINUITY_TEST/",)
NUMBER_WORDS={"zero":"0","one":"1","two":"2","three":"3","four":"4","five":"5","six":"6","seven":"7","eight":"8","nine":"9","ten":"10","eleven":"11","twelve":"12","thirteen":"13","fourteen":"14","fifteen":"15","sixteen":"16","seventeen":"17","eighteen":"18","nineteen":"19","twenty":"20"}

def git(*args:str)->str:
    return subprocess.run(["git",*args],text=True,capture_output=True,check=True).stdout

def current_files(root:Path,scope:str|None=None)->list[Path]:
    base=root/scope if scope else root
    if not base.exists(): return []
    out=[]
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in DOC_EXTENSIONS: continue
        rel=p.relative_to(root).as_posix()
        if any(x in IGNORE_PARTS for x in p.parts) or rel.startswith(GENERATED_PREFIXES): continue
        out.append(p)
    return sorted(out)

def history_for(path:Path,root:Path,limit:int=20)->list[str]:
    try:return [x for x in git("log","--follow","--format=%H",f"-n{limit}","--",path.relative_to(root).as_posix()).splitlines() if x]
    except subprocess.CalledProcessError:return []

def old_content(commit:str,path:Path,root:Path)->str|None:
    try:return git("show",f"{commit}:{path.relative_to(root).as_posix()}")
    except subprocess.CalledProcessError:return None

def normalize(line:str)->str:
    return re.sub(r"\s+"," ",re.sub(r"[`*_#>-]"," ",line.lower())).strip()

def facts(text:str)->set[str]:
    return {n for n in (normalize(x) for x in text.splitlines()) if len(n)>=35 and not n.startswith(("status:","scope:","source:","---"))}

def numeric_tokens(text:str)->tuple[str,...]:
    t=normalize(text)
    for word,digit in NUMBER_WORDS.items(): t=re.sub(rf"\b{word}\b",digit,t)
    return tuple(re.findall(r"\b\d+(?:\.\d+)?%?\b",t))

def number_skeleton(line:str)->str:
    t=normalize(line)
    for word in NUMBER_WORDS: t=re.sub(rf"\b{word}\b","<NUM>",t)
    t=re.sub(r"\b\d+(?:\.\d+)?(?:\s*(?:%|million|billion|thousand|m|km|kg|g|years?|months?|days?|people))?\b","<NUM>",t)
    return re.sub(r"\s+"," ",t).strip()

def factual_numeric_changes(current:str,previous:str)->list[dict]:
    prev={}
    for raw in previous.splitlines():
        n=normalize(raw)
        if len(n)<20: continue
        tok=numeric_tokens(n)
        if tok: prev.setdefault(number_skeleton(n),set()).update(tok)
    changes=[]
    for raw in current.splitlines():
        n=normalize(raw); tok=numeric_tokens(n); sk=number_skeleton(n)
        if len(n)>=20 and tok and sk in prev and set(tok)!=prev[sk]: changes.append({"statement":n,"previous":sorted(prev[sk]),"current":sorted(set(tok))})
    return changes

def classify(path:Path,root:Path)->dict:
    rel=path.relative_to(root).as_posix(); parts=path.relative_to(root).parts
    return {"path":rel,"folder":"/".join(parts[:-1]),"filename":path.name,"archive":"07_ARCHIVE" in parts or "ARCHIVE" in parts,"tool":"TOOLS" in parts,"test_fixture":rel.startswith(TEST_PREFIXES),"administrative":rel.startswith(ADMIN_PATH_PREFIXES) or path.name in ADMIN_FILENAMES}

def compare(current:str,previous:str)->dict:
    cf,pf=facts(current),facts(previous); preserved=cf&pf; up=pf-preserved; uc=cf-preserved; modified=[]; usedp=set(); usedc=set()
    pairs=[]
    for p in up:
        best=""; score=0
        for c in uc:
            s=difflib.SequenceMatcher(None,p,c).ratio()
            if s>score: best,score=c,s
        if best and score>=.72: pairs.append((p,best,score))
    for p,c,s in sorted(pairs,key=lambda x:x[2],reverse=True):
        if p in usedp or c in usedc: continue
        usedp.add(p); usedc.add(c); modified.append({"previous":p,"current":c,"similarity":round(s,3)})
    return {"preserved":sorted(preserved),"added":sorted(uc-usedc),"potentially_dropped":sorted(up-usedp),"modified":modified,"numeric_fact_changes":factual_numeric_changes(current,previous),"similarity":round(difflib.SequenceMatcher(None,previous,current).ratio(),4)}

def analyze(path:Path,root:Path)->dict:
    current=path.read_text(encoding="utf-8",errors="replace"); info=classify(path,root); versions=[]
    for commit in history_for(path,root)[1:]:
        previous=old_content(commit,path,root)
        if previous is None or previous==current: continue
        cmp=compare(current,previous)
        versions.append({"commit":commit,**cmp,"overlay":list(difflib.unified_diff(previous.splitlines(),current.splitlines(),fromfile=f"previous:{commit[:12]}",tofile="current",lineterm=""))})
        if len(versions)>=5: break
    return {**info,"history_versions_checked":len(versions),"versions":versions}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--root",default="."); ap.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS"); ap.add_argument("--scope"); ap.add_argument("--include-test-fixtures",action="store_true"); args=ap.parse_args()
    root=Path(args.root).resolve(); out=root/args.out; out.mkdir(parents=True,exist_ok=True)
    records=[analyze(p,root) for p in current_files(root,args.scope)]; records=[r for r in records if not r["archive"]]; findings=[]
    for r in records:
        if r["administrative"] or (r["tool"] and not (args.include_test_fixtures and r["test_fixture"])): continue
        for v in r["versions"]:
            prefix="TEST_" if r["test_fixture"] else ""
            if v["potentially_dropped"]: findings.append({"type":prefix+"POTENTIAL_CANON_LOSS","severity":"REVIEW","path":r["path"],"folder":r["folder"],"commit":v["commit"],"dropped":v["potentially_dropped"][:50]})
            if v["modified"]: findings.append({"type":prefix+"MODIFIED_FACT","severity":"REVIEW","path":r["path"],"folder":r["folder"],"commit":v["commit"],"changes":v["modified"][:50]})
            if v["numeric_fact_changes"]: findings.append({"type":prefix+"NUMERIC_FACT_CHANGE","severity":"REVIEW","path":r["path"],"folder":r["folder"],"commit":v["commit"],"changes":v["numeric_fact_changes"][:50]})
    report={"mode":"READ_ONLY","scope":args.scope or "ALL_ACTIVE_NON_GENERATED_CONTENT","generated_reports_excluded":True,"administrative_documents_excluded_from_canon_findings":True,"test_fixtures_included":bool(args.include_test_fixtures),"documents":len(records),"findings":len(findings),"records":records,"findings_detail":findings}
    (out/"CONTINUITY_INDEX.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    lines=["# ARUUN Continuity Report","","**Mode:** READ-ONLY",f"**Scope:** `{args.scope or 'ALL_ACTIVE_NON_GENERATED_CONTENT'}`","**Generated reports excluded:** yes","**Administrative/master documents excluded from canon findings:** yes",f"**Test fixtures included:** {'yes' if args.include_test_fixtures else 'no'}","",f"Documents analyzed: {len(records)}",f"Continuity findings: {len(findings)}","",("No canon continuity findings were generated." if not findings else "## Findings\n")]
    for i,f in enumerate(findings,1):
        lines += [f"### {i}. {f['type']} — `{f['path']}`",f"- Historical commit: `{f['commit']}`"]
        if "dropped" in f: lines += [f"- Potentially dropped: {len(f['dropped'])}"]+[f"  - {x}" for x in f['dropped'][:10]]
        if "changes" in f:
            for c in f['changes'][:10]: lines.append(f"- `{c}`")
        lines.append("")
    (out/"CONTINUITY_REPORT.md").write_text("\n".join(lines),encoding="utf-8")
    overlays=[]
    for r in records:
        for v in r["versions"]:
            if not (v["overlay"] or v["modified"] or v["potentially_dropped"] or v["added"]): continue
            overlays += [f"## {r['path']} — `{v['commit'][:12]}`","",f"**Similarity:** {v['similarity']}","", "### Preserved", *[f"- {x}" for x in v['preserved'][:20]], "", "### Added", *[f"- {x}" for x in v['added'][:20]], "", "### Modified", *[f"- {x['previous']} → {x['current']}" for x in v['modified'][:20]], "", "### Potentially Dropped", *[f"- {x}" for x in v['potentially_dropped'][:20]], "", "### Unified Overlay", "```diff", *v['overlay'][:1200], "```", ""]
    (out/"CONTINUITY_OVERLAY.md").write_text("\n".join(overlays) if overlays else "# Continuity Overlay\n\nNo version differences require an overlay.\n",encoding="utf-8")
    queue=[f for f in findings if not f["type"].startswith("TEST_")]
    (out/"REVIEW_QUEUE.json").write_text(json.dumps({"mode":"HUMAN_REVIEW_REQUIRED","items":queue},indent=2),encoding="utf-8")
    return 0

if __name__=="__main__": raise SystemExit(main())
