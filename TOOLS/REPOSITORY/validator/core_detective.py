#!/usr/bin/env python3
"""CORE A.C.E. Detective: bounded case investigation with Mythroot deciding factors."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from core_foundations import factor_snapshot
from core_deciding_factor_questions import QUESTIONS
from mythroot_profile import profile_snapshot, RELATIONSHIP_GATES
DEFAULT_POOL_SIZE=10
MAX_POOL_SIZE=20
FOCUS={'authority':['AUTHORITY','LEADERSHIP','GOVERNANCE','COUNCIL','LEADER','HEAD','HOUSE'],'scope':['CONTINENT','CONTINENTAL','HEARTH-WIDE','REGIONAL','REGION','MOUNTAIN','RIVER','PLAINS','SETTLEMENT','VILLAGE','LOCAL'],'support':['SUPPORT','INFORMS','REFERENCES','DERIVED FROM','BASED ON','BUILDS ON','CHECKLIST','AUDIT','REFERENCE'],'temporal':['REVISED','SUPERSEDES','REPLACED','PREVIOUS','FORMER','EARLIER','CURRENT','OLDER','REVISION','HISTORICAL'],'family':['FAMILY','BIRTH','CHILDHOOD','MARRIAGE','KIN','HOUSEHOLD'],'specialist':['SPECIALIST','LINEAGE','HOUSE','CRAFT','KEEPER']}
CASE_QUESTIONS={
 'subject':'Are these artifacts describing the same underlying subject, or merely related subjects?',
 'scope':'Do these artifacts apply to the same geographic, social, organizational, or conceptual scope?',
 'function':'Do the artifacts perform the same informational function, or do they serve different purposes?',
 'role':'Do the artifacts have the same document/artifact role, or is one source, supporting, derived, historical, audit, or tool material?',
 'temporal':'Do the artifacts describe the same temporal state, or is one earlier, revised, superseded, or historical?',
 'relationship':'What relationship is actually supported between these two artifacts: variant, duplicate, supporting, historical, misplaced, conflict, related, or coincidental?',
 'provenance':'What evidence establishes where each claim came from and whether either artifact derives from or has precedence over the other?',
 'dependency':'Does either artifact explicitly depend on, derive from, reference, or inform the other?',
 'consequence':'Would treating these artifacts as equivalent create a materially different downstream world or repository result?',
 'intentionality':'Could an apparent difference be intentional scope, development state, or creator choice rather than an inconsistency?',
}
RELATION_TERMS=('SAME','VARIANT','DUPLICATE','DERIVED','SUPPORT','SUPPORTING','REFERENCE','REFERENCES','BASED ON','BUILDS ON','SUPERSEDES','REPLACES','CONFLICT','DIFFERENT','SEPARATE','REGIONAL','REGION','HISTORICAL','PREVIOUS','CURRENT')

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
  t=terms(read(p,root));score=sum(2*len((set(ta[k])|set(tb[k]))&set(t[k])) for k in FOCUS)
  if score:rows.append((score,p))
 return [p for _,p in sorted(rows,key=lambda x:(x[0],x[1]),reverse=True)[:max(1,min(pool,MAX_POOL_SIZE))]]

def question_for_unknown(text):
 l=text.lower()
 for key in ('authority','support','temporal'):
  if key in l:return key,CASE_QUESTIONS[key]
 return 'relationship',CASE_QUESTIONS['relationship']

def passages(path,root,dimension):
 lines=read(path,root).splitlines();words=FOCUS.get(dimension,[]);out=[];seen=set()
 for i,line in enumerate(lines):
  if any(w in line.upper() for w in words):
   text=' '.join(lines[max(0,i-1):min(len(lines),i+2)]).strip();key=re.sub(r'\s+',' ',text).lower()
   if key not in seen:seen.add(key);out.append(text)
 return out[:6]

def stem_tokens(path):
 return {x for x in re.split(r'[^a-z0-9]+',Path(path).stem.lower()) if len(x)>=4 and x not in {'family','regional','document','draft','final','version','comparative'}}

def pair_anchors(a,b):
 aa,bb=stem_tokens(a),stem_tokens(b);common=aa&bb
 return common or ((aa|bb)-{'hearth','region','regions'})

def claim_from(path,text,dimension,pair_anchors=()):
 u=text.upper();patterns={'authority':r'(?:(?:AUTHORITY|LEADER|LEADERSHIP|GOVERNANCE|COUNCIL|HEAD).{0,140}(?:VILLAGE|SETTLEMENT|REGION|REGIONAL|CONTINENT|CONTINENTAL)|(?:VILLAGE|SETTLEMENT|REGION|REGIONAL|CONTINENT|CONTINENTAL).{0,140}(?:AUTHORITY|LEADER|LEADERSHIP|GOVERNANCE|COUNCIL|HEAD))','support':r'(?:SUPPORT|INFORMS|REFERENCES|DERIVED FROM|BASED ON|BUILDS ON).{0,160}(?:DOCUMENT|GUIDE|FRAMEWORK|CHECKLIST|CANON|SOURCE)','temporal':r'(?:REVISED|SUPERSEDES|REPLACED|PREVIOUS|FORMER|EARLIER|CURRENT|OLDER|REVISION).{0,160}(?:VERSION|DOCUMENT|CANON|SOURCE|TEXT)?','relationship':r'(?:SAME|VARIANT|DUPLICATE|DERIVED|SUPPORT|SUPPORTING|REFERENCE|REFERENCES|BASED ON|BUILDS ON|SUPERSEDES|REPLACES|CONFLICT|DIFFERENT|SEPARATE|REGIONAL|HISTORICAL|PREVIOUS|CURRENT).{0,180}'}
 direct=bool(re.search(patterns.get(dimension,patterns['relationship']),u,re.S));contextual=bool(any(w in u for w in FOCUS.get(dimension,[]))) or bool(any(w in u for w in RELATION_TERMS))
 anchors={x for x in pair_anchors if x.upper() in u};pair_relevant=bool(anchors) or (dimension=='relationship' and direct)
 entities=extract_entities(text);grounded=direct and pair_relevant and (len(entities)>=1 or dimension=='relationship')
 if grounded:quality='DIRECT';score=1.0;reason='question_specific_and_pair_relevant'
 elif direct or contextual:quality='CONTEXTUAL';score=.5;reason='dimension_signal_but_not_pair_resolving'
 else:quality='KEYWORD_ONLY';score=.1;reason='weak_signal'
 up=path.upper();source='primary'
 if any(x in up for x in ['CHECKLIST','AUDIT','FRAMEWORK','GUIDE','OPERATING_RULES']):source='supporting'
 if any(x in up for x in ['ARCHIVE','HISTORICAL','REVISION']):source='historical'
 return {'source':path,'passage':text,'dimension':dimension,'claim':text,'claim_type':quality,'quality_score':score,'reason':reason,'source_role':source,'entities':entities,'grounded':grounded,'pair_relevant':pair_relevant,'pair_anchors':sorted(anchors)}

def extract_entities(text):
 vals=[]
 for m in re.finditer(r'\b(?:the\s+)?([A-Z][A-Za-z0-9_-]{2,}(?:\s+[A-Z][A-Za-z0-9_-]{2,}){0,4})\b',text):
  v=m.group(1).strip(' .,;:()[]')
  if v.upper() not in {'THE','THIS','THAT','WHICH','DOCUMENT','SOURCE','CURRENT','FORMER'} and v not in vals: vals.append(v)
 return vals[:12]

def collect_claims(paths,root,dimension,pair_anchors=()):
 claims=[];seen=set()
 for p in paths:
  for text in passages(p,root,dimension):
   c=claim_from(p,text,dimension,pair_anchors);key=(c['source'],re.sub(r'\s+',' ',text).strip().lower(),dimension)
   if key not in seen:seen.add(key);claims.append(c)
 return claims

def validity(question,dimension,claims):
 relevant=[c for c in claims if c['dimension']==dimension];direct=[c for c in relevant if c['claim_type']=='DIRECT'];grounded=[c for c in direct if c['grounded']];context=[c for c in relevant if c['claim_type']=='CONTEXTUAL'];sources={c['source'] for c in context}
 answered=bool(grounded);quality=1.0 if grounded else (.5 if context else 0.0)
 return {'question':question,'dimension':dimension,'answerability':quality,'answers_question':answered,'direct_claims':len(direct),'grounded_direct_claims':len(grounded),'contextual_claims':len(context),'independent_context_sources':len(sources),'pair_resolving_claims':len([c for c in relevant if c.get('pair_relevant')]),'evidence_quality':relevant}

def missing_targets(remaining,root,a,b,used,pool,pair_anchors):
 targets=[];reasons=[];used=set(used)|{a,b}
 for u in remaining:
  dim,_=question_for_unknown(u);rows=[]
  for p in files(root):
   if p in used:continue
   text=read(p,root);score=len(terms(text).get(dim,[]))*2 + sum(1 for x in pair_anchors if x.upper() in text.upper())
   if score:rows.append((score,p))
  for _,p in sorted(rows,key=lambda x:(x[0],x[1]),reverse=True)[:pool]:
   if p not in targets:targets.append(p);reasons.append({'missing':u,'dimension':dim,'target':p,'reason':'first pass lacked pair-resolving evidence'})
 return targets[:pool],reasons

def principle_checks(factor_map):
 dimensions=factor_map['dimensions'];checks={}
 for label,gates in RELATIONSHIP_GATES.items():checks[label]={'gate_factors':list(gates),'same_subject_signal':bool(dimensions['subject']['shared']),'scope_signal':bool(dimensions['scope']['different'] or dimensions['scope']['shared']),'functional_continuity_signal':bool(dimensions['function']['shared']),'status':'candidate_only','reason':'Deciding factors explain a relationship; lexical overlap alone cannot promote a gate.'}
 return checks

def investigate(r,root,pool=DEFAULT_POOL_SIZE):
 a,b=r.get('left',''),r.get('right','');ta,tb=terms(read(a,root)),terms(read(b,root));factor_map=factor_snapshot(read(a,root),read(b,root));profile=profile_snapshot();anchors=pair_anchors(a,b);unknown=[];known=[]
 for d in FOCUS:
  common=set(ta[d])&set(tb[d]);diff=set(ta[d])^set(tb[d])
  if common:known.append(f'{d}: shared {", ".join(sorted(common))}')
  if diff:known.append(f'{d}: differs {", ".join(sorted(diff))}')
 # A case is not solved merely because a keyword has a supporting sentence.
 # Ask the relationship-level questions explicitly, then add specialist questions
 # only when the evidence shows that dimension is actually relevant.
 unknown.extend(['relationship between the two artifacts requires explicit case evidence'])
 if ta['authority'] or tb['authority']:unknown.append('authority role and organizational level require contextual confirmation')
 if ta['support'] or tb['support']:unknown.append('explicit support relationship is not established by indicators alone')
 if ta['temporal'] or tb['temporal']:unknown.append('temporal precedence/supersession is not established by indicators alone')
 if factor_map['dimensions']['scope']['different'] or factor_map['dimensions']['scope']['shared']:unknown.append('scope relationship requires explicit case evidence')
 if factor_map['dimensions']['function']['different'] or factor_map['dimensions']['function']['shared']:unknown.append('functional relationship requires explicit case evidence')
 questions=[{'unknown':u,'question':question_for_unknown(u)[1],'dimension':question_for_unknown(u)[0]} for u in sorted(set(unknown))];targets=candidates(a,b,root,pool=pool);rounds=[];all_claims=[];resolved=[];vals=[]
 for q in questions:
  claims=collect_claims([a,b]+targets,root,q['dimension'],anchors);all_claims.extend(claims);vals.append(validity(q['question'],q['dimension'],claims))
 for u,v in zip([q['unknown'] for q in questions],vals):
  if v['answers_question']:resolved.append(u)
 remaining=[u for u in [q['unknown'] for q in questions] if u not in resolved]
 rounds.append({'round':1,'trigger':'initial case investigation','evidence_targets':targets,'questions':questions,'claim_count':len(all_claims),'evidence_validity':vals,'unanswered_after_round':remaining,'next_round_justified':bool(remaining)})
 if remaining:
  second,why=missing_targets(remaining,root,a,b,targets,pool,anchors);q2=[{'unknown':u,'question':question_for_unknown(u)[1],'dimension':question_for_unknown(u)[0]} for u in remaining];vals=[]
  for q in q2:
   claims=collect_claims(second,root,q['dimension'],anchors);all_claims.extend(claims);vals.append(validity(q['question'],q['dimension'],claims))
  resolved2=[u for u,v in zip(remaining,vals) if v['answers_question']];resolved+=resolved2;remaining=[u for u in remaining if u not in resolved2]
  rounds.append({'round':2,'trigger':'round 1 lacked pair-resolving evidence','trigger_evidence':why,'evidence_targets':second,'questions':q2,'claim_count':len(all_claims),'evidence_validity':vals,'unanswered_after_round':remaining,'next_round_justified':False})
 direct=sum(c['claim_type']=='DIRECT' for c in all_claims);grounded=sum(c['grounded'] for c in all_claims);context=sum(c['claim_type']=='CONTEXTUAL' for c in all_claims);pair_claims=sum(c.get('pair_relevant',False) for c in all_claims);unique=len({(c['source'],c['passage'],c['dimension']) for c in all_claims})
 return {'relationship_id':r.get('relationship_id'),'documents':{'a':a,'b':b},'domain_profile':profile['name'],'domain_profile_version':profile['version'],'mythroot_principles':profile['principles'],'deciding_factors':factor_map['dimensions'],'principle_checks':principle_checks(factor_map),'case_anchors':sorted(anchors),'known':known,'unknown_before':sorted(set(unknown)),'questions':questions,'investigation_rounds':len(rounds),'investigation_rounds_detail':rounds,'evidence_pool_size':pool,'evidence_targets':targets,'evidence_claims':all_claims,'evidence_updates':[{'type':'evidence_update','effect':'reduced_uncertainty','resolved_unknowns':sorted(set(resolved)),'basis':'pair-resolving evidence'}] if resolved else [],'unknown_after':sorted(set(remaining)),'second_pass':{'attempted':len(rounds)>1,'causally_justified':len(rounds)>1,'missing_evidence':rounds[1].get('trigger_evidence',[]) if len(rounds)>1 else [],'targets':rounds[1]['evidence_targets'] if len(rounds)>1 else [],'new_targets_distinct_from_round_one':bool(len(rounds)>1 and set(rounds[1]['evidence_targets'])-set(targets))},'evidence_quality_summary':{'direct_claims':direct,'grounded_direct_claims':grounded,'pair_resolving_claims':pair_claims,'contextual_claims':context,'keyword_only_claims':sum(c['claim_type']=='KEYWORD_ONLY' for c in all_claims),'unique_claims':unique},'stop_reason':'bounded case investigation completed; unresolved relationship questions remain explicit; human review remains authoritative','safety':{'self_training':False,'automatic_rule_promotion':False,'automatic_canon_change':False}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');ap.add_argument('--pool-size',type=int,default=DEFAULT_POOL_SIZE);x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out;pool=max(1,min(x.pool_size,MAX_POOL_SIZE));blind=load(out/'CORE_BLIND_TEST.json',{'predictions':[]});cases=[investigate(r,root,pool) for r in blind.get('predictions',[])];before=sum(bool(c['unknown_before']) for c in cases);after=sum(bool(c['unknown_after']) for c in cases);updates=sum(bool(c['evidence_updates']) for c in cases);answered=sum(sum(1 for v in rnd['evidence_validity'] if v['answers_question']) for c in cases for rnd in c['investigation_rounds_detail']);direct=sum(c['evidence_quality_summary']['direct_claims'] for c in cases);grounded=sum(c['evidence_quality_summary']['grounded_direct_claims'] for c in cases);pair=sum(c['evidence_quality_summary']['pair_resolving_claims'] for c in cases);context=sum(c['evidence_quality_summary']['contextual_claims'] for c in cases);unique=sum(c['evidence_quality_summary']['unique_claims'] for c in cases);second=sum(c['second_pass']['attempted'] for c in cases);causal=sum(c['second_pass']['causally_justified'] for c in cases);distinct=sum(c['second_pass']['new_targets_distinct_from_round_one'] for c in cases);report={'engine':'CORE A.C.E. Detective','schema_version':'2.5','mode':'READ_ONLY','domain_profile':'Mythroot Worldbuilding','purpose':'solve relationships by investigating deciding factors with pair-resolving evidence rather than merely finding grounded statements','cases':cases,'summary':{'cases':len(cases),'evidence_pool_size':pool,'with_case_questions_before':before,'with_case_questions_after':after,'case_questions_reduced':before-after,'cases_with_evidence_updates':updates,'questions_answered':answered,'direct_claims':direct,'grounded_direct_claims':grounded,'pair_resolving_claims':pair,'contextual_claims':context,'unique_claims':unique,'cases_requiring_second_pass':second,'causally_justified_second_passes':causal,'distinct_second_pass_targets':distinct,'factor_dimensions':15,'average_rounds':round(sum(c['investigation_rounds'] for c in cases)/len(cases),2) if cases else 0},'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
 out.mkdir(parents=True,exist_ok=True);(out/'CORE_DETECTIVE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(out/'CORE_DETECTIVE_REPORT.md').write_text('# CORE A.C.E. Detective Report\n\nMythroot deciding-factor-aware case investigation with pair-resolving evidence.\n\n'+json.dumps(report['summary'],indent=2),encoding='utf-8');print(json.dumps(report['summary'],indent=2))
if __name__=='__main__':main()
