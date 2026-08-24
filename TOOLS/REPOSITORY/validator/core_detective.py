#!/usr/bin/env python3
"""CORE A.C.E. Detective: evidence-seeking investigation with evidence validity and second-pass targeting."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def read(path,root,limit=60000):
 p=root/path if path else None
 try:return p.read_text(encoding='utf-8')[:limit] if p and p.exists() else ''
 except:return ''

def signals(path,body):
 s=((path or '')+'\n'+body).upper(); groups={'scope':['CONTINENT','CONTINENTAL','HEARTH-WIDE','REGIONAL','REGION','MOUNTAIN','RIVER','WETLAND','PLAINS','DESERT','COAST','SETTLEMENT','VILLAGE','LOCAL','NARROW'],'population':['PEOPLE','PEOPLES','LINEAGE','FAMILY','CLAN','HOUSE','HOUSEHOLD'],'family':['FAMILY','BIRTH','CHILDHOOD','MARRIAGE','KIN','HOUSEHOLD'],'authority':['GOVERNANCE','AUTHORITY','LEADERSHIP','COUNCIL','LEADER','HEAD','HOUSE'],'specialist':['SPECIALIST','LINEAGE','HOUSE','CRAFT','KEEPER'],'support':['CHECKLIST','AUDIT','REFERENCE','FRAMEWORK','GUIDE'],'historical':['HISTORICAL','ARCHIVE','REVISION','FORMER','OBSOLETE']}
 return {k:sorted({w for w in ws if re.search(r'\b'+re.escape(w)+r'\b',s)}) for k,ws in groups.items()}

def files(root): return [str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*.md') if '.git' not in p.parts and 'REPORTS' not in p.parts]

def related_candidates(a,b,root,exclude=()):
 base=signals(a,read(a,root));scored=[]
 for p in files(root):
  if p in {a,b,*exclude}: continue
  s=signals(p,read(p,root));score=2*sum(len(set(base[k])&set(s[k])) for k in base)
  if score: scored.append((score,p))
 return [p for _,p in sorted(scored,reverse=True)[:3]]

def evidence_for(a,b,root,extra_targets=()):
 targets=list(extra_targets)+related_candidates(a,b,root,extra_targets);targets=list(dict.fromkeys(targets))[:5];snippets=[];focus=['AUTHORITY','LEADERSHIP','HOUSE','VILLAGE','SETTLEMENT','REGIONAL','CONTINENT','FAMILY','BIRTH','SUPPORT','REFERENCE','HISTORICAL']
 for p in [a,b]+targets:
  lines=read(p,root).splitlines();hits=[]
  for i,line in enumerate(lines):
   if any(w in line.upper() for w in focus): hits.append(' '.join(lines[max(0,i-1):min(len(lines),i+2)]).strip())
  if hits: snippets.append({'path':p,'excerpts':hits[:4]})
 return targets,snippets

def evidence_validity(question,excerpts):
 text=' '.join(excerpts).upper();q=question.lower();checks=[]
 if 'authority' in q: checks=[('explicit_authority',bool(re.search(r'\b(LEAD|LEADER|GOVERN|AUTHORITY|HEAD|COUNCIL)\b',text))),('organizational_scale',bool(re.search(r'\b(VILLAGE|SETTLEMENT|REGION|REGIONAL|CONTINENT|CONTINENTAL)\b',text)))]
 elif 'support' in q: checks=[('explicit_support',bool(re.search(r'\b(SUPPORT|REFERENCE|CHECKLIST|GUIDE|FRAMEWORK|INFORMS|BUILDS ON)\b',text)))]
 elif 'temporal' in q: checks=[('explicit_temporal',bool(re.search(r'\b(THEN|FORMER|PREVIOUS|HISTORICAL|REVISED|SUPERSEDE|OLDER|EARLIER)\b',text)))]
 else: checks=[('contextual_match',bool(text))]
 passed=sum(v for _,v in checks);return {'question':question,'checks':[{'test':k,'passed':v} for k,v in checks],'answerability':round(passed/len(checks),2) if checks else 0.0,'answers_question':bool(checks) and passed==len(checks)}

def missing_targets(unknown,validity,root,a,b,used):
 targets=[]
 for u in unknown:
  q='authority scope evidence' if 'authority' in u else ('support relationship evidence' if 'support' in u else 'historical precedence evidence')
  # Ask for a document whose signals specifically cover the missing dimension and differs from the first-pass targets.
  candidates=[]
  for p in files(root):
   if p in {a,b,*used}: continue
   s=signals(p,read(p,root))
   if ('authority' in u and (s['authority'] or s['scope'])) or ('support' in u and s['support']) or ('temporal' in u and s['historical']): candidates.append(p)
  targets.extend(candidates[:2])
 return list(dict.fromkeys(targets))

def investigate(r,root):
 a,b=r.get('left',''),r.get('right','');sa,sb=signals(a,read(a,root)),signals(b,read(b,root));known=[];unknown=[];assumptions=[]
 for d in sa:
  common=sorted(set(sa[d])&set(sb[d]));diff=sorted(set(sa[d])^set(sb[d]));
  if common: known.append(f'{d}: shared {", ".join(common)}')
  if diff: known.append(f'{d}: differs {", ".join(diff)}')
 if sa['authority'] or sb['authority']: unknown.append('authority role and organizational level require contextual confirmation')
 if sa['support'] or sb['support']: unknown.append('explicit support relationship is not established by indicators alone')
 if sa['historical'] or sb['historical']: unknown.append('temporal precedence/supersession is not established by indicators alone')
 if sa['family'] and sb['family']: assumptions.append('shared family vocabulary may indicate shared subject without implying duplicate content')
 if sa['authority'] and sb['specialist']: assumptions.append('authority and specialist signals may describe overlapping roles')
 hypotheses=[];overlap=set(sum(sa.values(),[]))&set(sum(sb.values(),[]))
 if overlap: hypotheses.append({'label':'VARIANT','basis':'shared subject signals with possible scope differences','status':'candidate'})
 if sa['support'] or sb['support']: hypotheses.append({'label':'SUPPORTING','basis':'support/audit/reference indicators present','status':'candidate'})
 if sa['historical'] or sb['historical']: hypotheses.append({'label':'HISTORICAL','basis':'historical/revision indicators present','status':'candidate'})
 if set(sa['authority'])&set(sb['authority']): hypotheses.append({'label':'RELATED','basis':'shared authority/governance signals','status':'candidate'})
 if not hypotheses: hypotheses=[{'label':'REVIEW','basis':'insufficient structural evidence','status':'candidate'}]
 questions=['Which document sections explicitly define the disputed scope, authority, or support relationship?'] if unknown else []
 used=[];rounds=[];targets,snippets=evidence_for(a,b,root);used.extend(targets);all_excerpts=[x for s in snippets for x in s['excerpts']];validity=[evidence_validity(q,all_excerpts) for q in questions];rounds.append({'round':1,'targets':targets,'evidence_count':len(all_excerpts),'validity':validity})
 resolved=[]
 for u in unknown:
  relevant=[v for v in validity if ('authority' in u and 'authority' in v['question'].lower()) or ('support' in u and 'support' in v['question'].lower()) or ('temporal' in u and 'temporal' in v['question'].lower())]
  if relevant and any(v['answers_question'] for v in relevant): resolved.append(u)
 remaining=[u for u in unknown if u not in resolved]
 second_targets=missing_targets(remaining,validity,root,a,b,used)
 if remaining and second_targets:
  t2,s2=evidence_for(a,b,root,second_targets);used.extend(t2);all2=[x for s in s2 for x in s['excerpts']];v2=[evidence_validity(q,all2) for q in questions];rounds.append({'round':2,'targets':t2,'evidence_count':len(all2),'validity':v2});snippets.extend(s2);validity.extend(v2)
  for u in list(remaining):
   relevant=[v for v in v2 if ('authority' in u and 'authority' in v['question'].lower()) or ('support' in u and 'support' in v['question'].lower()) or ('temporal' in u and 'temporal' in v['question'].lower())]
   if relevant and any(v['answers_question'] for v in relevant): resolved.append(u);remaining.remove(u)
 updates=[{'type':'evidence_update','effect':'reduced_uncertainty','resolved_unknowns':sorted(set(resolved)),'basis':'retrieved evidence passed the question-specific answerability test'}] if resolved else []
 for h in hypotheses: h['post_evidence_status']='supported_candidate' if overlap else h['status']
 return {'relationship_id':r.get('relationship_id'),'documents':{'a':a,'b':b},'known':known,'unknown_before':sorted(set(unknown)),'assumptions':sorted(set(assumptions)),'questions':questions,'investigation_rounds':rounds,'evidence_targets':used,'evidence_found':snippets,'evidence_validity':validity,'evidence_updates':updates,'unknown_after':sorted(set(remaining)),'hypotheses':hypotheses,'challenge_questions':[f'What evidence would falsify {h["label"]}?' for h in hypotheses],'stop_reason':'bounded two-pass investigation; human review remains authoritative','safety':{'self_training':False,'automatic_rule_promotion':False,'automatic_canon_change':False}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out;blind=load(out/'CORE_BLIND_TEST.json',{'predictions':[]});cases=[investigate(r,root) for r in blind.get('predictions',[])]
 before=sum(bool(c['unknown_before']) for c in cases);after=sum(bool(c['unknown_after']) for c in cases);updates=sum(bool(c['evidence_updates']) for c in cases);answered=sum(sum(1 for v in c['evidence_validity'] if v['answers_question']) for c in cases);second=sum(1 for c in cases if len(c['investigation_rounds'])>1)
 report={'engine':'CORE A.C.E. Detective','schema_version':'1.4','mode':'READ_ONLY','purpose':'bounded two-pass evidence-seeking investigation with question-specific validity and missing-evidence targeting','cases':cases,'summary':{'cases':len(cases),'with_unknowns_before':before,'with_unknowns_after':after,'cases_with_evidence':sum(bool(c['evidence_found']) for c in cases),'cases_with_updates':updates,'unknown_cases_reduced':before-after,'questions_fully_answered':answered,'cases_requiring_second_pass':second,'average_rounds':round(sum(len(c['investigation_rounds']) for c in cases)/len(cases),2) if cases else 0},'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
 (out/'CORE_DETECTIVE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(out/'CORE_DETECTIVE_REPORT.md').write_text('# CORE A.C.E. Detective Report\n\nBounded two-pass investigation with question-specific evidence validity and missing-evidence targeting.\n\n'+f"Cases: **{len(cases)}**\nUnknown cases before: **{before}**\nUnknown cases after: **{after}**\nCases with evidence: **{report['summary']['cases_with_evidence']}**\nCases with evidence updates: **{updates}**\nUnknown cases reduced: **{before-after}**\nQuestions fully answered: **{answered}**\nCases requiring second pass: **{second}**\nAverage rounds: **{report['summary']['average_rounds']}**\n",encoding='utf-8');print(f'Detective: {len(cases)} cases; {second} second-pass investigations; unknown cases reduced {before-after}; fully answered {answered}.')
if __name__=='__main__':main()
