#!/usr/bin/env python3
"""Cross-check Batman's repository investigation with Robin's independent semantic signals."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def cross_case(bat,rob):
 b={v['dimension']:v for v in bat.get('investigation_rounds_detail',[{}])[0].get('evidence_validity',[])}
 r=rob.get('robin_results',{});dims=sorted(set(b)|set(r));rows=[]
 for d in dims:
  bv=b.get(d,{});rv=r.get(d,{})
  ba=bool(bv.get('answers_question'));rs=bool(rv.get('supports_semantic_relation')); 
  if ba and rs:state='AGREE'
  elif ba and not rs:state='BATMAN_ONLY'
  elif not ba and rs:state='ROBIN_ONLY'
  elif d in b or d in r:state='NEITHER'
  else:state='NO_SIGNAL'
  rows.append({'dimension':d,'batman_answered':ba,'robin_semantic_support':rs,'state':state,'batman_answerability':bv.get('answerability',0),'robin_confidence':rv.get('confidence','none'),'ambiguity_signals':rv.get('ambiguity_signals',0)})
 agree=sum(x['state']=='AGREE' for x in rows);conflicts=sum(x['state'] in {'BATMAN_ONLY','ROBIN_ONLY'} for x in rows);return {'relationship_id':bat.get('relationship_id'),'documents':bat.get('documents',{}),'dimensions':rows,'agreement_count':agree,'disagreement_count':conflicts,'status':'AGREE' if agree and conflicts==0 else ('CONFLICT' if conflicts else 'INCONCLUSIVE')}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out;bd=load(out/'CORE_DETECTIVE_REPORT.json',{'cases':[]});rd=load(out/'CORE_ROBIN_REPORT.json',{'cases':[]});rmap={c.get('relationship_id'):c for c in rd.get('cases',[])};cases=[cross_case(c,rmap.get(c.get('relationship_id'),{})) for c in bd.get('cases',[])];summary={'cases':len(cases),'agree':sum(c['status']=='AGREE' for c in cases),'conflict':sum(c['status']=='CONFLICT' for c in cases),'inconclusive':sum(c['status']=='INCONCLUSIVE' for c in cases),'batman_only_dimensions':sum(x['state']=='BATMAN_ONLY' for c in cases for x in c['dimensions']),'robin_only_dimensions':sum(x['state']=='ROBIN_ONLY' for c in cases for x in c['dimensions'])};payload={'engine':'CORE A.C.E. Cross-Check','schema_version':'1.0','mode':'READ_ONLY','purpose':'cross-reference independent Detective and semantic-analysis perspectives','cases':cases,'summary':summary,'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}};(out/'CORE_CROSSCHECK_REPORT.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_CROSSCHECK_REPORT.md').write_text('# CORE Batman / Robin Cross-Check\n\n'+json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
