#!/usr/bin/env python3
"""CORE document triage: canonical-grounded layered classification before deep investigation."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from core_layered_relationship import compare, CALIBRATION_CASES
from core_canonical_context import build_for_pair, build_context

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def text(root,p):
    try:return (root/p).read_text(encoding='utf-8',errors='replace')
    except:return ''

def canonical_result(case,root):
    return build_for_pair(case,root)['canonical_context']

def triage(case,root):
    a,b=case.get('left',''),case.get('right','')
    result=compare(a,text(root,a),b,text(root,b)); canon=canonical_result(case,root)
    # Canonical context is evidence, not a filename shortcut. It can veto a
    # relationship only when it supplies a structural fact (scope, role,
    # conflict, or temporal relationship) that the layered comparison records.
    result['canonical_context']=canon
    status='DIRECT' if result['decision'] in {'DUPLICATE','VARIANT','RELATED','SUPPORTING','HISTORICAL','COINCIDENTAL'} else 'ESCALATE'
    reason='layered relationship resolved directly against canonical repository context' if status=='DIRECT' else 'one or more relationship layers remain ambiguous; canonical knowns supplied to deep investigation'
    return {'relationship_id':case.get('relationship_id'),'documents':{'a':a,'b':b},'triage_status':status,'decision':result['decision'],'reason':reason,'layered_comparison':result,'canonical_context':canon,'deep_investigation_required':status!='DIRECT','safety':{'automatic_canon_change':False,'automatic_rule_promotion':False}}

def run_calibration(root):
    out=[]
    for a,b,expected in CALIBRATION_CASES:
        r=compare(a,text(root,a),b,text(root,b));out.append({'left':a,'right':b,'expected':expected,'actual':r['decision'],'pass':r['decision']==expected,'comparison':r,'canonical_context':build_for_pair({'left':a,'right':b},root)['canonical_context']})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    queue=load(out/'CORE_ADJUDICATION_QUEUE.json',{'queue':[]});results=[triage(c,root) for c in queue.get('queue',[])];cal=run_calibration(root)
    summary={'cases':len(results),'direct_triage':sum(x['triage_status']=='DIRECT' for x in results),'deep_investigation':sum(x['deep_investigation_required'] for x in results),'canonical_grounded_cases':sum(bool(x.get('canonical_context')) for x in results),'decisions':{},'calibration_cases':len(cal),'calibration_passed':sum(x['pass'] for x in cal),'calibration_failed':sum(not x['pass'] for x in cal)}
    for x in results:summary['decisions'][x['decision']]=summary['decisions'].get(x['decision'],0)+1
    payload={'engine':'CORE A.C.E. Document Triage','schema_version':'3.1','mode':'READ_ONLY','purpose':'identify canonical knowns first, then classify category, subject, context, content, purpose, and information overlap','cases':results,'calibration':cal,'summary':summary,'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
    (out/'CORE_DOCUMENT_TRIAGE.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_DOCUMENT_TRIAGE.md').write_text('# CORE Document Triage\n\n'+json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
    if any(not x['pass'] for x in cal): raise SystemExit('Layered relationship calibration failed')
if __name__=='__main__':main()
