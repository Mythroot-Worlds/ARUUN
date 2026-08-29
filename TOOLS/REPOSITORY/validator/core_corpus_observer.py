#!/usr/bin/env python3
"""CORE A.C.E. corpus observer: read-only inventory/orchestration boundary.

The observer records document-derived evidence first and reuses the existing
CORE information-unit and artifact-identity layers. It does not decide canon,
final relationships, or placement, and it never treats filenames as decisions.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from core_artifact_identity import resolve_identity as resolve_artifact_identity
from core_artifact_roles import infer_artifact_role
from core_information_units import units as extract_information_units

EXCLUDED_DIRS={".git",".github","node_modules","__pycache__"}
EXCLUDED_PREFIXES=("TOOLS/REPOSITORY/REPORTS/","TOOLS/REPOSITORY/CONTINUITY_TEST/")
EXCLUDED_RELEASE_MARKERS=("/RELEASE/","/RELEASES/","_RELEASE")
FIELD_RE=re.compile(r"^\s*(?:[-#]\s*)?(subject|domain|scope|cultural[_ ]scope|population|region|subregion|entity|purpose|role|document[_ ]role|status|canonical[_ ]status|authority|authority[_ ]layer)\s*[:=-]\s*(.*?)\s*$",re.I)

def normalize(value):
    if value is None:return None
    value=re.sub(r"\s+"," ",value.strip());return value or None

def document_context(path):
    text=path.read_text(encoding="utf-8",errors="replace"); sample=text[:40000]; lines=sample.splitlines(); fields={}; in_frontmatter=bool(lines and lines[0].strip()=="---"); scan=lines[1:] if in_frontmatter else lines[:160]
    if in_frontmatter:
        for line in scan:
            if line.strip()=="---":break
            m=FIELD_RE.match(line)
            if m: fields[re.sub(r"\s+","_",m.group(1).lower())]=normalize(m.group(2)) or ""
    else:
        for line in scan:
            m=FIELD_RE.match(line)
            if m: fields.setdefault(re.sub(r"\s+","_",m.group(1).lower()),normalize(m.group(2)) or "")
    headings=[re.sub(r"^#+\s*","",line).strip() for line in lines if line.startswith("#")][:12]
    return {"sha256":hashlib.sha256(text.encode()).hexdigest(),"bytes":len(text.encode()),"fields":fields,"headings":headings,"content_evidence":bool(fields or headings)}

def in_source_scope(root,path):
    rel=path.relative_to(root).as_posix()
    if any(part in EXCLUDED_DIRS for part in path.parts):return False
    if any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):return False
    upper="/"+rel.upper()+"/"
    if any(marker in upper for marker in EXCLUDED_RELEASE_MARKERS):return False
    return path.suffix.lower()==".md"

def observe(root):
    records=[]
    for path in sorted(root.rglob("*.md")):
        if not in_source_scope(root,path):continue
        rel=path.relative_to(root).as_posix(); ctx=document_context(path); fields=ctx["fields"]
        identity=resolve_artifact_identity(root,rel)
        explicit_authority=fields.get("authority") or fields.get("authority_layer"); explicit_status=fields.get("status") or fields.get("canonical_status")
        artifact_role=infer_artifact_role(layer=identity.get("layer"),authority=explicit_authority,path=rel,status=explicit_status)
        # Reuse the established information-unit extractor rather than creating
        # a second prose parser here. These units are evidence, not decisions.
        info_units=extract_information_units(path,root)
        records.append({"path":rel,"document":{"subject":fields.get("subject"),"domain":fields.get("domain"),"cultural_scope":fields.get("cultural_scope") or fields.get("scope"),"population":fields.get("population"),"region":fields.get("region"),"subregion":fields.get("subregion"),"entity":fields.get("entity"),"purpose":fields.get("purpose"),"role":fields.get("role") or fields.get("document_role"),"status":explicit_status,"authority":explicit_authority},"content_evidence":{"fields_observed":sorted(fields),"headings":ctx["headings"],"content_evidence_present":ctx["content_evidence"],"information_unit_count":len(info_units),"information_unit_sections":sorted({u["section"] for u in info_units}),"information_unit_fingerprints":[u["fingerprint"] for u in info_units[:200]]},"identity":identity,"artifact_role":artifact_role,"provenance":{"content_sha256":ctx["sha256"],"identity_basis":identity.get("identity_basis",[]),"identity_source":identity.get("identity_source",{}),"information_unit_source":"core_information_units.units"}})
    return records

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--root",default=".");parser.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS");args=parser.parse_args();root=Path(args.root).resolve();out=root/args.out;out.mkdir(parents=True,exist_ok=True);records=observe(root)
    payload={"engine":"CORE A.C.E. Corpus Observer","phase":"1 — Corpus Inventory / observation boundary","mode":"READ_ONLY","documents_in_scope":len(records),"documents":records,"safety":{"source_mutation":False,"canon_mutation":False,"working_material_promotion":False,"holdout_mutation":False,"automatic_placement":False,"generated_releases_as_sources":False,"filename_as_deciding_factor":False},"operating_principle":"Document information is primary evidence; path/filename identity is contextual evidence, never a deciding factor by itself.","downstream_contract":"Information units are extracted by the existing CORE information-unit engine and exposed as evidence for semantic/relationship engines; this observer does not adjudicate them."}
    (out/"CORE_CORPUS_OBSERVER.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    md=["# CORE A.C.E. Corpus Observer","","**Mode:** READ-ONLY","**Phase:** 1 — Corpus Inventory / observation boundary","",f"Documents in scope: **{len(records)}**","","## Safety","- Source mutation: **OFF**","- Canon mutation: **OFF**","- Working-material promotion: **OFF**","- Holdout mutation: **OFF**","- Automatic placement: **OFF**","- Generated releases used as sources: **OFF**","- Filename as deciding factor: **OFF**","","## Observation contract","Document-derived information is recorded first. Existing structural/artifact identity and the established information-unit extractor are contextual evidence for downstream engines; unresolved information remains unresolved.","","## Inventory"]
    for r in records:
        d=r["document"];md.append(f"- `{r['path']}` — subject=`{d['subject'] or 'UNRESOLVED'}`, domain=`{d['domain'] or 'UNRESOLVED'}`, cultural_scope=`{d['cultural_scope'] or 'UNRESOLVED'}`, authority=`{d['authority'] or 'UNRESOLVED'}`, artifact_role=`{r['artifact_role']}`, information_units=`{r['content_evidence']['information_unit_count']}`")
    (out/"CORE_CORPUS_OBSERVER.md").write_text("\n".join(md)+"\n",encoding="utf-8");print(f"CORE observer: {len(records)} source documents observed; source mutation OFF.")
if __name__=="__main__":main()
