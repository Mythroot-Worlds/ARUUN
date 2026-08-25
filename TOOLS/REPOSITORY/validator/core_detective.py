#!/usr/bin/env python3
"""CORE A.C.E. Batman: bounded relationship case solver.

Routine cases are handled by document triage first. Batman investigates only
cases whose identity, scope, role, or relationship remains genuinely ambiguous.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from core_foundations import factor_snapshot
from core_deciding_factor_questions import QUESTIONS
from core_relationship_reasoning_v2 import evaluate_relationships
from core_document_triage import triage
from mythroot_profile import profile_snapshot

DEFAULT_POOL_SIZE=10
MAX_POOL_SIZE=20
TOKENS={'scope':['CONTINENT','CONTINENTAL','HEARTH-WIDE','REGIONAL','REGION','MOUNTAIN','RIVER','PLAINS','SETTLEMENT','VILLAGE','LOCAL','WETLANDS','DESERT','COAST'],'function':['FAMILY','BIRTH','CHILDHOOD','MARRIAGE','KIN','HOUSEHOLD','GOVERNANCE','AUTHORITY','LEADERSHIP','SPECIALIST','LINEAGE','SUPPORT','CHECKLIST','AUDIT','REFERENCE','HISTORICAL','ARCHIVE','REVISION'],'authority':['AUTHORITY','LEADERSHIP','GOVERNANCE','COUNCIL','LEADER','HEAD','HOUSE'],'support':['SUPPORT','INFORMS','REFERENCES','DERIVED FROM','BASED ON','BUILDS ON','CHECKLIST','AUDIT','REFERENCE'],'temporal':['REVISED','SUPERSEDES','REPLACED','PREVIOUS','FORMER','EARLIER','CURRENT','OLDER','REVISION','HISTORICAL']}

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def read(path,root,limit=60000):
 try:return (root/path).read_text(encoding='utf-8')[:limit]
 except:return ''

def files(root):return [str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*.md') if '.git' not in p.parts and 'REPORTS' not in p.parts]

def anchors(a,b):
 f=lambda p:{x for x in re.split(r'[^a-z0-9]+',Path(p).stem.lower()) if len(x)>=4 and x not in {'family','regional','document','draft','final','version','comparative','hearth','region','regions'}}
 return f(a)&f(b) or f(a)|f(b)

def candidates(a,b,root,exclude=(),pool=DEFAULT_POOL_SIZE):
 aa=anchors(a,b);used={a,b,*exclude};rows=[]
 for p in files(root):
  if p in used:continue
  t=read(p,root).upper();score=sum(2*sum(w in t for w in ws) for ws in TOKENS.values())+4*sum(x.upper() in t for x in aa)
  if score:rows.append((score,p))
 return [p for _,p in sorted(rows,key=lambda z:(z[0],z[1]),reverse=True)[:max(1,min(pool,MAX_POOL_SIZE))]]

def passages(path,root,dimension):
 lines=read(path,root).splitlines();words=TOKENS.get(dimension,[]);out=[];seen=set()
 for i,line in enumerate(lines):
  if any(w in line.upper() for w in words):
   s=' '.join(lines[max(0,i-1):min(len(lines),i+2)]).strip();k=re.sub(r'\s+',' ',s).lower()
   if k not in seen:seen.add(k);out.append(s)
 return out[:8]

def collect(paths,root,dimension,aa):
 out=[];seen=set();relation=('SAME','VARIANT','DUPLICATE','SUPPORTING','HISTORICAL','CONFLICT','RELATED','MISPLACED','BASED ON','DERIVED FROM','REFERENCES','INFORMS','SUPERSEDES','REPLACES')
 for p in paths:
  for s in passages(p,root,dimension):
   u=s.upper();hits=[x for x in aa if x.upper() in u];direct=bool(hits or any(x in u for x in relation));k=(p,s,dimension)
   if k in seen:continue
   seen.add(k);out.append({'source':p,'passage':s,'dimension':dimension,'claim':s,'claim_type':'DIRECT' if hits else ('CONTEXTUAL' if direct else 'KEYWORD_ONLY'),'quality_score':1.0 if hits else (.5 if direct else .1),'grounded':bool(hits),'pair_relevant':bool(hits),'pair_anchors':sorted(hits),'source_role':'supporting' if any(x in p.upper() for x in ['CHECKLIST','AUDIT','FRAMEWORK','GUIDE']) else 'primary'})
 return out

def validity(question,dimension,claims):
 rel=[c for c in claims if c['dimension']==dimension];grounded=[c for c in rel if c['grounded']];return {'question':question,'dimension':dimension,'answerability':1.0 if grounded else (.5 if rel else 0.0),'answers_question':bool(grounded),'direct_claims':sum(c['claim_type']=='DIRECT' for c in rel),'grounded_direct_claims':len(grounded),'pair_resolving_claims':sum(c['pair_relevant'] for c in rel),'contextual_claims':sum(c['claim_type']=='CONTEXTUAL' for c in rel),'evidence_quality':rel}

def investigate(r,root,robin,pool,triage_result):
 if triage_result.get('triage_status')=='DIRECT':
  return {'relationship_id':r.get('relationship_id'),'documents':{'a':r.get('left',''),'b':r.get('right','')},'role':'case_solver','triage_status':'DIRECT','triage_decision':triage_result['decision'],'triage_reason':triage_result['reason'],'triage_evidence':triage_result['evidence'],'relationship_reasoning':{'decision':triage_result['decision'],'confidence':'STRUCTURAL','decision_basis':triage_result['reason'],'candidates':[triage_result['decision']],'viable_relationships':[triage_result['decision']],'unresolved_dimensions':[]},'case_question':{'question':'What is this document relationship and where does it belong?','status':'resolved_by_triage'},'investigation_rounds':0,'investigation_rounds_detail':[],'evidence_targets':[],'evidence_claims':[],'unknown_after':[],'evidence_updates':[{'type':'triage_update','effect':'resolved_without_deep_investigation','basis':triage_result['reason']}],'evidence_quality_summary':{'direct_claims':0,'grounded_direct_claims':0,'pair_resolving_claims':0,'contextual_claims':0,'unique_claims':0},'stop_reason':'clear relationship resolved by document triage; Batman not required','safety':{'self_training':False,'automatic_rule_promotion':False,'automatic_canon_change':False}}
 a,b=r.get('left',''),r.get('right','');factor_map=factor_snapshot(read(a,root),read(b,root));robin_dims=robin.get('robin_results',{});aa=anchors(a,b);targets=candidates(a,b,root,pool=pool);claims=[];vals=[]
 for d,q in QUESTIONS.items():
  cs=collect([a,b]+targets,root,d,aa);claims.extend(cs);vals.append(validity(q,d,cs))
 unresolved=[v['dimension'] for v in vals if not v['answers_question']];second=candidates(a,b,root,exclude=targets,pool=pool) if unresolved else [];second_vals=[]
 for d in unresolved:
  cs=collect(second,root,d,aa);claims.extend(cs);second_vals.append(validity(QUESTIONS[d],d,cs))
 resolved2=[v['dimension'] for v in second_vals if v['answers_question']];remaining=[d for d in unresolved if d not in resolved2]
 rounds=[{'round':1,'trigger':'ambiguous case investigation','evidence_targets':targets,'evidence_validity':vals,'unanswered_after_round':unresolved}]
 if second:rounds.append({'round':2,'trigger':'unresolved deciding factors after round 1','evidence_targets':second,'evidence_validity':second_vals,'unanswered_after_round':remaining})
 reasoning=evaluate_relationships(robin_dims) if robin_dims else {'decision':'REVIEW','confidence':'LOW','decision_basis':'Robin factor matrix missing','candidates':[],'viable_relationships':[],'unresolved_dimensions':list(QUESTIONS)}
 return {'relationship_id':r.get('relationship_id'),'documents':{'a':a,'b':b},'role':'case_solver','triage_status':'ESCALATE','triage_decision':triage_result.get('decision'),'triage_reason':triage_result.get('reason'),'domain_profile':profile_snapshot()['name'],'deciding_factors':factor_map['dimensions'],'factor_question_count':len(QUESTIONS),'robin_factor_investigation':robin_dims,'robin_handoff_status':'RECEIVED' if robin_dims else 'MISSING','relationship_reasoning':reasoning,'case_question':{'question':'What relationship is actually supported between these two artifacts?','status':'deep_investigation'},'investigation_rounds':len(rounds),'investigation_rounds_detail':rounds,'evidence_targets':targets,'evidence_claims':claims,'unknown_after':remaining,'evidence_updates':[{'type':'evidence_update','effect':'reduced_uncertainty','resolved_factors':resolved2,'basis':'Batman case solving after Robin factor investigation'}] if resolved2 else [],'evidence_quality_summary':{'direct_claims':sum(c['claim_type']=='DIRECT' for c in claims),'grounded_direct_claims':sum(c['grounded'] for c in claims),'pair_resolving_claims':sum(c['pair_relevant'] for c in claims),'contextual_claims':sum(c['claim_type']=='CONTEXTUAL' for c in claims),'unique_claims':len({(c['source'],c['passage'],c['dimension']) for c in claims})},'stop_reason':'ambiguous relationship escalated to Batman/Robin; human adjudication remains authoritative','safety':{'self_training':False,'automatic_rule_promotion':False,'automatic_canon_change':False}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');ap.add_argument('--pool-size',type=int,default=DEFAULT_POOL_SIZE);x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out;pool=max(1,min(x.pool_size,MAX_POOL_SIZE));queue=load(out/'CORE_ADJUDICATION_QUEUE.json',{'queue':[]});rr=load(out/'CORE_ROBIN_REPORT.json',{'cases':[]});rmap={c.get('relationship_id'):c for c in rr.get('cases',[])};triage_report=load(out/'CORE_DOCUMENT_TRIAGE.json',{'cases':[]});tmap={c.get('relationship_id'):c for c in triage_report.get('cases',[])};live=queue.get('queue',[]);source='CORE_ADJUDICATION_QUEUE.json';cases=[investigate(r,root,rmap.get(r.get('relationship_id'),{}),pool,tmap.get(r.get('relationship_id'),triage(r,root))) for r in live];decisions={};triage_counts={'DIRECT':0,'ESCALATE':0}
 for c in cases:
  d=c.get('relationship_reasoning',{}).get('decision','REVIEW');decisions[d]=decisions.get(d,0)+1;triage_counts[c.get('triage_status','ESCALATE')]=triage_counts.get(c.get('triage_status','ESCALATE'),0)+1
 summary={'cases':len(cases),'case_source':source,'triage_direct':triage_counts.get('DIRECT',0),'triage_escalated':triage_counts.get('ESCALATE',0),'deep_investigation_rate':round(triage_counts.get('ESCALATE',0)/max(1,len(cases)),3),'cases_using_robin_factor_map':sum(bool(c.get('robin_factor_investigation')) for c in cases),'cases_missing_robin_factor_map':sum(not bool(c.get('robin_factor_investigation')) for c in cases),'cases_with_unresolved_factors':sum(bool(c.get('unknown_after')) for c in cases),'grounded_direct_claims':sum(c['evidence_quality_summary']['grounded_direct_claims'] for c in cases),'pair_resolving_claims':sum(c['evidence_quality_summary']['pair_resolving_claims'] for c in cases),'relationship_decisions':decisions,'cases_with_non_review_decision':sum(c['relationship_reasoning']['decision']!='REVIEW' for c in cases),'cases_escalated_to_review':sum(c['relationship_reasoning']['decision']=='REVIEW' for c in cases)}
 payload={'engine':'CORE A.C.E. Detective','schema_version':'3.4','mode':'READ_ONLY','purpose':'simple document triage first; deep Batman/Robin investigation only for genuinely ambiguous cases','cases':cases,'summary':summary,'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
 (out/'CORE_DETECTIVE_REPORT.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_DETECTIVE_REPORT.md').write_text('# CORE A.C.E. Detective Case Solver\n\n'+json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
