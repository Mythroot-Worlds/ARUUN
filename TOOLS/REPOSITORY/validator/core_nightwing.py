#!/usr/bin/env python3
"""CORE Nightwing: independent synthesis of factor coverage and case evidence."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def synth(case,oracle):
 out=[]
 oracle_has_context=bool(oracle.get('oracle',{}).get('association_candidates'))
 for d in case.get('dimensions',[]):
  state=d.get('state')
  if state=='CORROBORATED': verdict='CONVERGENT'
  elif state=='CONTRADICTED': verdict='CONTRADICTORY'
  elif state in {'BATMAN_UNCORROBORATED','ROBIN_SUPPORT_ONLY','MIXED_COVERAGE'}: verdict='PARTIAL'
  else: verdict='UNRESOLVED'
  out.append({'dimension':d.get('dimension'),'verdict':verdict,'basis':{'batman_answered':d.get('batman_answered',False),'robin_factor_support':d.get('robin_factor_support',False),'oracle_context':oracle_has_context}})
 return {'relationship_id':case.get('relationship_id'),'dimensions':out,'oracle_context_attached':oracle_has_context,'independent_synthesis':'Nightwing evaluates convergence, partial coverage, contradiction, and unresolved factors without overwriting Batman or Robin'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();out=Path(x.root).resolve()/x.out;cross=load(out/'CORE_CROSSCHECK_REPORT.json',{'cases':[]});oracle=load(out/'CORE_ORACLE_REPORT.json',{'cases':[]});omap={c.get('relationship_id'):c for c in oracle.get('cases',[]) if c.get('relationship_id')};cases=[synth(c,omap.get(c.get('relationship_id'),{})) for c in cross['cases']];summary={'cases':len(cases),'convergent_dimensions':sum(sum(x['verdict']=='CONVERGENT' for x in c['dimensions']) for c in cases),'partial_dimensions':sum(sum(x['verdict']=='PARTIAL' for x in c['dimensions']) for c in cases),'contradictory_dimensions':sum(sum(x['verdict']=='CONTRADICTORY' for x in c['dimensions']) for c in cases),'unresolved_dimensions':sum(sum(x['verdict']=='UNRESOLVED' for x in c['dimensions']) for c in cases),'cases_with_oracle_context':sum(c['oracle_context_attached'] for c in cases)};payload={'engine':'CORE A.C.E. Nightwing','schema_version':'2.1','mode':'READ_ONLY','purpose':'independent synthesis of investigator roles, complete evidence coverage, and Oracle context','cases':cases,'summary':summary};(out/'CORE_NIGHTWING_REPORT.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_NIGHTWING_REPORT.md').write_text('# CORE Nightwing Report\n\n'+json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
