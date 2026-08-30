#!/usr/bin/env python3
"""CORE A.C.E. Cross-Check: validate the evidence path taken by each case.

Directly triaged cases do not require Robin coverage. Escalated cases are
cross-checked against Robin using the complete Detective investigation,
including later evidence rounds, so resolved evidence is not lost after the
first search pass.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from core_deciding_factor_questions import QUESTIONS

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def detective_factor_evidence(bat, dimension):
    """Merge all Detective rounds for a dimension instead of trusting round 1."""
    merged=[]
    for rnd in bat.get('investigation_rounds_detail',[]):
        for item in rnd.get('evidence_validity',[]):
            if item.get('dimension') == dimension:
                merged.append(item)
    if not merged:
        return {}
    return {
        'question': merged[-1].get('question', QUESTIONS[dimension]),
        'answers_question': any(bool(x.get('answers_question')) for x in merged),
        'answerability': max((x.get('answerability',0) or 0) for x in merged),
        'direct_claims': sum(x.get('direct_claims',0) or 0 for x in merged),
        'grounded_direct_claims': sum(x.get('grounded_direct_claims',0) or 0 for x in merged),
        'pair_resolving_claims': sum(x.get('pair_resolving_claims',0) or 0 for x in merged),
        'contextual_claims': sum(x.get('contextual_claims',0) or 0 for x in merged),
        'round_count': len(merged),
    }

def cross_case(bat,rob):
 if bat.get('triage_status')=='DIRECT':
  return {'relationship_id':bat.get('relationship_id'),'documents':bat.get('documents',{}),'dimensions':[],'corroborated_count':0,'contradiction_count':0,'unresolved_count':0,'status':'DIRECT_TRIAGE','role_note':'Case was resolved by structural document triage; Batman/Robin investigation was intentionally not required.'}
 r=rob.get('robin_results',{});rows=[]
 for d in QUESTIONS:
  bv=detective_factor_evidence(bat,d);rv=r.get(d,{})
  ba=bool(bv.get('answers_question'))
  robin_state=rv.get('relationship_state',rv.get('evidence_state','NO_SIGNAL'))
  rs=robin_state in {'SAME','MIXED','DIFFERENT'}
  contradiction=bool(rv.get('contradiction_signal'))
  if contradiction:state='CONTRADICTED'
  elif ba and rs:state='CORROBORATED'
  elif ba:state='BATMAN_UNCORROBORATED'
  elif rs:state='ROBIN_SUPPORT_ONLY'
  else:state='UNRESOLVED'
  rows.append({'dimension':d,'question':QUESTIONS[d],'batman_answered':ba,'batman_rounds_considered':bv.get('round_count',0),'robin_factor_state':robin_state,'robin_factor_support':rs,'state':state,'batman_answerability':bv.get('answerability',0),'robin_confidence':rv.get('confidence','none'),'ambiguity_signals':rv.get('ambiguity_signals',0),'contradiction_signal':contradiction})
 corroborated=sum(x['state']=='CORROBORATED' for x in rows);contradicted=sum(x['state']=='CONTRADICTED' for x in rows);unresolved=sum(x['state']=='UNRESOLVED' for x in rows)
 status='CONTRADICTION' if contradicted else ('CORROBORATED' if corroborated and unresolved==0 else ('MIXED_COVERAGE' if corroborated else 'EVIDENCE_GAP'))
 return {'relationship_id':bat.get('relationship_id'),'documents':bat.get('documents',{}),'dimensions':rows,'corroborated_count':corroborated,'contradiction_count':contradicted,'unresolved_count':unresolved,'status':status,'role_note':'Batman solves the relationship; Robin investigates factors. All Detective evidence rounds are considered; absence of Robin support is not a conflict.'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();out=Path(x.root).resolve()/x.out;bd=load(out/'CORE_DETECTIVE_REPORT.json',{'cases':[]});rd=load(out/'CORE_ROBIN_REPORT.json',{'cases':[]});rmap={c.get('relationship_id'):c for c in rd.get('cases',[])};cases=[cross_case(c,rmap.get(c.get('relationship_id'),{})) for c in bd.get('cases',[])];summary={'cases':len(cases),'direct_triage':sum(c['status']=='DIRECT_TRIAGE' for c in cases),'corroborated':sum(c['status']=='CORROBORATED' for c in cases),'mixed_coverage':sum(c['status']=='MIXED_COVERAGE' for c in cases),'evidence_gap':sum(c['status']=='EVIDENCE_GAP' for c in cases),'contradiction':sum(c['status']=='CONTRADICTION' for c in cases),'corroborated_dimensions':sum(c['corroborated_count'] for c in cases),'contradiction_dimensions':sum(c['contradiction_count'] for c in cases),'unresolved_dimensions':sum(c['unresolved_count'] for c in cases),'factor_dimensions_available':len(QUESTIONS)};payload={'engine':'CORE A.C.E. Cross-Check','schema_version':'2.2','mode':'READ_ONLY','purpose':'cross-reference deep Batman/Robin cases while preserving complete Detective evidence coverage','cases':cases,'summary':summary,'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}};(out/'CORE_CROSSCHECK_REPORT.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_CROSSCHECK_REPORT.md').write_text('# CORE Batman / Robin Cross-Check\n\n'+json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
