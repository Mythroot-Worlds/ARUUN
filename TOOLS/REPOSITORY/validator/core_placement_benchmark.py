#!/usr/bin/env python3
"""Placement-first benchmark: score where a document belongs, not label trivia."""
from __future__ import annotations
import json
from pathlib import Path

def norm(p): return Path(p).as_posix().upper()
def expected(path):
 p=norm(path)
 if '/03_PEOPLES/CULTURES/HEARTH/' in p:
  for r in ('PLAINS','MOUNTAINS','RIVER','WETLANDS','DESERT','COAST'):
   if f'/HEARTH/{r}/' in p:return f'03_PEOPLES/CULTURES/HEARTH/{r}'
  if '/COMPARATIVE/' in p:return '03_PEOPLES/CULTURES/HEARTH/COMPARATIVE'
  return '03_PEOPLES/CULTURES/HEARTH'
 if '/07_ARCHIVE/HISTORICAL/' in p:return '07_ARCHIVE/HISTORICAL'
 return str(Path(path).parent)
def main():
 root=Path('TOOLS/REPOSITORY/REPORTS'); tri=root/'CORE_DOCUMENT_TRIAGE.json';data=json.loads(tri.read_text(encoding='utf-8')) if tri.exists() else {'cases':[]};rows=[]
 for c in data.get('cases',[]):
  for side in ('a','b'):
   path=c.get('documents',{}).get(side,''); actual=c.get('placement',{}).get(side,{}); exp=expected(path); proposed=actual.get('scope',{}).get('region')
   if proposed: proposed=f'03_PEOPLES/CULTURES/HEARTH/{proposed}'
   elif actual.get('role')=='HISTORICAL': proposed='07_ARCHIVE/HISTORICAL'
   elif actual.get('content_type')=='CULTURE': proposed='03_PEOPLES/CULTURES/HEARTH'
   else: proposed=str(Path(path).parent)
   rows.append({'relationship_id':c.get('relationship_id'),'document':path,'expected_parent':exp,'proposed_parent':proposed,'placement_correct':proposed==exp,'relationship_decision':c.get('decision'),'relationship_tags':c.get('layered_comparison',{}).get('relationship_tags',[]),'placement_basis':actual})
 correct=sum(x['placement_correct'] for x in rows);total=len(rows);critical=[x for x in rows if not x['placement_correct'] and '/03_PEOPLES/CULTURES/HEARTH/' in norm(x['document'])]
 report={'schema_version':'1.0','mode':'READ_ONLY','purpose':'measure placement correctness independently of relationship label perfection','cases':rows,'summary':{'documents':total,'correct_placements':correct,'incorrect_placements':total-correct,'placement_accuracy':round(correct/total,3) if total else None,'critical_wrong_hearth_placements':len(critical),'relationship_tag_is_not_placement_gate':True},'safety':{'automatic_move':False,'automatic_canon_change':False,'human_validation_required':True}}
 (root/'CORE_PLACEMENT_BENCHMARK.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report['summary'],indent=2))
if __name__=='__main__':main()
