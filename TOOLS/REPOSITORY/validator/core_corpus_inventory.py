#!/usr/bin/env python3
"""CORE A.C.E. Phase 1 — deterministic, read-only ARUUN corpus inventory."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from core_document_identity import identify

EXCLUDED_TOP={"TOOLS",".GITHUB",".GIT"}
EXCLUDED_PARTS={"08_RELEASES","REPORTS"}
INCLUDED_EXTENSIONS={".md",".yaml",".yml",".json"}
STATUS_MAP={"C":"CANON","CANON":"CANON","P":"PROVISIONAL","PROVISIONAL":"PROVISIONAL","O":"OPEN","OPEN":"OPEN","X":"CONFLICTED","CONFLICTED":"CONFLICTED","D":"DEPRECATED","DEPRECATED":"DEPRECATED"}
NON_AUTH_PATH_MARKERS=("HISTORICAL","ARCHIVE","LEGACY","SUPERSEDED","PREVIOUS")
SUPPORTING_MARKERS=("CHECKLIST","AUDIT","FRAMEWORK","GUIDE","REFERENCE","OPERATING_RULES","COMPARATIVE")
DOMAIN_BY_TOP={"00_MASTER":"MASTER","01_WORLD":"WORLD","02_ECOLOGY":"ECOLOGY","03_PEOPLES":"PEOPLES","04_HISTORY":"HISTORY","05_SYSTEMS":"SYSTEMS","06_WORKING":"WORKING","07_ARCHIVE":"ARCHIVE","08_RELEASES":"RELEASES"}

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

def status_from_meta(meta):
    for key in ("status","lifecycle"):
        val=norm(meta.get(key))
        if val in STATUS_MAP:return STATUS_MAP[val]
    return None

def role_from_inventory(rel,identity,meta):
    u=rel.upper(); status=status_from_meta(meta)
    # Explicit lifecycle/status and archive location outrank generic filename heuristics.
    if status=="DEPRECATED" or any(x in u for x in NON_AUTH_PATH_MARKERS): return "HISTORICAL"
    if status in {"PROVISIONAL","OPEN","CONFLICTED"}: return "NON_CANONICAL"
    if str(meta.get("canonical","")).strip().lower()=="false": return "NON_CANONICAL"
    if identity.get("role")=="SUPPORTING" or any(x in u for x in SUPPORTING_MARKERS): return "SUPPORTING"
    if status=="CANON": return "AUTHORITATIVE"
    # Existing identity is a fallback only when no explicit metadata contradicts it.
    return identity.get("role","UNKNOWN")

def authority_from_role(role,status,meta):
    if role=="HISTORICAL":return "HISTORICAL"
    if role=="SUPPORTING":return "SUPPORTING"
    if status in {"PROVISIONAL","OPEN","CONFLICTED","DEPRECATED"}:return status
    if str(meta.get("canonical","")).strip().lower()=="false":return "NON_CANONICAL"
    if status=="CANON":return "CANON"
    return "UNRESOLVED"

def domain_from_path(rel,meta,identity):
    parts=Path(rel).parts
    top=parts[0].upper() if parts else ""
    explicit=norm(meta.get("domain"))
    # Do not allow a filename to masquerade as a domain.
    if explicit and explicit.lower().endswith(('.md','.yaml','.yml','.json')): explicit=""
    return explicit or DOMAIN_BY_TOP.get(top) or identity.get("content_type") or "UNKNOWN"

def inventory(root):
    docs=[]
    for path in sorted(root.rglob("*"),key=lambda p:p.relative_to(root).as_posix().lower()):
        if not path.is_file() or not eligible(path,root):continue
        rel=path.relative_to(root).as_posix(); identity=identify(rel); meta=front_matter(path)
        status=status_from_meta(meta); role=role_from_inventory(rel,identity,meta)
        docs.append({"path":rel,"front_matter":meta,"status":status or (meta.get("status") or meta.get("lifecycle") or None),"domain":domain_from_path(rel,meta,identity),"cultural_scope":meta.get("scope") or identity.get("scope"),"subject":meta.get("subject") or identity.get("subject"),"content_type":identity.get("content_type"),"role":role,"identity_layer":identity.get("identity_layer"),"authority_layer":authority_from_role(role,status,meta),"naming":identity.get("naming"),"identity_basis":identity.get("identity_basis"),"identity_confidence":identity.get("identity_confidence"),"provenance":{"source_path":rel,"sha256":sha256(path)}})
    return docs

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",default="."); ap.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS"); args=ap.parse_args(); root=Path(args.root).resolve(); out=root/args.out; out.mkdir(parents=True,exist_ok=True)
    docs=inventory(root); payload={"engine":"CORE A.C.E.","phase":"PHASE_1_CORPUS_INVENTORY","mode":"READ_ONLY","document_count":len(docs),"documents":docs,"safety":{"source_mutation":False,"canon_mutation":False,"working_material_promotion":False,"holdout_mutation":False,"automatic_placement":False}}
    raw=json.dumps(payload,indent=2,sort_keys=True)+"\n"; digest=hashlib.sha256(raw.encode()).hexdigest(); payload["inventory_sha256"]=digest
    (out/"CORE_CORPUS_INVENTORY.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    counts=lambda key:{k:sum(1 for d in docs if d.get(key)==k) for k in sorted({d.get(key) or "UNKNOWN" for d in docs})}
    lines=["# CORE A.C.E. Corpus Inventory","","**Phase:** 1 — Corpus Inventory  ","**Mode:** READ-ONLY  ",f"**Documents in source corpus:** {len(docs)}  ",f"**Inventory SHA-256:** `{digest}`","","## Safety","- Source mutation: **OFF**","- Canon mutation: **OFF**","- Working-material promotion: **OFF**","- Holdout mutation: **OFF**","- Automatic placement: **OFF**","","## Summary by domain"]
    for k,v in counts("domain").items():lines.append(f"- `{k}`: **{v}**")
    lines += ["","## Summary by role"]
    for k,v in counts("role").items():lines.append(f"- `{k}`: **{v}**")
    lines += ["","## Summary by authority"]
    for k,v in counts("authority_layer").items():lines.append(f"- `{k}`: **{v}**")
    lines += ["","## Inventory entries"]
    for d in docs:lines.append(f"- `{d['path']}` — subject=`{d['subject']}`, domain=`{d['domain']}`, type=`{d['content_type']}`, role=`{d['role']}`, authority=`{d['authority_layer']}`")
    (out/"CORE_CORPUS_INVENTORY.md").write_text("\n".join(lines)+"\n",encoding="utf-8"); print(f"CORE A.C.E. Phase 1: inventoried {len(docs)} source documents; inventory digest {digest}.")
if __name__=="__main__":main()
