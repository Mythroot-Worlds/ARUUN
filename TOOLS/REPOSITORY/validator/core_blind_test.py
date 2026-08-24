#!/usr/bin/env python3
"""CORE A.C.E. blind generalization test.

Applies learned heuristics as competing evidence rather than a single rule.
Read-only: never writes labels to the ledger or changes canon.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out
 ace=load(out/'CORE_ACE_CALIBRATION_REPORT.json',{}); disc=load(out/'CORE_RELATIONSHIP_DISCOVERY.json',{'relationships':[]})
 heur=[h for h in ace.get('heuristic_candidates',[]) if h.get('status')=='ELIGIBLE_FOR_HUMAN_REVIEW']
 ledger=load(out/'CORE_DECISION_LEDGER.json',{'decisions':[]});known={d.get('relationship_id') for d in ledger.get('decisions',[])}
 fresh=[r for r in disc.get('relationships',[]) if r.get('relationship_id') not in known];fresh.sort(key=lambda r:hashlib.sha1(r.get('relationship_id','').encode()).hexdigest());holdout=fresh[:min(30,len(fresh))]
 results=[]
 for r in holdout:
  proposed='DUPLICATE' if r.get('match_strength',0)>=4 else 'MERGE'
  domain='PEOPLES';role='CANON';scores={}
  for h in heur:
   if h.get('domain')!=domain or h.get('role')!=role: continue
   hp=h.get('proposed'); label=h.get('observed_label'); support=float(h.get('support',0) or 0)
   compatibility=1.0 if hp==proposed else 0.35
   strength=float(r.get('match_strength',0) or 0); strength_fit=1.0
   if hp=='DUPLICATE': strength_fit=max(0.2,min(1.0,strength/5.0))
   elif hp=='MERGE': strength_fit=max(0.2,min(1.0,(6-strength)/5.0))
   score=support*compatibility*strength_fit
   scores[label]=scores.get(label,0)+score
  if scores:
   ordered=sorted(scores.items(),key=lambda x:x[1],reverse=True);pred=ordered[0][0];top=ordered[0][1];second=ordered[1][1] if len(ordered)>1 else 0;conf=round(top/(top+second),3) if top+second else 0
   status='LEARNED_HEURISTIC' if conf>=0.60 else 'LOW_CONFIDENCE'
  else: pred='UNCLASSIFIED';conf=0;status='NO_LEARNED_HEURISTIC';ordered=[]
  results.append({'relationship_id':r.get('relationship_id'),'match_strength':r.get('match_strength'),'proposed_signal':proposed,'predicted_classification':pred,'confidence':conf,'evidence_scores':dict(ordered),'prediction_status':status,'requires_human_validation':True})
 data={'engine':'CORE A.C.E. Blind Generalization Test','mode':'READ_ONLY','holdout_size':len(holdout),'eligible_learned_heuristics':len(heur),'predictions':results,'summary':{'predicted_with_learned_heuristic':sum(x['prediction_status']=='LEARNED_HEURISTIC' for x in results),'low_confidence':sum(x['prediction_status']=='LOW_CONFIDENCE' for x in results),'unclassified':sum(x['prediction_status']=='NO_LEARNED_HEURISTIC' for x in results)},'safety':{'holdout_excluded_from_training':True,'automatic_canon_change':False,'automatic_ledger_update':False,'human_validation_required':True}}
 (out/'CORE_BLIND_TEST.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 md=['# CORE A.C.E. Blind Generalization Test','','Fresh discoveries are held out from the human decision ledger. Learned heuristics compete as weighted evidence; predictions remain provisional.','',f"Holdout relationships: **{len(holdout)}**",f"Eligible learned heuristics: **{len(heur)}**",f"Predicted with learned heuristic: **{data['summary']['predicted_with_learned_heuristic']}**",f"Low confidence: **{data['summary']['low_confidence']}**",f"Unclassified: **{data['summary']['unclassified']}**",'']
 for r in results: md.append(f"- `{r['relationship_id']}` — {r['match_strength']}/5 — `{r['proposed_signal']}` → **{r['predicted_classification']}** ({r['prediction_status']}, confidence {r['confidence']})")
 (out/'CORE_BLIND_TEST.md').write_text('\n'.join(md)+'\n',encoding='utf-8');print(f"CORE blind test: {len(holdout)} fresh relationships; {data['summary']['predicted_with_learned_heuristic']} confident, {data['summary']['low_confidence']} low-confidence, {data['summary']['unclassified']} unclassified.")
if __name__=='__main__':main()
