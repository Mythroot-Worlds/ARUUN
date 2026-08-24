#!/usr/bin/env python3
"""Apply evidence-gated VARIANT arbitration using semantic claims and information units."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from core_variant_arbitration import assess_variant

ARCHIVE_PARTS={'.git','.github','TOOLS','07_ARCHIVE','node_modules','__pycache__'}

def load(p, default):
    try: return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default
    except Exception: return default

def front_context(path: Path) -> dict:
    try: body=path.read_text(encoding='utf-8',errors='replace')[:30000]
    except Exception: return {}
    ctx={'subject':None,'scope':None,'time':None,'purpose':None,'role':None,'claims':[]}
    for line in body.splitlines()[:100]:
        m=re.match(r'^\s*[-#]*\s*(subject|scope|time|date|purpose|role|document\s*role|type)\s*[:=-]\s*(.+?)\s*$',line,re.I)
        if not m: continue
        key=re.sub(r'\s+','_',m.group(1).lower()); val=m.group(2).strip()
        if key=='date': key='time'
        if key in ('document_role','type'): key='role'
        if key in ctx and val: ctx[key]=val
    return ctx

def claims_for(source, report): return [c for c in report.get('claims',[]) if c.get('source')==source]
def units_for(source, report): return [u for u in report.get('units',[]) if u.get('source')==source]

def token_set(text): return {x for x in re.findall(r"[a-z0-9']+", text.lower()) if len(x)>2}
def unit_similarity(a,b):
    # Conservative lexical/section-aware signal; it is evidence for arbitration,
    # never sufficient by itself to establish VARIANT.
    if not a or not b: return 0.0
    scores=[]
    for x in a:
        xt=token_set(x.get('text','')); xs=(x.get('section') or '').lower()
        best=0.0
        for y in b:
            yt=token_set(y.get('text','')); ys=(y.get('section') or '').lower()
            if not xt or not yt: continue
            j=len(xt & yt)/len(xt | yt)
            if xs and ys and xs==ys: j=min(1.0,j+0.12)
            best=max(best,j)
        scores.append(best)
    reverse=[]
    for y in b:
        yt=token_set(y.get('text','')); ys=(y.get('section') or '').lower(); best=0.0
        for x in a:
            xt=token_set(x.get('text','')); xs=(x.get('section') or '').lower()
            if not xt or not yt: continue
            j=len(xt & yt)/len(xt | yt)
            if xs and ys and xs==ys: j=min(1.0,j+0.12)
            best=max(best,j)
        reverse.append(best)
    return round((sum(scores)/len(scores)+sum(reverse)/len(reverse))/2,4)

def doc_context(root, rel, claims_report, units_report):
    c=front_context(root/rel)
    parts=Path(rel).parts
    if len(parts)>=4 and parts[:3]==('03_PEOPLES','CULTURES','HEARTH'):
        c['scope']=c['scope'] or parts[3]
    c['claims']=claims_for(rel,claims_report)
    c['information_units']=units_for(rel,units_report)
    return c

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS'); a=ap.parse_args()
    root=Path(a.root).resolve(); out=root/a.out
    discovery=load(out/'CORE_RELATIONSHIP_DISCOVERY.json',{'relationships':[]})
    claims=load(out/'CORE_SEMANTIC_CLAIMS.json',{'claims':[]})
    units=load(out/'CORE_INFORMATION_UNITS.json',{'units':[]})
    rows=[]; eligible=0; rejected=0
    for r in discovery.get('relationships',[]):
        left=doc_context(root,r['left'],claims,units); right=doc_context(root,r['right'],claims,units)
        assessment=assess_variant(left,right)
        iu=unit_similarity(left['information_units'],right['information_units'])
        x=dict(r); x['variant_arbitration']=assessment.as_dict(); x['information_unit_similarity']=iu
        # Information-unit similarity can support equivalent-information cases,
        # but never overrides structural gates. If structural gates pass and
        # semantic claims are sparse, a strong bidirectional information signal
        # may satisfy the claims gate.
        if not assessment.eligible and iu >= 0.75 and all(assessment.gates[k] for k in ('subject','scope','time','purpose','role')):
            assessment.gates['claims']=True
            assessment.eligible=True
            assessment.descriptor='VARIANT'
            assessment.claim_overlap=max(assessment.claim_overlap,iu)
            assessment.informational_equivalence=iu
            assessment.reasons=['information_unit_equivalence >= 0.75; explicit relational claims were sparse']
            x['variant_arbitration']=assessment.as_dict()
        x['variant_status']='ELIGIBLE' if assessment.eligible else 'REJECTED'
        eligible += int(assessment.eligible); rejected += int(not assessment.eligible); rows.append(x)
    result={'engine':'CORE VARIANT Gate','mode':'READ_ONLY','definition':'Same informational job, subject, scope, time, purpose, role, and substantially equivalent information. Wording, presentation, formatting, or modest detail may differ.','candidate_count':len(rows),'variant_candidates':eligible,'rejected_variant_candidates':rejected,'relationships':rows,'safety':{'automatic_variant_acceptance':False,'automatic_canon_change':False,'provenance_required':True}}
    (out/'CORE_VARIANT_GATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    md=['# CORE VARIANT Gate','','VARIANT means informational near-equivalence, not merely shared subject matter.','',f"Candidates assessed: **{len(rows)}**",f"Eligible VARIANT candidates: **{eligible}**",f"Rejected VARIANT candidates: **{rejected}**",'','## Required gates','- Same subject','- Same scope','- Same applicable time','- Same purpose','- Same document role','- Substantially equivalent semantic claims **or** strong bidirectional information-unit equivalence when explicit relational claims are sparse.','','Information-unit similarity is evidence only; it cannot override subject, scope, time, purpose, or role gates.']
    (out/'CORE_VARIANT_GATE.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(f'CORE VARIANT gate: {len(rows)} assessed; {eligible} eligible; {rejected} rejected.')
if __name__=='__main__': main()
