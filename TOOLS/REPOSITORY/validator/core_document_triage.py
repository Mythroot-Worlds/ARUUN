#!/usr/bin/env python3
"""CORE document triage: answer obvious document-placement/relationship cases cheaply.

This is intentionally conservative. It identifies the document subject/scope and
handles only relationships that are structurally obvious. Ambiguous cases are
marked for the existing Batman/Robin investigation subsystem.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

STOP=set('the and for with from that this document regional family final draft version comparative variant duplicate supporting historical canonical canon hearth region regions'.split())
REGIONS={'PLAINS','MOUNTAINS','RIVER','WETLANDS','DESERT','COAST'}
SUPPORT_MARKERS=('CHECKLIST','AUDIT','FRAMEWORK','GUIDE','REFERENCE','OPERATING_RULES')
HISTORICAL_MARKERS=('HISTORICAL','ARCHIVE','LEGACY','SUPERSEDED','PREVIOUS')

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def text(root,p):
    try:return (root/p).read_text(encoding='utf-8',errors='replace')
    except:return ''

def subject(p):
    toks=[x for x in re.split(r'[^a-z0-9]+',Path(p).stem.lower()) if len(x)>=3 and x not in STOP and x.upper() not in {r.lower() for r in REGIONS}]
    return '_'.join(toks)

def region(p):
    for part in reversed(Path(p).parts):
        u=part.upper().replace('-','_')
        if u in REGIONS:return u
    return None

def tokens(t):
    return {x for x in re.findall(r'[a-z][a-z0-9_]{3,}',t.lower()) if x not in STOP}

def similarity(a,b):
    aa,bb=tokens(a),tokens(b)
    return len(aa&bb)/max(1,len(aa|bb))

def role(p):
    u=p.upper()
    if any(x in u for x in HISTORICAL_MARKERS):return 'HISTORICAL'
    if any(x in u for x in SUPPORT_MARKERS):return 'SUPPORTING'
    return 'AUTHORITATIVE'

def triage(case,root):
    a,b=case.get('left',''),case.get('right','');ta,tb=subject(a),subject(b);ra,rb=region(a),region(b);aa,bb=text(root,a),text(root,b);sim=similarity(aa,bb);roles=(role(a),role(b))
    evidence={'subject':{'left':ta,'right':tb,'same':ta==tb},'scope':{'left':ra,'right':rb,'same':ra==rb and ra is not None},'role':{'left':roles[0],'right':roles[1],'same':roles[0]==roles[1]},'content_similarity':round(sim,4)}
    decision='REVIEW';status='ESCALATE';reason=''
    if roles[0]=='HISTORICAL' or roles[1]=='HISTORICAL':
        decision='HISTORICAL';status='DIRECT';reason='historical/archive role is structurally explicit'
    elif roles[0]=='SUPPORTING' or roles[1]=='SUPPORTING':
        decision='SUPPORTING';status='DIRECT';reason='support/reference role is structurally explicit'
    elif ta and tb and ta==tb and ra is not None and rb is not None and ra!=rb:
        decision='RELATED';status='DIRECT';reason='same subject identity but different regional scope; not a variant'
    elif ta and tb and ta==tb and ra is not None and rb is not None and ra==rb:
        if sim>=0.92:
            decision='DUPLICATE';status='DIRECT';reason='same subject and scope with near-identical content'
        elif sim>=0.65:
            decision='VARIANT';status='DIRECT';reason='same subject and scope with substantially overlapping but non-identical content'
        else:
            reason='same structural identity but substantive content differs; deep investigation required'
    elif ta and tb and ta!=tb and sim<0.12:
        decision='COINCIDENTAL';status='DIRECT';reason='different subject identities with negligible content overlap'
    else:
        reason='structural identity/scope/function does not establish a safe direct classification'
    return {'relationship_id':case.get('relationship_id'),'documents':{'a':a,'b':b},'triage_status':status,'decision':decision,'reason':reason,'evidence':evidence,'deep_investigation_required':status!='DIRECT','safety':{'automatic_canon_change':False,'automatic_rule_promotion':False}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    queue=load(out/'CORE_ADJUDICATION_QUEUE.json',{'queue':[]});results=[triage(c,root) for c in queue.get('queue',[])]
    summary={'cases':len(results),'direct_triage':sum(x['triage_status']=='DIRECT' for x in results),'deep_investigation':sum(x['deep_investigation_required'] for x in results),'decisions':{}}
    for x in results:summary['decisions'][x['decision']]=summary['decisions'].get(x['decision'],0)+1
    payload={'engine':'CORE A.C.E. Document Triage','schema_version':'1.0','mode':'READ_ONLY','purpose':'identify what a document is, where it belongs, and whether an obvious existing relationship can be classified before deep investigation','cases':results,'summary':summary,'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
    (out/'CORE_DOCUMENT_TRIAGE.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    (out/'CORE_DOCUMENT_TRIAGE.md').write_text('# CORE Document Triage\n\n'+json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
