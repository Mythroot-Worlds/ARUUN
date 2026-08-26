#!/usr/bin/env python3
"""Evaluate relationship reasoning against the corrected ontology without leaking pair answers."""
from __future__ import annotations
import json
from pathlib import Path
ONTOLOGY={"VARIANT","RELATED","SUPPORTING","HISTORICAL","CONFLICT","MISPLACED","COINCIDENTAL","REVIEW"}
def main():
 root=Path('TOOLS/REPOSITORY/REPORTS')
 live=json.loads((root/'CORE_DETECTIVE_REPORT.json').read_text(encoding='utf-8')) if (root/'CORE_DETECTIVE_REPORT.json').exists() else {'cases':[]}
 cases=[]
 for c in live.get('cases',[]):
  d=c.get('relationship_reasoning',{}).get('decision','REVIEW')
  cases.append({'relationship_id':c.get('relationship_id'),'prediction':d if d in ONTOLOGY else 'REVIEW','source':'live_reasoning','exemplar_used':False})
 counts={}
 for c in cases: counts[c['prediction']]=counts.get(c['prediction'],0)+1
 distinct=len(counts)
 report={'schema_version':'2.0','mode':'EVALUATION_ONLY','answer_leakage':False,'ontology_labels':sorted(ONTOLOGY),'cases':cases,'summary':{'cases':len(cases),'distinct_predictions':distinct,'prediction_counts':counts,'collapsed_to_single_label':distinct<=1},'policy':'Legacy human labels are not used as pair-level answers. They remain immutable calibration evidence and review material.'}
 (root/'CORE_ONTOLOGY_V2_BLIND_BENCHMARK.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps(report['summary'],indent=2))
if __name__=='__main__':main()
