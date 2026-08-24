#!/usr/bin/env python3
"""Apply evidence-gated VARIANT arbitration using claims and information units."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from core_variant_arbitration import assess_variant
from core_semantic_comparator import compare_units

SKIP={'.git','.github','TOOLS','07_ARCHIVE','node_modules','__pycache__'}

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def front_context(path):
    try: body=path.read_text(encoding='utf-8',errors='replace')[:30000]
    except:return {}
    ctx={'subject':None,'scope':None,'time':None,'purpose':None,'role':None,'claims':[]}
    for line in body.splitlines()[:100]:
        m=re.match(r'^\s*[-#]*\s*(subject|scope|time|date|purpose|role|document\s*role|type)\s*[:=-]\s*(.+?)\s*$',line,re.I)
        if not m:continue
        key=re.sub(r'\s+','_',m.group(1).lower());val=m.group(2).strip()
        if key=='date':key='time'
        if key in ('document_role','type'):key='role'
        if key in ctx and val:ctx[key]=val
    return ctx

def for_source(source,report,key):return [x for x in report.get(key,[]) if x.get('source')==source]

def doc_context(root,rel,claims,units):
    c=front_context(root/rel);parts=Path(rel).parts
    if len(parts)>=4 and parts[:3]==('03_PEOPLES','CULTURES','HEARTH'):c['scope']=c['scope'] or parts[3]
    c['claims']=for_source(rel,claims,'claims');c['information_units']=for_source(rel,units,'units');return c

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    discovery=load(out/'CORE_RELATIONSHIP_DISCOVERY.json',{'relationships':[]});claims=load(out/'CORE_SEMANTIC_CLAIMS.json',{'claims':[]});units=load(out/'CORE_INFORMATION_UNITS.json',{'units':[]})
    rows=[];eligible=rejected=0
    for r in discovery.get('relationships',[]):
        left=doc_context(root,r['left'],claims,units);right=doc_context(root,r['right'],claims,units);assessment=assess_variant(left,right);comparison=compare_units(left['information_units'],right['information_units'])
        x=dict(r);x['pairwise_semantic_comparison']=comparison.as_dict();x['variant_arbitration']=assessment.as_dict()
        structural=all(assessment.gates[k] for k in ('subject','scope','time','purpose','role'))
        if not assessment.eligible and structural and comparison.same_information:
            assessment.gates['claims']=True;assessment.eligible=True;assessment.descriptor='VARIANT';assessment.claim_overlap=max(assessment.claim_overlap,comparison.score);assessment.informational_equivalence=comparison.score;assessment.comparison_basis='pairwise_information_units';assessment.reasons=['bidirectional semantic information equivalence passed; explicit claims were sparse or differently worded'];x['variant_arbitration']=assessment.as_dict()
        x['variant_status']='ELIGIBLE' if assessment.eligible else 'REJECTED';eligible+=int(assessment.eligible);rejected+=int(not assessment.eligible);rows.append(x)
    result={'engine':'CORE VARIANT Gate','schema_version':'2.0','mode':'READ_ONLY','definition':'VARIANT means near-equivalent informational content: same subject, scope, time, purpose, role, and substantially equivalent underlying information. Wording, presentation, formatting, and modest detail may differ.','candidate_count':len(rows),'variant_candidates':eligible,'rejected_variant_candidates':rejected,'relationships':rows,'safety':{'automatic_variant_acceptance':False,'automatic_canon_change':False,'provenance_required':True}}
    (out/'CORE_VARIANT_GATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    md=['# CORE VARIANT Gate','','VARIANT is informational near-equivalence, not shared subject matter.','',f"Candidates assessed: **{len(rows)}**",f"Eligible VARIANT candidates: **{eligible}**",f"Rejected VARIANT candidates: **{rejected}**",'','## Gates','- Same subject','- Same scope','- Same applicable time','- Same purpose','- Same document role','- Bidirectional information equivalence, using pairwise semantic comparison when explicit claims are sparse.','','The comparator is evidence, not autonomous canon authority.']
    (out/'CORE_VARIANT_GATE.md').write_text('\n'.join(md)+'\n',encoding='utf-8');print(f'CORE VARIANT gate: {len(rows)} assessed; {eligible} eligible; {rejected} rejected.')
if __name__=='__main__':main()
