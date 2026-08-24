#!/usr/bin/env python3
"""CORE A.C.E. Detective: bounded investigation with deciding-factor context."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from core_foundations import factor_snapshot
DEFAULT_POOL_SIZE=10
MAX_POOL_SIZE=20
FOCUS={'authority':['AUTHORITY','LEADERSHIP','GOVERNANCE','COUNCIL','LEADER','HEAD','HOUSE'],'scope':['CONTINENT','CONTINENTAL','HEARTH-WIDE','REGIONAL','REGION','MOUNTAIN','RIVER','PLAINS','SETTLEMENT','VILLAGE','LOCAL'],'support':['SUPPORT','INFORMS','REFERENCES','DERIVED FROM','BASED ON','BUILDS ON','CHECKLIST','AUDIT','REFERENCE'],'temporal':['REVISED','SUPERSEDES','REPLACED','PREVIOUS','FORMER','EARLIER','CURRENT','OLDER','REVISION','HISTORICAL'],'family':['FAMILY','BIRTH','CHILDHOOD','MARRIAGE','KIN','HOUSEHOLD'],'specialist':['SPECIALIST','LINEAGE','HOUSE','CRAFT','KEEPER']}

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def read(path,root,limit=60000):
 try:return (root/path).read_text(encoding='utf-8')[:limit]
 except:return ''

def terms(text):
 u=text.upper();return {k:sorted({w for w in ws if re.search(r'\b'+re.escape(w)+r'\b',u)}) for k,ws in FOCUS.items()}

def files(root):return [str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*.md') if '.git' not in p.parts and 'REPORTS' not in p.parts]

def candidates(a,b,root,exclude=(),pool=DEFAULT_POOL_SIZE):
 ta,tb=terms(read(a,root)),terms(read(b,root));excluded={a,b,*exclude};rows=[]
 for p in files(root):
  if p in excluded:continue
  t=terms(read(p,root));score=0
  for k in FOCUS: score += 2*len((set(ta[k])|set(tb[k])) & set(t[k]))
  if score:rows.append((score,p))
 return [p for _,p in sorted(rows,key=lambda x:(x[0],x[1]),reverse=True)[:max(1,min(pool,MAX_POOL_SIZE))]]

def question_for(u):
 l=u.lower()
 if 'authority' in l:return ('authority','Which source explicitly establishes the organizational authority, leadership role, and scope of the disputed document?')
 if 'support' in l:return ('support','Which source explicitly establishes that one document supports, informs, references, or derives from the other?')
 if 'temporal' in l:return ('temporal','Which source establishes the temporal relationship, revision, supersession, or historical precedence between these documents?')
 return ('general','What specific source evidence would resolve the remaining uncertainty?')

def passages(path,root,dimension):
 lines=read(path,root).splitlines();words=FOCUS.get(dimension,[]);out=[];seen=set()
 for i,line in enumerate(lines):
  if any(w in line.upper() for w in words):
   text=' '.join(lines[max(0,i-1):min(len(lines),i+2)]).strip();key=re.sub(r'\s+',' ',text).lower()
   if key not in seen:seen.add(key);out.append(text)
 return out[:6]

def extract_entities(text):
 vals=[]
 for m in re.finditer(r'\b(?:the\s+)?([A-Z][A-Za-z0-9_-]{2,}(?:\s+[A-Z][A-Za-z0-9_-]{2,}){0,4})\b',text):
  v=m.group(1).strip(' .,;:()[]');
  if v.upper() not in {'THE','THIS','THAT','WHICH','DOCUMENT','SOURCE','CURRENT','FORMER'} and v not in vals: vals.append(v)
 return vals[:12]

def claim_from(path,text,dimension,question_entities=()):
 u=text.upper();patterns={'authority':r'(?:(?:AUTHORITY|LEADER|LEADERSHIP|GOVERNANCE|COUNCIL|HEAD).{0,140}(?:VILLAGE|SETTLEMENT|REGION|REGIONAL|CONTINENT|CONTINENTAL)|(?:VILLAGE|SETTLEMENT|REGION|REGIONAL|CONTINENT|CONTINENTAL).{0,140}(?:AUTHORITY|LEADER|LEADERSHIP|GOVERNANCE|COUNCIL|HEAD))','support':r'(?:SUPPORT|INFORMS|REFERENCES|DERIVED FROM|BASED ON|BUILDS ON).{0,160}(?:DOCUMENT|GUIDE|FRAMEWORK|CHECKLIST|CANON|SOURCE)','temporal':r'(?:REVISED|SUPERSEDES|REPLACED|PREVIOUS|FORMER|EARLIER|CURRENT|OLDER|REVISION).{0,160}(?:VERSION|DOCUMENT|CANON|SOURCE|TEXT)?','general':r'(?!)'}
 direct=bool(re.search(patterns[dimension],u,re.S));contextual=bool(any(w in u for w in FOCUS.get(dimension,[])));entities=extract_entities(text)
 grounded=direct and len(entities)>=1
 if grounded:quality='DIRECT';score=1.0;reason='question_specific_relation_with_grounded_entity'
 elif contextual:quality='CONTEXTUAL';score=.5;reason='dimension_signal_without_grounded_relation'
 else:quality='KEYWORD_ONLY';score=.1;reason='weak_signal'
 up=path.upper();source='primary'
 if any(x in up for x in ['CHECKLIST','AUDIT','FRAMEWORK','GUIDE','OPERATING_RULES']):source='supporting'
 if any(x in up for x in ['ARCHIVE','HISTORICAL','REVISION']):source='historical'
 return {'source':path,'passage':text,'dimension':dimension,'claim':text,'claim_type':quality,'quality_score':score,'reason':reason,'source_role':source,'entities':entities,'grounded':grounded}

def collect_claims(paths,root,dimension):
 claims=[];seen=set()
 for p in paths:
  for text in passages(p,root,dimension):
   c=claim_from(p,text,dimension);key=(c['source'],re.sub(r'\s+',' ',text).strip().lower(),dimension)
   if key not in seen:seen.add(key);claims.append(c)
 return claims

def validity(question,dimension,claims):
 relevant=[c for c in claims if c['dimension']==dimension];direct=[c for c in relevant if c['claim_type']=='DIRECT'];context=[c for c in relevant if c['claim_type']=='CONTEXTUAL'];sources={c['source'] for c in context}
 answered=bool(direct) or len(sources)>=2
 quality=1.0 if direct else (.75 if len(sources)>=2 else (.5 if context else 0.0))
 return {'question':question,'dimension':dimension,'answerability':quality,'answers_question':answered,'direct_claims':len(direct),'contextual_claims':len(context),'independent_context_sources':len(sources),'evidence_quality':relevant,'grounded_direct_claims':sum(1 for c in direct if c['grounded'])}

def missing_targets(remaining,root,a,b,used,pool):
 targets=[];reasons=[];used=set(used)|{a,b}
 for u in remaining:
  dim,_=question_for(u);rows=[]
  for p in files(root):
   if p in used:continue
   score=len(terms(read(p,root)).get(dim,[]))
   if score:rows.append((score,p))
  for _,p in sorted(rows,key=lambda x:(x[0],x[1]),reverse=True)[:pool]:
   if p not in targets:targets.append(p);reasons.append({'missing':u,'dimension':dim,'target':p,'reason':'first pass lacked sufficient grounded claim-level evidence'})
 return targets[:pool],reasons

def investigate(r,root,pool=DEFAULT_POOL_SIZE):
 a,b=r.get('left',''),r.get('right','');ta,tb=terms(read(a,root)),terms(read(b,root));factor_map=factor_snapshot(read(a,root),read(b,root))
 unknown=[];known=[]
 for d in FOCUS:
  common=set(ta[d])&set(tb[d]);diff=set(ta[d])^set(tb[d])
  if common:known.append(f'{d}: shared {", ".join(sorted(common))}')
  if diff:known.append(f'{d}: differs {", ".join(sorted(diff))}')
 if ta['authority'] or tb['authority']:unknown.append('authority role and organizational level require contextual confirmation')
 if ta['support'] or tb['support']:unknown.append('explicit support relationship is not established by indicators alone')
 if ta['temporal'] or tb['temporal']:unknown.append('temporal precedence/supersession is not established by indicators alone')
 questions=[{'unknown':u,'question':question_for(u)[1],'dimension':question_for(u)[0]} for u in unknown];targets=candidates(a,b,root,pool=pool);rounds=[];all_claims=[];resolved=[];vals=[]
 for q in questions:
  claims=collect_claims([a,b]+targets,root,q['dimension']);all_claims.extend(claims);vals.append(validity(q['question'],q['dimension'],claims))
 for u,v in zip(unknown,vals):
  if v['answers_question']:resolved.append(u)
 remaining=[u for u in unknown if u not in resolved]
 rounds.append({'round':1,'trigger':'initial investigation','evidence_targets':targets,'questions':questions,'claim_count':len(all_claims),'evidence_validity':vals,'unanswered_after_round':remaining,'next_round_justified':bool(remaining)})
 if remaining:
  second,why=missing_targets(remaining,root,a,b,targets,pool);q2=[{'unknown':u,'question':question_for(u)[1],'dimension':question_for(u)[0]} for u in remaining];vals=[]
  for q in q2:
   claims=collect_claims(second,root,q['dimension']);all_claims.extend(claims);vals.append(validity(q['question'],q['dimension'],claims))
  resolved2=[u for u,v in zip(remaining,vals) if v['answers_question']];resolved+=resolved2;remaining=[u for u in remaining if u not in resolved2]
  rounds.append({'round':2,'trigger':'round 1 was insufficient','trigger_evidence':why,'evidence_targets':second,'questions':q2,'claim_count':len(all_claims),'evidence_validity':vals,'unanswered_after_round':remaining,'next_round_justified':False})
 direct=sum(c['claim_type']=='DIRECT' for c in all_claims);grounded=sum(c['grounded'] for c in all_claims);context=sum(c['claim_type']=='CONTEXTUAL' for c in all_claims);unique=len({(c['source'],c['passage'],c['dimension']) for c in all_claims})
 return {'relationship_id':r.get('relationship_id'),'documents':{'a':a,'b':b},'deciding_factors':factor_map['dimensions'],'known':known,'unknown_before':sorted(set(unknown)),'questions':questions,'investigation_rounds':len(rounds),'investigation_rounds_detail':rounds,'evidence_pool_size':pool,'evidence_targets':targets,'evidence_claims':all_claims,'evidence_updates':[{'type':'evidence_update','effect':'reduced_uncertainty','resolved_unknowns':sorted(set(resolved)),'basis':'claim-level evidence met grounded question validity rule'}] if resolved else [],'unknown_after':sorted(set(remaining)),'second_pass':{'attempted':len(rounds)>1,'causally_justified':len(rounds)>1,'missing_evidence':rounds[1].get('trigger_evidence',[]) if len(rounds)>1 else [],'targets':rounds[1]['evidence_targets'] if len(rounds)>1 else [],'new_targets_distinct_from_round_one':bool(len(rounds)>1 and set(rounds[1]['evidence_targets'])-set(targets))},'evidence_quality_summary':{'direct_claims':direct,'grounded_direct_claims':grounded,'contextual_claims':context,'keyword_only_claims':sum(c['claim_type']=='KEYWORD_ONLY' for c in all_claims),'unique_claims':unique},'stop_reason':'bounded investigation completed; deciding factors recorded; human review remains authoritative','safety':{'self_training':False,'automatic_rule_promotion':False,'automatic_canon_change':False}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');ap.add_argument('--pool-size',type=int,default=DEFAULT_POOL_SIZE);x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out;pool=max(1,min(x.pool_size,MAX_POOL_SIZE));blind=load(out/'CORE_BLIND_TEST.json',{'predictions':[]});cases=[investigate(r,root,pool) for r in blind.get('predictions',[])];before=sum(bool(c['unknown_before']) for c in cases);after=sum(bool(c['unknown_after']) for c in cases);updates=sum(bool(c['evidence_updates']) for c in cases);answered=sum(sum(1 for v in rnd['evidence_validity'] if v['answers_question']) for c in cases for rnd in c['investigation_rounds_detail']);direct=sum(c['evidence_quality_summary']['direct_claims'] for c in cases);grounded=sum(c['evidence_quality_summary']['grounded_direct_claims'] for c in cases);context=sum(c['evidence_quality_summary']['contextual_claims'] for c in cases);unique=sum(c['evidence_quality_summary']['unique_claims'] for c in cases);second=sum(c['second_pass']['attempted'] for c in cases);causal=sum(c['second_pass']['causally_justified'] for c in cases);distinct=sum(c['second_pass']['new_targets_distinct_from_round_one'] for c in cases);report={'engine':'CORE A.C.E. Detective','schema_version':'2.1','mode':'READ_ONLY','purpose':'bounded investigation using deciding factors, configurable evidence neighborhoods, grounded claim candidates, question coverage, and auditable second-pass targeting','cases':cases,'summary':{'cases':len(cases),'evidence_pool_size':pool,'with_unknowns_before':before,'with_unknowns_after':after,'unknown_cases_reduced':before-after,'cases_with_evidence_updates':updates,'questions_answered':answered,'direct_claims':direct,'grounded_direct_claims':grounded,'contextual_claims':context,'unique_claims':unique,'cases_requiring_second_pass':second,'causally_justified_second_passes':causal,'distinct_second_pass_targets':distinct,'factor_dimensions':15,'average_rounds':round(sum(c['investigation_rounds'] for c in cases)/len(cases),2) if cases else 0},'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
 out.mkdir(parents=True,exist_ok=True);(out/'CORE_DETECTIVE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(out/'CORE_DETECTIVE_REPORT.md').write_text('# CORE A.C.E. Detective Report\n\nDeciding-factor-aware, grounded evidence investigation.\n\n'+json.dumps(report['summary'],indent=2),encoding='utf-8');print(json.dumps(report['summary'],indent=2))
if __name__=='__main__':main()
