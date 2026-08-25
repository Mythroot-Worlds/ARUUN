#!/usr/bin/env python3
"""CORE read-only document disposition: explain what a document is and where it belongs."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from core_canonical_family import resolve as resolve_family
from core_document_naming import parse as parse_naming,status_for_role

REGIONS={"PLAINS","MOUNTAINS","RIVER","WETLANDS","DESERT","COAST"}
CULTURE_ROOT="03_PEOPLES/CULTURES/HEARTH"

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def canonical_region(identity):
    scope=identity.get('scope') or {}
    region=scope.get('region')
    if isinstance(region,str) and region.upper() in REGIONS:return region.upper()
    legacy=scope.get('regional_scope')
    if isinstance(legacy,str) and legacy.upper() in REGIONS:return legacy.upper()
    return None

def infer_destination(doc, identity, relationship="REVIEW", canonical_context=None):
    """Derive a canonical home from identity + family lineage, never pairwise keywords."""
    p=doc.upper().replace('\\','/')
    role=identity.get('role','UNKNOWN')
    lifecycle=identity.get('lifecycle_status')
    ctype=identity.get('content_type','')
    layer=identity.get('identity_layer','')
    region=canonical_region(identity)
    context=canonical_context or {}

    if role=='HISTORICAL' or lifecycle in {'ARCHIVE','HISTORICAL'} or '/07_ARCHIVE/' in p:
        return "07_ARCHIVE/HISTORICAL/"
    if role=='SUPPORTING' or 'COMPARATIVE' in p or context.get('document_layer')=='SUPPORTING':
        if ctype=='CULTURE' or context.get('canonical_domain')=='CULTURE':return f"{CULTURE_ROOT}/COMPARATIVE/"
        return None
    if ctype!='CULTURE':return None
    if region:return f"{CULTURE_ROOT}/{region}/"
    if layer=='CANONICAL_ROOT' or relationship in {'CANONICAL_ROOT','ROOT','BASE'}:
        return f"{CULTURE_ROOT}/"
    if relationship=='SUPPORTING':return f"{CULTURE_ROOT}/COMPARATIVE/"
    return None

def disposition(case):
    a=case.get('documents',{}).get('a',''); b=case.get('documents',{}).get('b','')
    ia=(case.get('identity') or {}).get('a',{}); ib=(case.get('identity') or {}).get('b',{})
    decision=case.get('decision','REVIEW'); canon=case.get('canonical_context') or {}; rows=[]
    for doc,ident in ((a,ia),(b,ib)):
        family=resolve_family(doc,ident); dest=infer_destination(doc,ident,decision,canon)
        action='REVIEW' if decision=='REVIEW' or dest is None else 'NO_MOVE_AUTOMATICALLY'
        naming=ident.get('naming') or parse_naming(doc)
        status_code=naming.get('status_code'); status_name=naming.get('status_name')
        if not status_code: status_code,status_name=status_for_role(ident.get('role'),ident.get('lifecycle_status'))
        basis=['canonical identity','canonical family lineage','domain/category','scope','document role','lifecycle','document naming/status rules']
        if dest:basis.append('domain-aware destination mapping')
        else:basis.append('no safe canonical destination inferred')
        rows.append({'document':doc,'canonical_subject':ident.get('subject'),'canonical_family_id':family.get('canonical_family_id'),'canonical_family_key':family.get('canonical_family_key'),'canonical_family_basis':family.get('canonical_family_basis'),'relation_to_family':family.get('relation_to_family'),'identity_layer':ident.get('identity_layer'),'domain_category':ident.get('content_type'),'context_scope':ident.get('scope'),'document_role':ident.get('role'),'lifecycle_status':ident.get('lifecycle_status'),'naming_normalized':naming.get('normalized',False),'status_code':status_code,'status_name':status_name,'relationship_class':decision,'recommended_destination':dest,'action':action,'evidence_basis':basis})
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    tri=load(out/'CORE_DOCUMENT_TRIAGE.json',{'cases':[]}); rows=[]
    for c in tri.get('cases',[]):rows.extend(disposition(c))
    summary={'documents':len(rows),'review':sum(r['action']=='REVIEW' for r in rows),'recommended_destinations':sum(bool(r['recommended_destination']) for r in rows),'automatic_moves':0,'regional_destinations':sum(bool(canonical_region({'scope':r.get('context_scope') or {}})) and bool(r.get('recommended_destination')) for r in rows),'canonical_root_documents':sum(r.get('identity_layer')=='CANONICAL_ROOT' for r in rows),'supporting_documents':sum(r.get('identity_layer')=='SUPPORTING_ARTIFACT' for r in rows),'historical_documents':sum(r.get('identity_layer')=='HISTORICAL_ARTIFACT' for r in rows),'normalized_names':sum(r.get('naming_normalized') for r in rows),'canonical_families':len({r['canonical_family_id'] for r in rows if r.get('canonical_family_id')}),'safety':'read-only; no canon or files are moved'}
    payload={'engine':'CORE A.C.E. Document Disposition','schema_version':'1.3','mode':'READ_ONLY','purpose':'turn canonical identity, family lineage, document layer, naming/status rules, and relationship decisions into explainable human-approved placement recommendations','documents':rows,'summary':summary,'safety':{'automatic_moves':False,'automatic_canon_change':False,'human_validation_required':True}}
    (out/'CORE_DOCUMENT_DISPOSITION.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    md=['# CORE Document Disposition','',f"Documents: {summary['documents']}",f"Review: {summary['review']}",f"Recommended destinations: {summary['recommended_destinations']}",f"Regional destinations: {summary['regional_destinations']}",f"Canonical root documents: {summary['canonical_root_documents']}",f"Supporting documents: {summary['supporting_documents']}",f"Historical documents: {summary['historical_documents']}",f"Normalized names: {summary['normalized_names']}",f"Canonical families: {summary['canonical_families']}",'','No files are moved automatically.']
    for r in rows: md += [f"## {r['document']}",f"- Subject: `{r['canonical_subject']}`",f"- Canonical family: `{r['canonical_family_id'] or 'UNRESOLVED'}` / `{r['canonical_family_key'] or 'UNRESOLVED'}`",f"- Family relation: `{r['relation_to_family']}`",f"- Identity layer: `{r['identity_layer']}`",f"- Category: `{r['domain_category']}`",f"- Scope: `{r['context_scope']}`",f"- Role: `{r['document_role']}`",f"- Naming normalized: `{r['naming_normalized']}`",f"- Status: `{r['status_code'] or '—'}` / `{r['status_name'] or '—'}`",f"- Relationship: `{r['relationship_class']}`",f"- Recommended destination: `{r['recommended_destination'] or 'REVIEW'}`",f"- Action: `{r['action']}`",f"- Evidence: {', '.join(r['evidence_basis'])}",'']
    (out/'CORE_DOCUMENT_DISPOSITION.md').write_text('\n'.join(md),encoding='utf-8');print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
