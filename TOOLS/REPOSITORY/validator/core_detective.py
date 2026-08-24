#!/usr/bin/env python3
"""CORE A.C.E. Detective: read-only investigative reasoning trace.

This is deliberately domain-neutral. It does not promote rules or alter canon.
It turns observed document signals into explicit knowledge/unknowns/assumptions,
competing hypotheses, questions, evidence targets, and a bounded investigation
loop. Domain-specific vocabulary belongs in profiles; this module only reasons
about the structure of uncertainty.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

LABELS=['DUPLICATE','VARIANT','SUPPORTING','HISTORICAL','COINCIDENTAL','MISPLACED','CONFLICT','RELATED','REVIEW']

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def read(path,root):
 p=root/path if path else None
 try:return p.read_text(encoding='utf-8')[:60000] if p and p.exists() else ''
 except:return ''

def signals(path,body):
 s=((path or '')+'\n'+body).upper()
 groups={
  'scope':['CONTINENT','CONTINENTAL','HEARTH-WIDE','REGIONAL','REGION','MOUNTAIN','RIVER','WETLAND','PLAINS','DESERT','COAST','SETTLEMENT','VILLAGE','LOCAL','NARROW'],
  'population':['PEOPLE','PEOPLES','LINEAGE','FAMILY','CLAN','HOUSE','HOUSEHOLD'],
  'family':['FAMILY','BIRTH','CHILDHOOD','MARRIAGE','KIN','HOUSEHOLD'],
  'authority':['GOVERNANCE','AUTHORITY','LEADERSHIP','COUNCIL','LEADER','HEAD','HOUSE'],
  'specialist':['SPECIALIST','LINEAGE','HOUSE','CRAFT','KEEPER'],
  'support':['CHECKLIST','AUDIT','REFERENCE','FRAMEWORK','GUIDE'],
  'historical':['HISTORICAL','ARCHIVE','REVISION','FORMER','OBSOLETE']}
 return {k:sorted({w for w in ws if re.search(r'\b'+re.escape(w)+r'\b',s)}) for k,ws in groups.items()}

def extract_pair(r,root):
 a,b=r.get('left',''),r.get('right',''); sa,sb=signals(a,read(a,root)),signals(b,read(b,root));return a,b,sa,sb

def investigate(r,root):
 a,b,sa,sb=extract_pair(r,root)
 known=[];unknown=[];assumptions=[];questions=[]
 for dim in sa:
  common=sorted(set(sa[dim])&set(sb[dim])); diff=sorted(set(sa[dim])^set(sb[dim]))
  if common: known.append(f'{dim}: shared indicators {", ".join(common)}')
  if diff: known.append(f'{dim}: differing indicators {", ".join(diff)}')
 if sa['scope'] and sb['scope'] and not set(sa['scope'])&set(sb['scope']): unknown.append('exact scope relationship is unresolved')
 if sa['population'] and sb['population'] and not set(sa['population'])&set(sb['population']): unknown.append('population overlap is unresolved')
 if sa['authority'] or sb['authority']: unknown.append('authority role and organizational level require contextual confirmation')
 if sa['support'] or sb['support']: unknown.append('whether one document explicitly supports the other is not established by indicators alone')
 if sa['historical'] or sb['historical']: unknown.append('temporal precedence/supersession is not established by indicators alone')
 if sa['family'] and sb['family'] and (sa['scope'] or sb['scope']): assumptions.append('shared family vocabulary may indicate a shared subject without implying duplicate content')
 if sa['authority'] and sb['specialist']: assumptions.append('authority and specialist signals may describe overlapping roles rather than separate institutions')
 if unknown: questions.extend(['What additional document context would resolve the scope/population/role ambiguity?','Do either document explicitly define the relationship or authority described?'])
 hypotheses=[]
 overlap=set(sum(sa.values(),[]))&set(sum(sb.values(),[]))
 if overlap: hypotheses.append({'label':'VARIANT','basis':'shared subject signals with possible scope differences','status':'candidate'})
 if sa['support'] or sb['support']: hypotheses.append({'label':'SUPPORTING','basis':'support/audit/reference indicators present','status':'candidate'})
 if sa['historical'] or sb['historical']: hypotheses.append({'label':'HISTORICAL','basis':'historical/revision indicators present','status':'candidate'})
 if set(sa['authority'])&set(sb['authority']): hypotheses.append({'label':'RELATED','basis':'shared authority/governance signals','status':'candidate'})
 if not hypotheses: hypotheses=[{'label':'REVIEW','basis':'insufficient structural evidence','status':'candidate'}]
 # bounded loop: second pass is a challenge, not self-confirmation.
 challenge=[]
 for h in hypotheses: challenge.append(f'What evidence would falsify {h["label"]}?')
 return {'relationship_id':r.get('relationship_id'),'documents':{'a':a,'b':b},'known':known,'unknown':sorted(set(unknown)),'assumptions':sorted(set(assumptions)),'questions':sorted(set(questions)),'hypotheses':hypotheses,'challenge_questions':challenge,'investigation_rounds':2,'stop_reason':'bounded evidence pass; human review remains authoritative','safety':{'self_training':False,'automatic_rule_promotion':False,'automatic_canon_change':False}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
 blind=load(out/'CORE_BLIND_TEST.json',{'predictions':[]});cases=[investigate(r,root) for r in blind.get('predictions',[])]
 report={'engine':'CORE A.C.E. Detective','schema_version':'1.0','mode':'READ_ONLY','purpose':'bounded contextual investigation before relationship classification','cases':cases,'summary':{'cases':len(cases),'with_unknowns':sum(bool(c['unknown']) for c in cases),'with_hypotheses':sum(bool(c['hypotheses']) for c in cases),'with_questions':sum(bool(c['questions']) for c in cases),'average_rounds':2},'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
 (out/'CORE_DETECTIVE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(out/'CORE_DETECTIVE_REPORT.md').write_text('# CORE A.C.E. Detective Report\n\nBounded investigation trace: knowns, unknowns, assumptions, hypotheses, questions, and challenge questions.\n\n'+f"Cases: **{len(cases)}**\nCases with unknowns: **{report['summary']['with_unknowns']}**\nCases with hypotheses: **{report['summary']['with_hypotheses']}**\nCases generating questions: **{report['summary']['with_questions']}**\n",encoding='utf-8');print(f'Detective: {len(cases)} cases; {report["summary"]["with_questions"]} generated questions.')
if __name__=='__main__':main()
