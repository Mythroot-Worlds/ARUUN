#!/usr/bin/env python3
"""CORE A.C.E. Detective: evidence-seeking investigation with hypothesis updates."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
LABELS={'DUPLICATE','VARIANT','SUPPORTING','HISTORICAL','COINCIDENTAL','MISPLACED','CONFLICT','RELATED','REVIEW'}

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

def related_candidates(a,b,root):
 base=signals(a,read(a,root)); terms=set(sum(base.values(),[])); scored=[]
 for p in files(root):
  if p in {a,b}: continue
  s=signals(p,read(p,root)); score=2*sum(len(set(base[k])&set(s[k])) for k in base)
  if score: scored.append((score,p))
 return [p for _,p in sorted(scored,reverse=True)[:3]]

def evidence_for(a,b,root):
 targets=related_candidates(a,b,root); snippets=[]; focus=['AUTHORITY','LEADERSHIP','HOUSE','VILLAGE','SETTLEMENT','REGIONAL','CONTINENT','FAMILY','BIRTH','SUPPORT','REFERENCE','HISTORICAL']
 for p in [a,b]+targets:
  lines=read(p,root).splitlines();hits=[]
  for i,line in enumerate(lines):
   if any(w in line.upper() for w in focus): hits.append(' '.join(lines[max(0,i-1):min(len(lines),i+2)]).strip())
  if hits: snippets.append({'path':p,'excerpts':hits[:4]})
 return targets,snippets

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
 targets,snippets=evidence_for(a,b,root)
 # Interpret retrieved evidence: explicit contextual words can resolve a missing dimension; absence never resolves it.
 evidence_text=' '.join(x for s in snippets for x in s['excerpts']).upper()
 resolved=[]
 if 'VILLAGE' in evidence_text or 'SETTLEMENT' in evidence_text:
  if any('authority role' in u for u in unknown): resolved.append('authority/organizational context gained from settlement-level evidence')
 if 'CHECKLIST' in evidence_text or 'REFERENCE' in evidence_text:
  if any('support' in u for u in unknown): resolved.append('supporting-document context found')
 remaining=[u for u in unknown if not any(k in u for k in ('authority role','explicit support')) or not resolved]
 updates=[]
 if resolved: updates.append({'type':'evidence_update','effect':'reduced uncertainty','basis':resolved})
 for h in hypotheses:
  h['post_evidence_status']='supported_candidate' if overlap else h['status']
 challenge=[f'What evidence would falsify {h["label"]}?' for h in hypotheses]
 return {'relationship_id':r.get('relationship_id'),'documents':{'a':a,'b':b},'known':known,'unknown_before':sorted(set(unknown)),'assumptions':sorted(set(assumptions)),'questions':questions,'evidence_targets':targets,'evidence_found':snippets,'evidence_updates':updates,'unknown_after':sorted(set(remaining)),'hypotheses':hypotheses,'challenge_questions':challenge,'investigation_rounds':2,'stop_reason':'targeted evidence pass completed; human review remains authoritative','safety':{'self_training':False,'automatic_rule_promotion':False,'automatic_canon_change':False}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out;blind=load(out/'CORE_BLIND_TEST.json',{'predictions':[]});cases=[investigate(r,root) for r in blind.get('predictions',[])]
 before=sum(bool(c['unknown_before']) for c in cases);after=sum(bool(c['unknown_after']) for c in cases);updates=sum(bool(c['evidence_updates']) for c in cases)
 report={'engine':'CORE A.C.E. Detective','schema_version':'1.2','mode':'READ_ONLY','purpose':'bounded evidence-seeking investigation with post-evidence hypothesis/uncertainty updates','cases':cases,'summary':{'cases':len(cases),'with_unknowns_before':before,'with_unknowns_after':after,'cases_with_evidence':sum(bool(c['evidence_found']) for c in cases),'cases_with_updates':updates,'unknown_cases_reduced':before-after,'average_rounds':2},'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
 (out/'CORE_DETECTIVE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(out/'CORE_DETECTIVE_REPORT.md').write_text('# CORE A.C.E. Detective Report\n\nEvidence-seeking investigation with explicit post-evidence updates.\n\n'+f"Cases: **{len(cases)}**\nUnknown cases before: **{before}**\nUnknown cases after: **{after}**\nCases with evidence: **{report['summary']['cases_with_evidence']}**\nCases with evidence updates: **{updates}**\nUnknown cases reduced: **{before-after}**\n",encoding='utf-8');print(f'Detective: {len(cases)} cases; {updates} evidence updates; unknown cases reduced {before-after}.')
if __name__=='__main__':main()
