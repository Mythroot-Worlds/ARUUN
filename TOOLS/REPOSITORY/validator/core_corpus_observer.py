#!/usr/bin/env python3
"""CORE A.C.E. corpus observer: read-only document-understanding boundary."""
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
DOMAIN_TERMS={
    "WORLD":("planet","world","geography","continent","tectonic","climate","ocean","hydrology","atmosphere"),
    "ECOLOGY":("ecology","fauna","flora","creature","species","predator","prey","niche","biome","plant","animal"),
    "PEOPLES":("culture","people","population","kinship","family","governance","authority","belief","ritual","settlement","demographic"),
    "HISTORY":("history","historical","migration","era","ancestral","chronology","past"),
    "SYSTEMS":("system","technology","economy","exchange","agriculture","domestication","magic","rules"),
}
CULTURAL_TERMS={"HEARTH":("hearth","hearth-wide"),"PLAINS":("plains",),"MOUNTAINS":("mountains",),"RIVER":("river",),"WETLANDS":("wetlands","wetland"),"DESERT":("desert",),"COAST":("coast","coastal")}

def normalize(value):
    if value is None:return None
    value=re.sub(r"\s+"," ",value.strip());return value or None

def document_context(path):
    text=path.read_text(encoding="utf-8",errors="replace"); sample=text[:160000]; lines=sample.splitlines(); fields={}; in_frontmatter=bool(lines and lines[0].strip()=="---"); scan=lines[1:] if in_frontmatter else lines[:240]
    if in_frontmatter:
        for line in scan:
            if line.strip()=="---":break
            m=FIELD_RE.match(line)
            if m: fields[re.sub(r"\s+","_",m.group(1).lower())]=normalize(m.group(2)) or ""
    else:
        for line in scan:
            m=FIELD_RE.match(line)
            if m: fields.setdefault(re.sub(r"\s+","_",m.group(1).lower()),normalize(m.group(2)) or "")
    headings=[re.sub(r"^#+\s*","",line).strip() for line in lines if line.startswith("#")][:40]
    title=headings[0] if headings else None
    return {"sha256":hashlib.sha256(text.encode()).hexdigest(),"bytes":len(text.encode()),"fields":fields,"headings":headings,"title":title,"text":text}

def in_source_scope(root,path):
    rel=path.relative_to(root).as_posix()
    if any(part in EXCLUDED_DIRS for part in path.parts):return False
    if any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):return False
    upper="/"+rel.upper()+"/"
    if any(marker in upper for marker in EXCLUDED_RELEASE_MARKERS):return False
    return path.suffix.lower()==".md"

def content_scores(headings, info_units):
    corpus=" ".join(headings+[(u.get("text") or "") for u in info_units[:200]]).lower()
    domain_scores={d:sum(corpus.count(term) for term in terms) for d,terms in DOMAIN_TERMS.items()}
    cultural_scores={d:sum(corpus.count(term) for term in terms) for d,terms in CULTURAL_TERMS.items()}
    return domain_scores,cultural_scores

def best_score(scores, minimum=2):
    ranked=sorted(scores.items(),key=lambda kv:(kv[1],kv[0]),reverse=True)
    if not ranked or ranked[0][1]<minimum:return None
    if len(ranked)>1 and ranked[0][1]==ranked[1][1]:return None
    return ranked[0][0]

def content_identity(ctx, info_units):
    fields=ctx["fields"]; domain_scores,cultural_scores=content_scores(ctx["headings"],info_units)
    explicit_subject=fields.get("subject")
    title=ctx.get("title")
    subject=explicit_subject or title
    basis=[]
    if explicit_subject:basis.append("document field: subject")
    elif title:basis.append("document title heading")
    domain=fields.get("domain") or best_score(domain_scores)
    if fields.get("domain"):basis.append("document field: domain")
    elif domain:basis.append("content term/section evidence")
    scope=fields.get("cultural_scope") or fields.get("scope")
    if scope:basis.append("document field: scope")
    else:
        cultural=best_score(cultural_scores,minimum=3)
        if cultural:scope=cultural;basis.append("content cultural-scope evidence")
    confidence="HIGH" if explicit_subject and (fields.get("domain") or domain) else ("MEDIUM" if subject or domain or scope else "LOW")
    return {"subject":subject,"domain":domain,"cultural_scope":scope,"confidence":confidence,"basis":basis,"domain_scores":domain_scores,"cultural_scope_scores":cultural_scores}

def observe(root):
    records=[]
    for path in sorted(root.rglob("*.md")):
        if not in_source_scope(root,path):continue
        rel=path.relative_to(root).as_posix(); ctx=document_context(path); fields=ctx["fields"]
        info_units=extract_information_units(path,root)
        identity=resolve_artifact_identity(root,rel)
        explicit_authority=fields.get("authority") or fields.get("authority_layer"); explicit_status=fields.get("status") or fields.get("canonical_status")
        artifact_role=infer_artifact_role(layer=identity.get("layer"),authority=explicit_authority,path=rel,status=explicit_status)
        ci=content_identity(ctx,info_units)
        # Structural identity is retained as contextual evidence. If it came
        # only from path/filename, it is never promoted into the primary
        # document-understanding fields below.
        identity_context={k:v for k,v in identity.items() if k not in {"subject","role","purpose","scope","region","subregion","entity","population"}}
        records.append({"path":rel,"document":{"subject":ci["subject"],"domain":ci["domain"],"cultural_scope":ci["cultural_scope"],"population":fields.get("population"),"region":fields.get("region"),"subregion":fields.get("subregion"),"entity":fields.get("entity"),"purpose":fields.get("purpose"),"role":fields.get("role") or fields.get("document_role"),"status":explicit_status,"authority":explicit_authority},"document_understanding":{"confidence":ci["confidence"],"basis":ci["basis"],"domain_scores":ci["domain_scores"],"cultural_scope_scores":ci["cultural_scope_scores"],"title_heading":ctx.get("title")},"content_evidence":{"fields_observed":sorted(fields),"headings":ctx["headings"],"content_evidence_present":bool(fields or ctx["headings"] or info_units),"information_unit_count":len(info_units),"information_unit_sections":sorted({u["section"] for u in info_units}),"information_unit_fingerprints":[u["fingerprint"] for u in info_units[:200]]},"identity_context":identity_context,"artifact_role":artifact_role,"provenance":{"content_sha256":ctx["sha256"],"structural_identity_source":identity.get("identity_source"),"structural_identity_basis":identity.get("identity_basis",[]),"information_unit_source":"core_information_units.units","primary_identity_source":"document content / explicit document fields"}})
    return records

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--root",default=".");parser.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS");args=parser.parse_args();root=Path(args.root).resolve();out=root/args.out;out.mkdir(parents=True,exist_ok=True);records=observe(root)
    payload={"engine":"CORE A.C.E. Corpus Observer","phase":"1 — Corpus Inventory / document understanding","mode":"READ_ONLY","documents_in_scope":len(records),"documents":records,"safety":{"source_mutation":False,"canon_mutation":False,"working_material_promotion":False,"holdout_mutation":False,"automatic_placement":False,"generated_releases_as_sources":False,"filename_as_deciding_factor":False},"operating_principle":"Document content and explicit document metadata are primary evidence; path/filename identity is contextual evidence only.","downstream_contract":"Information units are extracted by the existing CORE information-unit engine and exposed as evidence for semantic/relationship engines; document understanding remains evidence-bearing and non-adjudicating."}
    (out/"CORE_CORPUS_OBSERVER.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    md=["# CORE A.C.E. Corpus Observer","","**Mode:** READ-ONLY","**Phase:** 1 — Corpus Inventory / document understanding","",f"Documents in scope: **{len(records)}**","","## Safety","- Source mutation: **OFF**","- Canon mutation: **OFF**","- Working-material promotion: **OFF**","- Holdout mutation: **OFF**","- Automatic placement: **OFF**","- Generated releases used as sources: **OFF**","- Filename as deciding factor: **OFF**","","## Observation contract","Document content and explicit document metadata are primary evidence. Structural identity and filenames are contextual evidence only.","","## Inventory"]
    for r in records:
        d=r["document"];u=r["document_understanding"];md.append(f"- `{r['path']}` — subject=`{d['subject'] or 'UNRESOLVED'}`, domain=`{d['domain'] or 'UNRESOLVED'}`, cultural_scope=`{d['cultural_scope'] or 'UNRESOLVED'}`, confidence=`{u['confidence']}`, artifact_role=`{r['artifact_role']}`, information_units=`{r['content_evidence']['information_unit_count']}`")
    (out/"CORE_CORPUS_OBSERVER.md").write_text("\n".join(md)+"\n",encoding="utf-8");print(f"CORE observer: {len(records)} source documents observed; document content is primary evidence; source mutation OFF.")
if __name__=="__main__":main()
