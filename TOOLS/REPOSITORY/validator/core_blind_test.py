#!/usr/bin/env python3
"""CORE A.C.E. blind test with leakage-safe exemplars and contextual skimming."""
from __future__ import annotations
import argparse,json,hashlib,sys
from pathlib import Path

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def role(path):
 p=(path or '').upper()
 if 'ARCHIVE' in p:return 'HISTORICAL'
 if 'COMPARATIVE' in p:return 'COMPARATIVE'
 if 'CHECKLIST' in p or 'AUDIT' in p or 'TOOL' in p or '/TOOLS/' in p:return 'TOOL'
 if 'WORKING_CANON' in p:return 'WORKING_CANON'
 if 'WORKING' in p or 'REVISION' in p or 'DEMOGRAPHIC' in p:return 'WORKING'
 return 'CANON'

def domain(path):
 p=(path or '').upper()
 if 'ECOLOGY' in p:return 'ECOLOGY'
 if 'TOOLS' in p:return 'TOOLS'
 if 'PEOPLES' in p or 'CULTURES' in p or 'HEARTH' in p:return 'PEOPLES'
 return 'UNKNOWN'

def signal(left,right,strength):
 lr=(left or '').rsplit('/',1)[-1].lower();rr=(right or '').rsplit('/',1)[-1].lower();roles={role(left),role(right)}
 if 'HISTORICAL' in roles:return 'KEEP'
 if lr==rr:return 'DUPLICATE'
 return 'MERGE'

def pair_key(a,b):return tuple(sorted((a or '',b or '')))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out
 ace=load(out/'CORE_ACE_CALIBRATION_REPORT.json',{});disc=load(out/'CORE_RELATIONSHIP_DISCOVERY.json',{'relationships':[]});ledger=load(out/'CORE_DECISION_LEDGER.json',{'decisions':[]})
 known={d.get('relationship_id') for d in ledger.get('decisions',[])};fresh=[r for r in disc.get('relationships',[]) if r.get('relationship_id') not in known];fresh.sort(key=lambda r:hashlib.sha1(r.get('relationship_id','').encode()).hexdigest());holdout=fresh[:min(30,len(fresh))]
 holdout_ids={r.get('relationship_id') for r in holdout if r.get('relationship_id')};holdout_pairs={pair_key(r.get('left'),r.get('right')) for r in holdout if r.get('left') and r.get('right')}
 sys.path.insert(0,str(Path(__file__).resolve().parent))
 from core_context import context
 from core_exemplar_pool import build as build_pool
 pool=build_pool(root,out,holdout_ids,holdout_pairs);heur=ace.get('heuristic_candidates',[]);results=[]
 for r in holdout:
  left,right=r.get('left',''),r.get('right','');ca=context(left,root);cb=context(right,root);proposed=signal(left,right,r.get('match_strength',0));d=domain(left);roles={role(left),role(right)}
  if len(roles)==1:role_key=next(iter(roles))
  elif 'CANON' in roles:role_key='CANON'
  elif 'COMPARATIVE' in roles:role_key='COMPARATIVE'
  elif 'TOOL' in roles:role_key='TOOL'
  elif 'WORKING' in roles:role_key='WORKING'
  else:role_key='MIXED'
  domain_key=d if d==domain(right) else 'UNKNOWN';scores={};evidence={}
  for h in heur:
   if h.get('domain')!=domain_key or h.get('role')!=role_key:continue
   hp=h.get('proposed');label=h.get('observed_label');support=float(h.get('support',0) or 0);compatibility=1.0 if hp==proposed else 0.15;strength=float(r.get('match_strength',0) or 0);fit=max(0.2,min(1.0,strength/5.0)) if hp=='DUPLICATE' else max(0.2,min(1.0,(6-strength)/5.0));score=(support**0.5)*compatibility*fit;scores[label]=scores.get(label,0)+score;evidence.setdefault(label,[]).append({'kind':'HEURISTIC','support':support,'proposed':hp,'strength_fit':round(fit,3)})
  target=(left+' '+right+' '+' '.join(sum(ca['indicators'].values(),[]))+' '+' '.join(sum(cb['indicators'].values(),[]))).upper();exemplar_hits=[]
  for ex in pool.get('examples',[]):
   if ex.get('domain')!=domain_key or ex.get('role')!=role_key:continue
   label=ex.get('label')
   if label not in {'DUPLICATE','VARIANT','SUPPORTING','HISTORICAL','COINCIDENTAL','MISPLACED','CONFLICT','RELATED','REVIEW'}:continue
   ef=ex.get('features',{});shared=0
   for dim in ('scope','function','authority','population'):
    shared+=len(set(ef.get(dim,[])) & set(ca.get('scope_signals',[])+cb.get('scope_signals',[]) if dim=='scope' else ca.get('indicators',{}).get(dim,[])+cb.get('indicators',{}).get(dim,[])))
   text=(ex.get('reason','')+' '+(ex.get('left') or '')+' '+(ex.get('right') or '')).upper();shared+=sum(1 for token in ['FAMILY','BIRTH','CHILD','GOVERNANCE','AUTHORITY','SPECIALIST','LINEAGE','COMPARATIVE','AUDIT','DEMOGRAPHIC'] if token in text and token in target)
   if shared<1:continue
   sim=min(0.85,0.18+0.10*shared);scores[label]=scores.get(label,0)+sim;evidence.setdefault(label,[]).append({'kind':'EXEMPLAR','example_id':ex.get('example_id'),'similarity':round(sim,3),'source':ex.get('source')});exemplar_hits.append(ex.get('example_id'))
  if scores:
   ordered=sorted(scores.items(),key=lambda x:x[1],reverse=True);pred=ordered[0][0];top=ordered[0][1];second=ordered[1][1] if len(ordered)>1 else 0;conf=round(top/(top+second),3) if top+second else 0;status='EXEMPLAR_ASSISTED' if exemplar_hits else ('LEARNED_HEURISTIC' if conf>=0.60 else 'LOW_CONFIDENCE')
  else:pred='UNCLASSIFIED';conf=0;status='NO_LEARNED_EVIDENCE';ordered=[]
  results.append({'relationship_id':r.get('relationship_id'),'left':left,'right':right,'match_strength':r.get('match_strength'),'context_a':ca,'context_b':cb,'derived_domain':domain_key,'derived_role':role_key,'proposed_signal':proposed,'predicted_classification':pred,'confidence':conf,'evidence_scores':dict(ordered),'evidence_detail':evidence,'exemplar_hits':sorted(set(exemplar_hits)),'prediction_status':status,'requires_human_validation':True})
 data={'engine':'CORE A.C.E. Blind Generalization Test','mode':'READ_ONLY','contextual_skimming':True,'holdout_size':len(holdout),'exemplar_pool_size':pool.get('example_count',0),'predictions':results,'summary':{'predicted_with_evidence':sum(x['prediction_status'] in {'LEARNED_HEURISTIC','EXEMPLAR_ASSISTED'} for x in results),'exemplar_assisted':sum(x['prediction_status']=='EXEMPLAR_ASSISTED' for x in results),'low_confidence':sum(x['prediction_status']=='LOW_CONFIDENCE' for x in results),'unclassified':sum(x['prediction_status']=='NO_LEARNED_EVIDENCE' for x in results),'distinct_predictions':len(set(x['predicted_classification'] for x in results))},'safety':{'holdout_excluded_from_exemplars':True,'automatic_rule_promotion':False,'automatic_canon_change':False,'automatic_ledger_update':False,'human_validation_required':True}}
 (out/'CORE_BLIND_TEST.json').write_text(json.dumps(data,indent=2),encoding='utf-8');print(f"CORE blind test: {len(holdout)} fresh relationships; contextual skimming enabled; exemplar pool {pool.get('example_count',0)}; {data['summary']['exemplar_assisted']} exemplar-assisted predictions.")
if __name__=='__main__':main()
