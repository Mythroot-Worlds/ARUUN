#!/usr/bin/env python3
"""Apply the evidence-gated VARIANT test to discovered document pairs.

This is a pre-adjudication gate, not a final relationship classifier. It reads
semantic claims and document context, annotates discovery candidates, and keeps
legacy/human labels separate from current engine resolution.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from core_variant_arbitration import assess_variant

ARCHIVE_PARTS={'.git','.github','TOOLS','07_ARCHIVE','node_modules','__pycache__'}

def load(p, default):
    try:
        return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default
    except Exception:
        return default

def front_context(path: Path) -> dict:
    try: body=path.read_text(encoding='utf-8',errors='replace')[:30000]
    except Exception: return {}
    ctx={'subject':None,'scope':None,'time':None,'purpose':None,'role':None,'claims':[]}
    lines=body.splitlines()
    # Conservative metadata extraction. Never invent values from filenames alone.
    for line in lines[:80]:
        m=re.match(r'^\s*[-#]*\s*(subject|scope|time|date|purpose|role|document\s*role|type)\s*[:=-]\s*(.+?)\s*$',line,re.I)
        if not m: continue
        key=re.sub(r'\s+','_',m.group(1).lower())
        val=m.group(2).strip()
        if key in ('date',): key='time'
        if key in ('document_role','type'): key='role'
        if key in ctx and val: ctx[key]=val
    return ctx

def claims_for(source: str, claims_report: dict) -> list[dict]:
    return [c for c in claims_report.get('claims',[]) if c.get('source')==source]

def doc_context(root: Path, rel: str, claims_report: dict) -> dict:
    p=root/rel
    c=front_context(p)
    # Path-derived scope is used only when it is an explicit directory boundary,
    # never as proof of informational equivalence.
    parts=Path(rel).parts
    if len(parts)>=4 and parts[0]=='03_PEOPLES' and parts[1]=='CULTURES' and parts[2]=='HEARTH':
        c['scope']=c['scope'] or parts[3]
    c['claims']=claims_for(rel,claims_report)
    # Semantic claims currently require entity resolution, so do not promote
    # their sentence context into structured claim identity automatically.
    return c

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out
    discovery=load(out/'CORE_RELATIONSHIP_DISCOVERY.json',{'relationships':[]}); claims=load(out/'CORE_SEMANTIC_CLAIMS.json',{'claims':[]})
    rows=[]; eligible=0; rejected=0
    for r in discovery.get('relationships',[]):
        left=doc_context(root,r['left'],claims); right=doc_context(root,r['right'],claims)
        assessment=assess_variant(left,right)
        x=dict(r); x['variant_arbitration']=assessment.as_dict()
        x['variant_status']='ELIGIBLE' if assessment.eligible else 'REJECTED'
        if assessment.eligible: eligible+=1
        else: rejected+=1
        rows.append(x)
    result={'engine':'CORE VARIANT Gate','mode':'READ_ONLY','definition':'Same informational job, subject, scope, time, purpose, role, and substantially equivalent semantic claims; wording/presentation/modest detail may differ.','candidate_count':len(rows),'variant_candidates':eligible,'rejected_variant_candidates':rejected,'relationships':rows,'safety':{'automatic_variant_acceptance':False,'automatic_canon_change':False,'provenance_required':True}}
    (out/'CORE_VARIANT_GATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    md=['# CORE VARIANT Gate','','VARIANT means informational near-equivalence, not merely shared subject matter.','',f"Candidates assessed: **{len(rows)}**",f"Eligible VARIANT candidates: **{eligible}**",f"Rejected VARIANT candidates: **{rejected}**",'','## Required gates','- Same subject','- Same scope','- Same applicable time','- Same purpose','- Same document role','- At least 75% semantic-claim overlap','', 'A failed gate keeps the case out of VARIANT and records the reason for human/context arbitration.']
    (out/'CORE_VARIANT_GATE.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(f'CORE VARIANT gate: {len(rows)} assessed; {eligible} eligible; {rejected} rejected.')
if __name__=='__main__': main()
