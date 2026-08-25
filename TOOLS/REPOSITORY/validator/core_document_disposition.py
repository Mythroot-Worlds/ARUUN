#!/usr/bin/env python3
"""CORE read-only document disposition: explain what a document is and where it belongs."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from core_canonical_family import resolve as resolve_family

REGIONS={"PLAINS","MOUNTAINS","RIVER","WETLANDS","DESERT","COAST"}
CULTURE_ROOT="03_PEOPLES/CULTURES/HEARTH"

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def canonical_region(identity):
    """Return the actual region name; regional_scope is only a boolean flag."""
    scope=identity.get('scope') or {}
    region=scope.get('region')
    if isinstance(region,str) and region.upper() in REGIONS:
        return region.upper()
    legacy=scope.get('regional_scope')
    if isinstance(legacy,str) and legacy.upper() in REGIONS:
        return legacy.upper()
    return None

def infer_destination(doc, identity, relationship="REVIEW", canonical_context=None):
    """Derive a canonical home from identity + family lineage, never pairwise keywords."""
    p=doc.upper().replace('\\','/')
    role=identity.get('role','UNKNOWN')
    lifecycle=identity.get('lifecycle_status')
    ctype=identity.get('content_type','')
    region=canonical_region(identity)
    context=canonical_context or {}
    family=resolve_family(doc, identity)

    if role=='HISTORICAL' or lifecycle in {'ARCHIVE','HISTORICAL'} or '/07_ARCHIVE/' in p:
        return "07_ARCHIVE/HISTORICAL/"

    if role=='SUPPORTING' or 'COMPARATIVE' in p or context.get('document_layer')=='SUPPORTING':
        if ctype=='CULTURE' or context.get('canonical_domain')=='CULTURE':
            return f"{CULTURE_ROOT}/COMPARATIVE/"
        return None

    if ctype!='CULTURE':
        return None

    if region:
        return f"{CULTURE_ROOT}/{region}/"

    if relationship=='SUPPORTING':
        return f"{CULTURE_ROOT}/COMPARATIVE/"
    return None

def disposition(case):
    a=case.get('documents',{}).get('a',''); b=case.get('documents',{}).get('b','')
    ia=(case.get('identity') or {}).get('a',{}); ib=(case.get('identity') or {}).get('b',{})
    decision=case.get('decision','REVIEW')
    canon=case.get('canonical_context') or {}
    rows=[]
    for doc,ident,other in ((a,ia,b),(b,ib,a)):
        family=resolve_family(doc,ident)
        dest=infer_destination(doc,ident,decision,canon)
        action='REVIEW' if decision=='REVIEW' or dest is None else 'NO_MOVE_AUTOMATICALLY'
        basis=['canonical identity','canonical family lineage','domain/category','scope','document role','lifecycle']
        if dest: basis.append('domain-aware destination mapping')
        else: basis.append('no safe canonical destination inferred')
        rows.append({'document':doc,'canonical_subject':ident.get('subject'),'canonical_family_id':family.get('canonical_family_id'),'canonical_family_key':family.get('canonical_family_key'),'canonical_family_basis':family.get('canonical_family_basis'),'relation_to_family':family.get('relation_to_family'),'domain_category':ident.get('content_type'),'context_scope':ident.get('scope'),'document_role':ident.get('role'),'lifecycle_status':ident.get('lifecycle_status'),'relationship_class':decision,'recommended_destination':dest,'action':action,'evidence_basis':basis})
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    tri=load(out/'CORE_DOCUMENT_TRIAGE.json',{'cases':[]})
    rows=[]
    for c in tri.get('cases',[]): rows.extend(disposition(c))
    summary={'documents':len(rows),'review':sum(r['action']=='REVIEW' for r in rows),'recommended_destinations':sum(bool(r['recommended_destination']) for r in rows),'automatic_moves':0,'regional_destinations':sum(bool(canonical_region({'scope':r.get('context_scope') or {}})) and bool(r.get('recommended_destination')) for r in rows),'canonical_families':len({r['canonical_family_id'] for r in rows if r.get('canonical_family_id')}),'safety':'read-only; no canon or files are moved'}
    payload={'engine':'CORE A.C.E. Document Disposition','schema_version':'1.2','mode':'READ_ONLY','purpose':'turn canonical identity, family lineage, and relationship decisions into explainable human-approved placement recommendations','documents':rows,'summary':summary,'safety':{'automatic_moves':False,'automatic_canon_change':False,'human_validation_required':True}}
    (out/'CORE_DOCUMENT_DISPOSITION.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    md=['# CORE Document Disposition','',f"Documents: {summary['documents']}",f"Review: {summary['review']}",f"Recommended destinations: {summary['recommended_destinations']}",f"Regional destinations: {summary['regional_destinations']}",f"Canonical families: {summary['canonical_families']}",'','No files are moved automatically.']
    for r in rows:
        md += [f"## {r['document']}",f"- Subject: `{r['canonical_subject']}`",f"- Canonical family: `{r['canonical_family_id'] or 'UNRESOLVED'}` / `{r['canonical_family_key'] or 'UNRESOLVED'}`",f"- Family relation: `{r['relation_to_family']}`",f"- Category: `{r['domain_category']}`",f"- Scope: `{r['context_scope']}`",f"- Role: `{r['document_role']}`",f"- Relationship: `{r['relationship_class']}`",f"- Recommended destination: `{r['recommended_destination'] or 'REVIEW'}`",f"- Action: `{r['action']}`",f"- Evidence: {', '.join(r['evidence_basis'])}",'']
    (out/'CORE_DOCUMENT_DISPOSITION.md').write_text('\n'.join(md),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
