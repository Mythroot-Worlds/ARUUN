#!/usr/bin/env python3
"""CORE Relationship Metrics — stable relationship discovery telemetry."""
from __future__ import annotations
import argparse,json,hashlib
from collections import Counter
from pathlib import Path

def load(p,d):
 try:return json.loads(p.read_text(encoding="utf-8")) if p.exists() else d
 except:return d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out;out.mkdir(parents=True,exist_ok=True)
 ledger=load(out/'CORE_DECISION_LEDGER.json',{'decisions':[]}); decisions=ledger.get('decisions',[])
 ace=load(out/'CORE_ACE_CALIBRATION_REPORT.json',{'decision_count':0,'heuristic_candidates':[]})
 # Each adjudicated example is a stable relationship record for the calibration corpus.
 rel=[]
 for d in decisions:
  rid=d.get('relationship_id') or 'REL-'+hashlib.sha1(d.get('id','').encode()).hexdigest()[:12]
  rel.append({'relationship_id':rid,'candidate':d.get('candidate'),'proposed':d.get('proposed'),'final':d.get('label'),'status':'HUMAN_CONFIRMED','context':d.get('context',{})})
 counts=Counter(x['final'] for x in rel); proposed=Counter(x['proposed'] for x in rel)
 data={'engine':'CORE Relationship Metrics','mode':'TELEMETRY_ONLY','relationship_count':len(rel),'candidate_count':len(rel),'human_confirmed_count':len(rel),'unresolved_count':sum(1 for x in rel if x['final']=='REVIEW'),'by_final_label':dict(sorted(counts.items())),'by_proposed_label':dict(sorted(proposed.items())),'ace_decisions':ace.get('decision_count',0),'ace_heuristic_candidates':len(ace.get('heuristic_candidates',[])),'relationship_records':rel,'run_comparison_note':'Persist these metrics between runs to calculate discovery growth, novelty, confirmation rate, false-positive rate, and coverage once candidate discovery telemetry is available.','safety':{'automatic_relationship_acceptance':False,'automatic_canon_change':False,'stable_relationship_ids':True,'provenance_required':True}}
 (out/'CORE_RELATIONSHIP_METRICS.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 md=['# CORE Relationship Metrics','','**Telemetry only.** These metrics measure relationships and human adjudication; they do not authorize canon changes.','',f"Human-confirmed relationships: **{len(rel)}**",f"Unresolved: **{data['unresolved_count']}**",f"A.C.E. labeled decisions: **{ace.get('decision_count',0)}**",f"A.C.E. heuristic candidates: **{len(ace.get('heuristic_candidates',[]))}**",'','## Final labels']+[f'- `{k}`: **{v}**' for k,v in sorted(counts.items())]+['','## Next-run metrics','- Discovery growth','- Novel relationship discovery','- Human confirmation rate','- False-positive rate','- Coverage','- Anomaly recognition rate','']
 (out/'CORE_RELATIONSHIP_METRICS.md').write_text('\n'.join(md),encoding='utf-8')
 print(f'CORE relationship metrics: {len(rel)} stable adjudicated relationships.')
if __name__=='__main__':main()
