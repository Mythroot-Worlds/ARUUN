#!/usr/bin/env python3
"""CORE Alfred: calm mediator, contradiction handler, and stop gate."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def mediate(cross,night):
 decisions=[]
 for d in cross.get('dimensions',[]):
  state=d.get('state');n=next((x for x in night.get('dimensions',[]) if x.get('dimension')==d.get('dimension')),None)
  if state=='CORROBORATED': decision='CONVERGED'
  elif state=='CONTRADICTED': decision='REQUIRES_HUMAN_REVIEW'
  elif state in {'BATMAN_UNCORROBORATED','ROBIN_SUPPORT_ONLY','MIXED_COVERAGE'}: decision='REQUIRES_CONTEXT'
  else: decision='UNRESOLVED'
  decisions.append({'dimension':d.get('dimension'),'cross_state':state,'nightwing_verdict':n.get('verdict') if n else 'UNKNOWN','alfred_decision':decision,'reason':'Batman and Robin provide compatible evidence' if decision=='CONVERGED' else ('explicit contradiction requires human review' if decision=='REQUIRES_HUMAN_REVIEW' else 'coverage or evidence remains incomplete')})
 status='RESOLVED' if decisions and all(x['alfred_decision']=='CONVERGED' for x in decisions) else ('ESCALATE' if any(x['alfred_decision'] in {'REQUIRES_HUMAN_REVIEW','REQUIRES_CONTEXT'} for x in decisions) else 'UNRESOLVED')
 return {'relationship_id':cross.get('relationship_id'),'decisions':decisions,'status':status,'human_review_required':status!='RESOLVED','stop_rule':'stop only when required dimensions converge without unresolved contradiction or evidence gap'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();out=Path(x.root).resolve()/x.out;cross=load(out/'CORE_CROSSCHECK_REPORT.json',{'cases':[]});night=load(out/'CORE_NIGHTWING_REPORT.json',{'cases':[]});nmap={c.get('relationship_id'):c for c in night.get('cases',[])};cases=[mediate(c,nmap.get(c.get('relationship_id'),{})) for c in cross['cases']];summary={'cases':len(cases),'resolved':sum(c['status']=='RESOLVED' for c in cases),'escalate':sum(c['status']=='ESCALATE' for c in cases),'unresolved':sum(c['status']=='UNRESOLVED' for c in cases)};payload={'engine':'CORE A.C.E. Alfred','schema_version':'2.0','mode':'READ_ONLY','purpose':'mediate factor coverage, escalate true contradictions, and stop only on sufficient convergence','cases':cases,'summary':summary,'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}};(out/'CORE_ALFRED_REPORT.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_ALFRED_REPORT.md').write_text('# CORE Alfred Mediation Report\n\n'+json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
