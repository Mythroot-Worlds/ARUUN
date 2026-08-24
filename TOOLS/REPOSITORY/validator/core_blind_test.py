#!/usr/bin/env python3
"""CORE A.C.E. blind generalization test.

Uses all observed human-calibration outcomes as competing evidence. Eligible
patterns carry their support; sub-threshold contrastive examples remain visible
so the system can learn when NOT to choose the dominant outcome.
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
 ace=load(out/'CORE_ACE_CALIBRATION_REPORT.json',{});disc=load(out/'CORE_RELATIONSHIP_DISCOVERY.json',{'relationships':[]});heur=ace.get('heuristic_candidates',[])
 ledger=load(out/'CORE_DECISION_LEDGER.json',{'decisions':[]});known={d.get('relationship_id') for d in ledger.get('decisions',[])}
 fresh=[r for r in disc.get('relationships',[]) if r.get('relationship_id') not in known];fresh.sort(key=lambda r:hashlib.sha1(r.get('relationship_id','').encode()).hexdigest());holdout=fresh[:min(30,len(fresh))]
 results=[]
 for r in holdout:
  proposed='DUPLICATE' if r.get('match_strength',0)>=4 else 'MERGE';domain='PEOPLES';role='CANON';scores={};evidence={}
  for h in heur:
   if h.get('domain')!=domain or h.get('role')!=role: continue
   hp=h.get('proposed');label=h.get('observed_label');support=float(h.get('support',0) or 0)
   compatibility=1.0 if hp==proposed else 0.15
   strength=float(r.get('match_strength',0) or 0)
   strength_fit=max(0.2,min(1.0,strength/5.0)) if hp=='DUPLICATE' else max(0.2,min(1.0,(6-strength)/5.0))
   score=(support**0.5)*compatibility*strength_fit
   scores[label]=scores.get(label,0)+score;evidence.setdefault(label,[]).append({'support':support,'proposed':hp,'strength_fit':round(strength_fit,3),'eligible':h.get('status')=='ELIGIBLE_FOR_HUMAN_REVIEW'})
  if scores:
   ordered=sorted(scores.items(),key=lambda x:x[1],reverse=True);pred=ordered[0][0];top=ordered[0][1];second=ordered[1][1] if len(ordered)>1 else 0;conf=round(top/(top+second),3) if top+second else 0;status='LEARNED_HEURISTIC' if conf>=0.60 else 'LOW_CONFIDENCE'
  else: pred='UNCLASSIFIED';conf=0;status='NO_LEARNED_HEURISTIC';ordered=[]
  results.append({'relationship_id':r.get('relationship_id'),'match_strength':r.get('match_strength'),'proposed_signal':proposed,'predicted_classification':pred,'confidence':conf,'evidence_scores':dict(ordered),'evidence_detail':evidence,'prediction_status':status,'requires_human_validation':True})
 data={'engine':'CORE A.C.E. Blind Generalization Test','mode':'READ_ONLY','holdout_size':len(holdout),'calibration_outcomes_available':len(heur),'contrastive_groups':ace.get('contrastive_groups',[]),'predictions':results,'summary':{'predicted_with_learned_heuristic':sum(x['prediction_status']=='LEARNED_HEURISTIC' for x in results),'low_confidence':sum(x['prediction_status']=='LOW_CONFIDENCE' for x in results),'unclassified':sum(x['prediction_status']=='NO_LEARNED_HEURISTIC' for x in results),'distinct_predictions':len(set(x['predicted_classification'] for x in results))},'safety':{'holdout_excluded_from_training':True,'automatic_canon_change':False,'automatic_ledger_update':False,'human_validation_required':True}}
 (out/'CORE_BLIND_TEST.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 md=['# CORE A.C.E. Blind Generalization Test','','Fresh discoveries are held out from the human decision ledger. All observed human outcomes compete as weighted evidence; predictions remain provisional.','',f"Holdout relationships: **{len(holdout)}**",f"Calibration outcomes available: **{len(heur)}**",f"Predicted with learned heuristic: **{data['summary']['predicted_with_learned_heuristic']}**",f"Low confidence: **{data['summary']['low_confidence']}**",f"Unclassified: **{data['summary']['unclassified']}**",f"Distinct predicted classifications: **{data['summary']['distinct_predictions']}**",'']
 for r in results: md.append(f"- `{r['relationship_id']}` — {r['match_strength']}/5 — `{r['proposed_signal']}` → **{r['predicted_classification']}** ({r['prediction_status']}, confidence {r['confidence']})")
 (out/'CORE_BLIND_TEST.md').write_text('\n'.join(md)+'\n',encoding='utf-8');print(f"CORE blind test: {len(holdout)} fresh relationships; {data['summary']['distinct_predictions']} distinct predicted classes.")
if __name__=='__main__':main()
