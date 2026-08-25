#!/usr/bin/env python3
"""CORE document triage: answer obvious cases cheaply after structural identity."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from core_document_identity import identify

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

def tokens(t): return {x for x in re.findall(r'[a-z][a-z0-9_]{3,}',t.lower()) if x not in STOP}
def similarity(a,b):
    aa,bb=tokens(a),tokens(b);return len(aa&bb)/max(1,len(aa|bb))

def role(p):
    u=p.upper()
    if any(x in u for x in HISTORICAL_MARKERS):return 'HISTORICAL'
    if any(x in u for x in SUPPORT_MARKERS):return 'SUPPORTING'
    return 'AUTHORITATIVE'

def triage(case,root):
    a,b=case.get('left',''),case.get('right','');ia,ib=identify(a),identify(b);aa,bb=text(root,a),text(root,b);sim=similarity(aa,bb)
    evidence={'identity':{'left':ia,'right':ib,'same_subject':ia['subject']==ib['subject'],'same_content_type':ia['content_type']==ib['content_type'],'same_scope':ia['scope']==ib['scope']},'content_similarity':round(sim,4)}
    decision='REVIEW';status='ESCALATE';reason=''
    if ia['role']=='HISTORICAL' or ib['role']=='HISTORICAL':
        decision='HISTORICAL';status='DIRECT';reason='historical/archive role is structurally explicit'
    elif ia['role']=='SUPPORTING' or ib['role']=='SUPPORTING':
        decision='SUPPORTING';status='DIRECT';reason='support/reference role is structurally explicit'
    elif ia['content_type']!=ib['content_type']:
        decision='RELATED';status='DIRECT';reason='different document types are related context, not variants'
    elif ia['subject'] and ib['subject'] and ia['subject']==ib['subject'] and ia['scope']['region'] and ib['scope']['region'] and ia['scope']['region']!=ib['scope']['region']:
        decision='RELATED';status='DIRECT';reason='same subject identity but different regional scope; not a variant'
    elif ia['subject']==ib['subject'] and ia['scope']==ib['scope']:
        if sim>=0.92: decision='DUPLICATE';status='DIRECT';reason='same subject, type, and scope with near-identical content'
        elif sim>=0.65: decision='VARIANT';status='DIRECT';reason='same subject, type, and scope with substantially overlapping but non-identical content'
        else: reason='same structural identity but substantive content differs; deep investigation required'
    elif ia['subject']!=ib['subject'] and sim<0.12:
        decision='COINCIDENTAL';status='DIRECT';reason='different subject identities with negligible content overlap'
    else: reason='structural identity/scope/function does not establish a safe direct classification'
    return {'relationship_id':case.get('relationship_id'),'documents':{'a':a,'b':b},'triage_status':status,'decision':decision,'reason':reason,'evidence':evidence,'deep_investigation_required':status!='DIRECT','safety':{'automatic_canon_change':False,'automatic_rule_promotion':False}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    queue=load(out/'CORE_ADJUDICATION_QUEUE.json',{'queue':[]});results=[triage(c,root) for c in queue.get('queue',[])]
    summary={'cases':len(results),'direct_triage':sum(x['triage_status']=='DIRECT' for x in results),'deep_investigation':sum(x['deep_investigation_required'] for x in results),'decisions':{}}
    for x in results:summary['decisions'][x['decision']]=summary['decisions'].get(x['decision'],0)+1
    payload={'engine':'CORE A.C.E. Document Triage','schema_version':'2.0','mode':'READ_ONLY','purpose':'identify document type, subject, scope, and role before relationship reasoning','cases':results,'summary':summary,'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
    (out/'CORE_DOCUMENT_TRIAGE.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_DOCUMENT_TRIAGE.md').write_text('# CORE Document Triage\n\n'+json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
