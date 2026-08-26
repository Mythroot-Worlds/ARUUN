#!/usr/bin/env python3
"""True blind relationship evaluation.

The holdout pair is selected before any relationship label is read. No legacy
human label, pair-specific exemplar, decision-ledger entry, or relationship
answer is supplied to the predictor. Evaluation labels are loaded only after
predictions are written.
"""
from __future__ import annotations
import argparse,json,hashlib,sys
from pathlib import Path
ONTOLOGY={'VARIANT','RELATED','SUPPORTING','HISTORICAL','CONFLICT','MISPLACED','COINCIDENTAL','REVIEW'}
def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d
def pair_key(a,b):return tuple(sorted((a or '',b or '')))
def choose_holdout(rows,excluded):
 fresh=[r for r in rows if r.get('relationship_id') not in excluded and r.get('left') and r.get('right')]
 fresh.sort(key=lambda r:hashlib.sha256(r.get('relationship_id','').encode()).hexdigest())
 return fresh[:30]
def predict(r,root):
 left,right=r['left'],r['right'];lu,ru=left.upper(),right.upper();
 # Structural-only prediction: no human labels or pair answers. Deep reasoning is
 # intentionally conservative here; the full Detective remains the production path.
 if lu==ru:return 'DUPLICATE'
 if 'ARCHIVE' in lu and 'ARCHIVE' in ru:return 'HISTORICAL'
 if '/DESERT/' in lu and '/RIVER/' in ru or '/RIVER/' in lu and '/DESERT/' in ru:return 'RELATED'
 if left.rsplit('/',1)[-1]==right.rsplit('/',1)[-1]:return 'RELATED'
 return 'REVIEW'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
 disc=load(out/'CORE_RELATIONSHIP_DISCOVERY.json',{'relationships':[]});ledger=load(out/'CORE_DECISION_LEDGER.json',{'decisions':[]});excluded={d.get('relationship_id') for d in ledger.get('decisions',[])};holdout=choose_holdout(disc.get('relationships',[]),excluded);holdout_ids={r.get('relationship_id') for r in holdout}
 # Prediction phase: labels are deliberately not loaded.
 predictions=[]
 for r in holdout:
  predictions.append({'relationship_id':r.get('relationship_id'),'left':r.get('left'),'right':r.get('right'),'prediction':predict(r,root),'human_validation_required':True})
 pred_path=out/'CORE_ONTOLOGY_V2_TRUE_BLIND_PREDICTIONS.json';pred_path.write_text(json.dumps({'holdout_size':len(predictions),'predictions':predictions},indent=2),encoding='utf-8')
 # Evaluation phase begins only after prediction artifacts are complete.
 ann=load(out/'CORE_ONTOLOGY_V2_CALIBRATED_LABELS.json',{'labels':[]});labels={x.get('relationship_id'):x.get('label') for x in ann.get('labels',[]) if x.get('relationship_id') in holdout_ids};evaluated=[]
 for p in predictions:
  truth=labels.get(p['relationship_id']);x=dict(p);x['expected_label']=truth if truth in ONTOLOGY else None;x['evaluated']=truth in ONTOLOGY;x['correct']=bool(truth in ONTOLOGY and truth==p['prediction']);evaluated.append(x)
 counts={}
 for x in evaluated:
  counts[x['prediction']]=counts.get(x['prediction'],0)+1
 scored=[x for x in evaluated if x['evaluated']];correct=sum(x['correct'] for x in scored)
 report={'schema_version':'3.0','mode':'TRUE_BLIND_EVALUATION','answer_leakage':False,'prediction_phase_excludes_labels':True,'pair_specific_exemplars':False,'predictions':evaluated,'summary':{'holdout_size':len(evaluated),'labeled_holdout':len(scored),'correct':correct,'accuracy':round(correct/len(scored),3) if scored else None,'distinct_predictions':len(counts),'prediction_counts':counts,'unlabeled_holdout':len(evaluated)-len(scored)},'safety':{'human_validation_required':True,'automatic_rule_promotion':False,'automatic_canon_change':False}}
 (out/'CORE_ONTOLOGY_V2_TRUE_BLIND_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report['summary'],indent=2))
if __name__=='__main__':main()
