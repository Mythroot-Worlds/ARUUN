#!/usr/bin/env python3
"""CORE A.C.E. Phase 1: deterministic, read-only corpus inventory."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from core_document_identity import identify

EXCLUDED_TOP={"TOOLS",".GITHUB",".GIT"}
EXCLUDED_PARTS={"08_RELEASES","REPORTS"}
INCLUDED_EXTENSIONS={".md",".yaml",".yml",".json"}
STATUS_MAP={"C":"CANON","CANON":"CANON","P":"PROVISIONAL","PROVISIONAL":"PROVISIONAL","O":"OPEN","OPEN":"OPEN","X":"CONFLICTED","CONFLICTED":"CONFLICTED","D":"RETIRED","DEPRECATED":"RETIRED","RETIRED":"RETIRED"}
CANON_TAXONOMY={"LOCKED CANON":"LOCKED_CANON","FLEXIBLE / PROVISIONAL":"PROVISIONAL","FLEXIBLE-PROVISIONAL":"PROVISIONAL","OPEN":"OPEN","UNKNOWN":"UNKNOWN","WORKING INFERENCE":"WORKING_INFERENCE","RETIRED":"RETIRED"}
DOMAIN_BY_TOP={"00_MASTER":"MASTER","01_WORLD":"WORLD","02_ECOLOGY":"ECOLOGY","03_PEOPLES":"PEOPLES","04_HISTORY":"HISTORY","05_SYSTEMS":"SYSTEMS","06_WORKING":"WORKING","07_ARCHIVE":"ARCHIVE","08_RELEASES":"RELEASES"}
SUPPORTING_MARKERS=("CHECKLIST","AUDIT","FRAMEWORK","GUIDE","REFERENCE","OPERATING_RULES","COMPARATIVE","CREATION_PACKAGE")

def eligible(path,root):
    rel=path.relative_to(root); parts=[p.upper() for p in rel.parts]
    return path.suffix.lower() in INCLUDED_EXTENSIONS and parts[0] not in EXCLUDED_TOP and not any(p in EXCLUDED_PARTS for p in parts[:-1])

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def front_matter(path):
    try:text=path.read_text(encoding="utf-8")
    except UnicodeDecodeError:return {}
    if not text.startswith("---\n"):return {}
    end=text.find("\n---",4)
    if end<0:return {}
    data={}
    for line in text[4:end].splitlines():
        if ":" not in line:continue
        k,v=line.split(":",1); data[k.strip().lower()]=v.strip().strip("\"'")
    return data

def norm(v):return str(v or "").strip().upper()

def meta_status(meta):
    raw=norm(meta.get("status") or meta.get("lifecycle"))
    return STATUS_MAP.get(raw)

def parse_index(root):
    """Read CANON_INDEX as authority evidence, never as source canon."""
    p=root/"00_MASTER/CANON_INDEX.md"
    if not p.exists():return {}
    text=p.read_text(encoding="utf-8",errors="replace")
    evidence={}
    for line in text.splitlines():
        paths=re.findall(r"`([^`]+)`",line)
        if not paths or "|" not in line:continue
        rhs=line.split("|",1)[1].strip().lower()
        found=[]
        for phrase,status in sorted(CANON_TAXONOMY.items(),key=lambda x:-len(x[0])):
            if phrase.lower() in rhs:found.append((status,phrase))
        if not found: continue
        status,phrase=found[0]
        for token in paths:
            if token.endswith("/") or "*" in token: continue
            token=token.strip()
            if token.startswith("Aruun/"):token=token[6:]
            evidence.setdefault(token,[]).append({"source":"00_MASTER/CANON_INDEX.md","status":status,"statement":line.strip()})
    return evidence

def bible_evidence(root):
    p=root/"00_MASTER/WORLD_BIBLE.md"
    if not p.exists():return []
    text=p.read_text(encoding="utf-8",errors="replace")
    return [{"source":"00_MASTER/WORLD_BIBLE.md","status":"LOCKED_CANON","statement":"Current authoritative World Bible for development."}] if re.search(r"\*\*Status:\*\*\s*Current authoritative World Bible",text,re.I) else []

def authority_evidence(rel,meta,identity,index,bible):
    ev=[]
    ms=meta_status(meta)
    if ms:ev.append({"source":"front_matter","status":ms})
    if str(meta.get("canonical","")).strip().lower()=="false":ev.append({"source":"front_matter","status":"NON_CANONICAL"})
    for x in index.get(rel,[]):ev.append(x)
    # Explicit master-world special cases are grounded in the index/Bible, not filename heuristics.
    if rel=="00_MASTER/WORLD_BIBLE.md":ev += bible
    if rel=="00_MASTER/FOUNDATION_WORLD_PROFILE.md":ev.append({"source":"00_MASTER/CANON_INDEX.md","status":"LOCKED_CANON","statement":"LOCKED CANON — original world concept, foundation reference."})
    statuses={x["status"] for x in ev if x.get("status")}
    return ev,statuses

def canonical_status(ev,statuses):
    if not statuses:return "UNRESOLVED"
    # NON_CANONICAL is an explicit negative assertion and conflicts with a positive canon assertion.
    positive={"LOCKED_CANON","CANON","PROVISIONAL","OPEN","UNKNOWN","WORKING_INFERENCE","RETIRED"}
    if "NON_CANONICAL" in statuses and statuses & positive:return "REVIEW"
    if "NON_CANONICAL" in statuses:return "NON_CANONICAL"
    if len(statuses)>1:return "REVIEW"
    return next(iter(statuses))

def role_from_inventory(rel,identity,meta,canon_status):
    u=rel.upper()
    if canon_status in {"RETIRED","HISTORICAL"} or "/ARCHIVE/" in "/"+u+"/":return "HISTORICAL"
    if canon_status in {"PROVISIONAL","OPEN","UNKNOWN","WORKING_INFERENCE","NON_CANONICAL"}:return "NON_CANONICAL"
    if canon_status=="LOCKED_CANON":return "AUTHORITATIVE"
    if identity.get("role")=="SUPPORTING" or any(x in u for x in SUPPORTING_MARKERS):return "SUPPORTING"
    return identity.get("role","UNKNOWN")

def domain_from_path(rel,meta,identity):
    parts=Path(rel).parts; top=parts[0].upper() if parts else ""
    explicit=str(meta.get("domain") or "").strip()
    if explicit and explicit.lower().endswith(('.md','.yaml','.yml','.json')):explicit=""
    return explicit.upper() if explicit else DOMAIN_BY_TOP.get(top) or identity.get("content_type") or "UNKNOWN"

def inventory(root):
    index=parse_index(root); bible=bible_evidence(root); docs=[]
    for path in sorted(root.rglob("*"),key=lambda p:p.relative_to(root).as_posix().lower()):
        if not path.is_file() or not eligible(path,root):continue
        rel=path.relative_to(root).as_posix(); identity=identify(rel); meta=front_matter(path)
        ev,statuses=authority_evidence(rel,meta,identity,index,bible); cstatus=canonical_status(ev,statuses); role=role_from_inventory(rel,identity,meta,cstatus)
        docs.append({"path":rel,"front_matter":meta,"status":meta.get("status") or meta.get("lifecycle"),"domain":domain_from_path(rel,meta,identity),"cultural_scope":meta.get("scope") or identity.get("scope"),"subject":meta.get("subject") or identity.get("subject"),"content_type":identity.get("content_type"),"role":role,"identity_layer":identity.get("identity_layer"),"canonical_status":cstatus,"authority_layer":cstatus,"authority_evidence":ev,"authority_evidence_count":len(ev),"naming":identity.get("naming"),"identity_basis":identity.get("identity_basis"),"identity_confidence":identity.get("identity_confidence"),"provenance":{"source_path":rel,"sha256":sha256(path)}})
    return docs

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--root",default=".");ap.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS");a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out;out.mkdir(parents=True,exist_ok=True)
    docs=inventory(root);payload={"engine":"CORE A.C.E.","phase":"PHASE_1_CORPUS_INVENTORY","mode":"READ_ONLY","document_count":len(docs),"documents":docs,"safety":{"source_mutation":False,"canon_mutation":False,"working_material_promotion":False,"holdout_mutation":False,"automatic_placement":False}}
    raw=json.dumps(payload,indent=2,sort_keys=True)+"\n";digest=hashlib.sha256(raw.encode()).hexdigest();payload["inventory_sha256"]=digest
    (out/"CORE_CORPUS_INVENTORY.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    counts=lambda key:{k:sum(1 for d in docs if d.get(key)==k) for k in sorted({d.get(key) or "UNRESOLVED" for d in docs})}
    lines=["# CORE A.C.E. Corpus Inventory","","**Phase:** 1 — Corpus Inventory  ","**Mode:** READ-ONLY  ",f"**Documents in source corpus:** {len(docs)}  ",f"**Inventory SHA-256:** `{digest}`","","## Safety","- Source mutation: **OFF**","- Canon mutation: **OFF**","- Working-material promotion: **OFF**","- Holdout mutation: **OFF**","- Automatic placement: **OFF**","","## Summary by canonical status"]
    for k,v in counts("canonical_status").items():lines.append(f"- `{k}`: **{v}**")
    lines += ["","## Summary by role"]
    for k,v in counts("role").items():lines.append(f"- `{k}`: **{v}**")
    lines += ["","## Summary by domain"]
    for k,v in counts("domain").items():lines.append(f"- `{k}`: **{v}**")
    lines += ["","## Review cases"]
    for d in docs:
        if d["canonical_status"]=="REVIEW":lines.append(f"- `{d['path']}` — conflicting authority evidence; human review required")
    lines += ["","## Inventory entries"]
    for d in docs:lines.append(f"- `{d['path']}` — subject=`{d['subject']}`, domain=`{d['domain']}`, type=`{d['content_type']}`, role=`{d['role']}`, canonical_status=`{d['canonical_status']}`, evidence={d['authority_evidence_count']}")
    (out/"CORE_CORPUS_INVENTORY.md").write_text("\n".join(lines)+"\n",encoding="utf-8");print(f"CORE A.C.E. Phase 1: inventoried {len(docs)} source documents; inventory digest {digest}.")
if __name__=="__main__":main()
