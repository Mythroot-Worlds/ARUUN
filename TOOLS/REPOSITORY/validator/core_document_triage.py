#!/usr/bin/env python3
"""CORE document triage: layered classification before deep investigation."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from core_layered_relationship import compare, CALIBRATION_CASES

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def text(root,p):
    try:return (root/p).read_text(encoding='utf-8',errors='replace')
    except:return ''

def triage(case,root):
    a,b=case.get('left',''),case.get('right','')
    result=compare(a,text(root,a),b,text(root,b))
    status='DIRECT' if result['decision'] in {'DUPLICATE','VARIANT','RELATED','SUPPORTING','HISTORICAL','COINCIDENTAL'} else 'ESCALATE'
    reason='layered relationship resolved directly' if status=='DIRECT' else 'one or more relationship layers remain ambiguous'
    return {'relationship_id':case.get('relationship_id'),'documents':{'a':a,'b':b},'triage_status':status,
            'decision':result['decision'],'reason':reason,'layered_comparison':result,
            'deep_investigation_required':status!='DIRECT',
            'safety':{'automatic_canon_change':False,'automatic_rule_promotion':False}}

def run_calibration(root):
    out=[]
    for a,b,expected in CALIBRATION_CASES:
        r=compare(a,text(root,a),b,text(root,b));out.append({'left':a,'right':b,'expected':expected,'actual':r['decision'],'pass':r['decision']==expected,'comparison':r})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    queue=load(out/'CORE_ADJUDICATION_QUEUE.json',{'queue':[]});results=[triage(c,root) for c in queue.get('queue',[])];cal=run_calibration(root)
    summary={'cases':len(results),'direct_triage':sum(x['triage_status']=='DIRECT' for x in results),'deep_investigation':sum(x['deep_investigation_required'] for x in results),'decisions':{},'calibration_cases':len(cal),'calibration_passed':sum(x['pass'] for x in cal),'calibration_failed':sum(not x['pass'] for x in cal)}
    for x in results:summary['decisions'][x['decision']]=summary['decisions'].get(x['decision'],0)+1
    payload={'engine':'CORE A.C.E. Document Triage','schema_version':'3.0','mode':'READ_ONLY','purpose':'classify category, subject, context, content, purpose, and information overlap before deep investigation','cases':results,'calibration':cal,'summary':summary,'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
    (out/'CORE_DOCUMENT_TRIAGE.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_DOCUMENT_TRIAGE.md').write_text('# CORE Document Triage\n\n'+json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
    if any(not x['pass'] for x in cal): raise SystemExit('Layered relationship calibration failed')
if __name__=='__main__':main()
