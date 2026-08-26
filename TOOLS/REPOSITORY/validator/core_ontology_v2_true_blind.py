#!/usr/bin/env python3
"""True blind relationship evaluation.

Prediction is completed before any trusted evaluation label is loaded. The
holdout is restricted to an explicit human-trusted holdout produced from
unambiguous human reconciliation annotations. Multi-choice/disputed labels
remain excluded until separately adjudicated.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
from core_document_triage import triage
ONTOLOGY={'VARIANT','RELATED','SUPPORTING','HISTORICAL','CONFLICT','MISPLACED','COINCIDENTAL','REVIEW'}
def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def choose_holdout(trusted_holdout,excluded):
    records=[r for r in trusted_holdout.get('records',[]) if r.get('relationship_id') not in excluded and r.get('trusted_label') in ONTOLOGY and r.get('left') and r.get('right')]
    records.sort(key=lambda r:hashlib.sha256(r.get('relationship_id','').encode()).hexdigest())
    return records[:30]

def predict(r,root):
    # Production triage receives only the pair. No trusted answer label is passed in.
    result=triage({'relationship_id':r.get('relationship_id'),'left':r.get('left',''),'right':r.get('right','')},root)
    decision=result.get('decision','REVIEW')
    return decision if decision in ONTOLOGY else 'REVIEW',result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    trusted=load(out/'CORE_TRUSTED_ONTOLOGY_V2_HOLDOUT.json',{'records':[]})
    ledger=load(out/'CORE_DECISION_LEDGER.json',{'decisions':[]});excluded={d.get('relationship_id') for d in ledger.get('decisions',[])}
    holdout=choose_holdout(trusted,excluded)
    # PREDICTION PHASE: trusted answer labels are not read or passed to triage.
    predictions=[]
    for r in holdout:
        pred,detail=predict(r,root)
        predictions.append({'relationship_id':r.get('relationship_id'),'left':r.get('left'),'right':r.get('right'),'prediction':pred,'triage_status':detail.get('triage_status'),'decision_basis':detail.get('layered_comparison',{}).get('decision_basis',{}),'human_validation_required':True})
    (out/'CORE_ONTOLOGY_V2_TRUE_BLIND_PREDICTIONS.json').write_text(json.dumps({'holdout_size':len(predictions),'predictions':predictions},indent=2),encoding='utf-8')
    # EVALUATION PHASE: only now reveal the trusted human answer key.
    labels={r.get('relationship_id'):r.get('trusted_label') for r in trusted.get('records',[]) if r.get('trusted_label') in ONTOLOGY}
    evaluated=[]
    for p in predictions:
        truth=labels.get(p['relationship_id']);x=dict(p);x['expected_label']=truth if truth in ONTOLOGY else None;x['evaluated']=truth in ONTOLOGY;x['correct']=bool(truth in ONTOLOGY and truth==p['prediction']);evaluated.append(x)
    counts={}
    for x in evaluated:counts[x['prediction']]=counts.get(x['prediction'],0)+1
    scored=[x for x in evaluated if x['evaluated']];correct=sum(x['correct'] for x in scored)
    report={'schema_version':'5.0','mode':'TRUE_BLIND_EVALUATION','answer_leakage':False,'prediction_phase_excludes_answer_key':True,'answer_key_policy':'Only explicitly human-trusted single-choice records from CORE_TRUSTED_ONTOLOGY_V2_HOLDOUT.json are eligible; multi-choice/disputed annotations remain excluded.','holdout_source':'CORE_TRUSTED_ONTOLOGY_V2_HOLDOUT.json','pair_specific_exemplars':False,'predictions':evaluated,'summary':{'holdout_size':len(evaluated),'labeled_holdout':len(scored),'correct':correct,'accuracy':round(correct/len(scored),3) if scored else None,'distinct_predictions':len(counts),'prediction_counts':counts,'unlabeled_holdout':len(evaluated)-len(scored)},'safety':{'human_validation_required':True,'automatic_rule_promotion':False,'automatic_canon_change':False,'multi_choice_labels_excluded':True}}
    (out/'CORE_ONTOLOGY_V2_TRUE_BLIND_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report['summary'],indent=2))
    if not scored: raise SystemExit('True-blind benchmark has no explicitly human-trusted labeled holdout cases')
if __name__=='__main__':main()
