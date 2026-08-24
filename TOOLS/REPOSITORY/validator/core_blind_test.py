#!/usr/bin/env python3
"""CORE A.C.E. blind generalization test with leakage-safe exemplar retrieval."""
from __future__ import annotations
import argparse,json,hashlib,sys
from pathlib import Path

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def role(path):
 p=path.upper()
 if 'ARCHIVE' in p:return 'HISTORICAL'
 if 'COMPARATIVE' in p:return 'COMPARATIVE'
 if 'TOOL' in p or '/TOOLS/' in p:return 'TOOL'
 if 'WORKING_CANON' in p:return 'WORKING_CANON'
 if 'WORKING' in p:return 'WORKING'
 return 'CANON'

def domain(path):
 p=path.upper()
 if 'ECOLOGY' in p:return 'ECOLOGY'
 if 'TOOLS' in p:return 'TOOLS'
 if 'PEOPLES' in p or 'CULTURES' in p or 'HEARTH' in p:return 'PEOPLES'
 return 'UNKNOWN'

def signal(left,right,strength):
 lr=left.rsplit('/',1)[-1].lower(); rr=right.rsplit('/',1)[-1].lower(); roles={role(left),role(right)}
 if 'HISTORICAL' in roles:return 'KEEP'
 if lr==rr:return 'DUPLICATE'
 return 'MERGE'

def pair_key(a,b):return tuple(sorted((a,b)))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out
 ace=load(out/'CORE_ACE_CALIBRATION_REPORT.json',{});disc=load(out/'CORE_RELATIONSHIP_DISCOVERY.json',{'relationships':[]});ledger=load(out/'CORE_DECISION_LEDGER.json',{'decisions':[]})
 known={d.get('relationship_id') for d in ledger.get('decisions',[])}
 fresh=[r for r in disc.get('relationships',[]) if r.get('relationship_id') not in known];fresh.sort(key=lambda r:hashlib.sha1(r.get('relationship_id','').encode()).hexdigest());holdout=fresh[:min(30,len(fresh))]
 holdout_ids={r.get('relationship_id') for r in holdout};holdout_pairs={pair_key(r.get('left',''),r.get('right','')) for r in holdout}
 sys.path.insert(0,str(Path(__file__).resolve().parent))
 try:
  from core_exemplar_pool import build as build_pool
  pool=build_pool(root,out,holdout_ids,holdout_pairs)
 except Exception as exc:
  pool={'examples':[],'example_count':0,'error':str(exc)}
 heur=ace.get('heuristic_candidates',[]);results=[]
 for r in holdout:
  left,right=r.get('left',''),r.get('right','');proposed=signal(left,right,r.get('match_strength',0));d=domain(left);roles={role(left),role(right)}
  if len(roles)==1:role_key=next(iter(roles))
  elif 'CANON' in roles:role_key='CANON'
  elif 'COMPARATIVE' in roles:role_key='COMPARATIVE'
  elif 'TOOL' in roles:role_key='TOOL'
  elif 'WORKING_CANON' in roles:role_key='WORKING_CANON'
  else:role_key='MIXED'
  domain_key=d if d==domain(right) else 'UNKNOWN';scores={};evidence={}
  for h in heur:
   hp=h.get('proposed');label=h.get('observed_label');support=float(h.get('support',0) or 0)
   if h.get('domain')!=domain_key or h.get('role')!=role_key:continue
   compatibility=1.0 if hp==proposed else 0.15;strength=float(r.get('match_strength',0) or 0);strength_fit=max(0.2,min(1.0,strength/5.0)) if hp=='DUPLICATE' else max(0.2,min(1.0,(6-strength)/5.0));score=(support**0.5)*compatibility*strength_fit;scores[label]=scores.get(label,0)+score;evidence.setdefault(label,[]).append({'kind':'HEURISTIC','support':support,'proposed':hp,'strength_fit':round(strength_fit,3)})
  exemplar_hits=[]
  for ex in pool.get('examples',[]):
   if ex.get('domain')!=domain_key or ex.get('role')!=role_key:continue
   label=ex.get('label');
   if label not in {'DUPLICATE','VARIANT','SUPPORTING','HISTORICAL','COINCIDENTAL','MISPLACED','CONFLICT','RELATED','REVIEW'}:continue
   text=(ex.get('reason','')+' '+ex.get('left','')+' '+ex.get('right','')).upper();target=(left+' '+right).upper();shared=sum(1 for token in ['FAMILY','BIRTH','CHILD','GOVERNANCE','AUTHORITY','SPECIALIST','LINEAGE','COMPARATIVE','AUDIT','DEMOGRAPHIC'] if token in text and token in target)
   if shared<1:continue
   sim=0.20+0.15*min(shared,4);scores[label]=scores.get(label,0)+sim;evidence.setdefault(label,[]).append({'kind':'EXEMPLAR','example_id':ex.get('example_id'),'similarity':round(sim,3),'source':ex.get('source')});exemplar_hits.append(ex.get('example_id'))
  if scores:
   ordered=sorted(scores.items(),key=lambda x:x[1],reverse=True);pred=ordered[0][0];top=ordered[0][1];second=ordered[1][1] if len(ordered)>1 else 0;conf=round(top/(top+second),3) if top+second else 0;status='EXEMPLAR_ASSISTED' if exemplar_hits else ('LEARNED_HEURISTIC' if conf>=0.60 else 'LOW_CONFIDENCE')
  else:pred='UNCLASSIFIED';conf=0;status='NO_LEARNED_EVIDENCE';ordered=[]
  results.append({'relationship_id':r.get('relationship_id'),'left':left,'right':right,'match_strength':r.get('match_strength'),'derived_domain':domain_key,'derived_role':role_key,'proposed_signal':proposed,'predicted_classification':pred,'confidence':conf,'evidence_scores':dict(ordered),'evidence_detail':evidence,'exemplar_hits':exemplar_hits,'prediction_status':status,'requires_human_validation':True})
 data={'engine':'CORE A.C.E. Blind Generalization Test','mode':'READ_ONLY','holdout_size':len(holdout),'exemplar_pool_size':pool.get('example_count',0),'predictions':results,'summary':{'predicted_with_evidence':sum(x['prediction_status'] in {'LEARNED_HEURISTIC','EXEMPLAR_ASSISTED'} for x in results),'exemplar_assisted':sum(x['prediction_status']=='EXEMPLAR_ASSISTED' for x in results),'low_confidence':sum(x['prediction_status']=='LOW_CONFIDENCE' for x in results),'unclassified':sum(x['prediction_status']=='NO_LEARNED_EVIDENCE' for x in results),'distinct_predictions':len(set(x['predicted_classification'] for x in results))},'safety':{'holdout_excluded_from_exemplars':True,'automatic_rule_promotion':False,'automatic_canon_change':False,'automatic_ledger_update':False,'human_validation_required':True}}
 (out/'CORE_BLIND_TEST.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 md=['# CORE A.C.E. Blind Generalization Test','','Fresh discoveries are held out. A.C.E. may retrieve leakage-safe human-verified exemplars, but holdout pairs are excluded from the exemplar pool.','',f"Holdout relationships: **{len(holdout)}**",f"Exemplar pool: **{pool.get('example_count',0)}**",f"Predicted with evidence: **{data['summary']['predicted_with_evidence']}**",f"Exemplar-assisted: **{data['summary']['exemplar_assisted']}**",f"Low confidence: **{data['summary']['low_confidence']}**",f"Unclassified: **{data['summary']['unclassified']}**",f"Distinct predicted classifications: **{data['summary']['distinct_predictions']}**",'']
 for r in results:md.append(f"- `{r['relationship_id']}` — {r['match_strength']}/5 — `{r['derived_domain']}/{r['derived_role']}` `{r['proposed_signal']}` → **{r['predicted_classification']}** ({r['prediction_status']}, confidence {r['confidence']}, exemplars {len(r['exemplar_hits'])})")
 (out/'CORE_BLIND_TEST.md').write_text('\n'.join(md)+'\n',encoding='utf-8');print(f"CORE blind test: {len(holdout)} fresh relationships; exemplar pool {pool.get('example_count',0)}; {data['summary']['exemplar_assisted']} exemplar-assisted predictions.")
if __name__=='__main__':main()
