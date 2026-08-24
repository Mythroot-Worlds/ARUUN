#!/usr/bin/env python3
"""CORE A.C.E. blind generalization test.

Uses only learned heuristics to score a fresh holdout of discovered relationships.
It never writes labels into the decision ledger and never changes canon.
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
 learned={(h.get('domain'),h.get('role'),h.get('proposed'),h.get('observed_label')):h.get('support',0) for h in ace.get('heuristic_candidates',[]) if h.get('status')=='ELIGIBLE_FOR_HUMAN_REVIEW'}
 # Hold out relationships not already represented by a human decision ID. Deterministic selection.
 ledger=load(out/'CORE_DECISION_LEDGER.json',{'decisions':[]}); known={d.get('relationship_id') for d in ledger.get('decisions',[])}
 fresh=[r for r in disc.get('relationships',[]) if r.get('relationship_id') not in known]
 fresh.sort(key=lambda r: hashlib.sha1(r.get('relationship_id','').encode()).hexdigest())
 holdout=fresh[:min(30,len(fresh))]
 results=[]
 for r in holdout:
  proposed='DUPLICATE' if r.get('match_strength',0)>=4 else 'MERGE'
  domain='PEOPLES'; role='CANON'
  applicable=[(label,s) for (d,ro,p,label),s in learned.items() if d==domain and ro==role and p==proposed]
  predicted=max(applicable,key=lambda x:x[1])[0] if applicable else 'UNCLASSIFIED'
  results.append({'relationship_id':r.get('relationship_id'),'match_strength':r.get('match_strength'),'proposed':proposed,'predicted_classification':predicted,'prediction_status':'LEARNED_HEURISTIC' if predicted!='UNCLASSIFIED' else 'NO_LEARNED_HEURISTIC','requires_human_validation':True})
 data={'engine':'CORE A.C.E. Blind Generalization Test','mode':'READ_ONLY','holdout_size':len(holdout),'learned_heuristics_available':len(learned),'predictions':results,'safety':{'holdout_excluded_from_training':True,'automatic_canon_change':False,'automatic_ledger_update':False,'human_validation_required':True}}
 (out/'CORE_BLIND_TEST.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 md=['# CORE A.C.E. Blind Generalization Test','','Fresh discoveries are held out from the human decision ledger. Predictions are provisional and require human validation.','',f"Holdout relationships: **{len(holdout)}**",f"Eligible learned heuristics available: **{len(learned)}**",'']
 for r in results:md.append(f"- `{r['relationship_id']}` — {r['match_strength']}/5 — proposed `{r['proposed']}` → **{r['predicted_classification']}** ({r['prediction_status']})")
 (out/'CORE_BLIND_TEST.md').write_text('\n'.join(md)+'\n',encoding='utf-8');print(f'CORE blind test: {len(holdout)} fresh relationships, {len(learned)} eligible heuristics.')
if __name__=='__main__':main()
