#!/usr/bin/env python3
"""CORE read-only document disposition: explain what a document is and where it belongs."""
from __future__ import annotations
import argparse,json
from pathlib import Path

REGIONS={"PLAINS","MOUNTAINS","RIVER","WETLANDS","DESERT","COAST"}

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def infer_destination(doc, identity, relationship, counterpart=""):
    p=doc.upper().replace('\\','/')
    role=identity.get('role','UNKNOWN'); scope=identity.get('scope') or {}
    region=scope.get('regional_scope')
    subject=identity.get('subject','')
    ctype=identity.get('content_type','')
    if '/03_PEOPLES/CULTURES/HEARTH/' in p and region:
        return f"03_PEOPLES/CULTURES/HEARTH/{region}/"
    if role=='SUPPORTING' or 'COMPARATIVE' in p:
        return "03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/"
    if role=='HISTORICAL' or '/07_ARCHIVE/' in p:
        return "07_ARCHIVE/HISTORICAL/"
    if region and ctype=='CULTURE':
        return f"03_PEOPLES/CULTURES/HEARTH/{region}/"
    return None

def disposition(case):
    a=case.get('documents',{}).get('a',''); b=case.get('documents',{}).get('b','')
    ia=(case.get('identity') or {}).get('a',{}); ib=(case.get('identity') or {}).get('b',{})
    decision=case.get('decision','REVIEW')
    rows=[]
    for doc,ident,other in ((a,ia,b),(b,ib,a)):
        dest=infer_destination(doc,ident,decision,other)
        rows.append({'document':doc,'canonical_subject':ident.get('subject'),'domain_category':ident.get('content_type'),'context_scope':ident.get('scope'),'document_role':ident.get('role'),'lifecycle_status':ident.get('lifecycle_status'),'relationship_class':decision,'recommended_destination':dest,'action':'REVIEW' if decision=='REVIEW' or dest is None else 'NO_MOVE_AUTOMATICALLY','evidence_basis':'canonical identity + layered relationship + document role/scope'})
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    tri=load(out/'CORE_DOCUMENT_TRIAGE.json',{'cases':[]})
    rows=[]
    for c in tri.get('cases',[]): rows.extend(disposition(c))
    summary={'documents':len(rows),'review':sum(r['action']=='REVIEW' for r in rows),'recommended_destinations':sum(bool(r['recommended_destination']) for r in rows),'automatic_moves':0,'safety':'read-only; no canon or files are moved'}
    payload={'engine':'CORE A.C.E. Document Disposition','schema_version':'1.0','mode':'READ_ONLY','purpose':'turn canonical identity and relationship decisions into explainable human-approved placement recommendations','documents':rows,'summary':summary,'safety':{'automatic_moves':False,'automatic_canon_change':False,'human_validation_required':True}}
    (out/'CORE_DOCUMENT_DISPOSITION.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    md=['# CORE Document Disposition','',f"Documents: {summary['documents']}",f"Review: {summary['review']}",f"Recommended destinations: {summary['recommended_destinations']}",'','No files are moved automatically.']
    for r in rows:
        md += [f"## {r['document']}",f"- Subject: `{r['canonical_subject']}`",f"- Category: `{r['domain_category']}`",f"- Scope: `{r['context_scope']}`",f"- Role: `{r['document_role']}`",f"- Relationship: `{r['relationship_class']}`",f"- Recommended destination: `{r['recommended_destination'] or 'REVIEW'}`",f"- Action: `{r['action']}`",'']
    (out/'CORE_DOCUMENT_DISPOSITION.md').write_text('\n'.join(md),encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
