#!/usr/bin/env python3
"""CORE A.C.E. Detective: bounded, evidence-seeking investigation.

Domain-neutral investigation mechanics. It treats its first interpretation as a
hypothesis, identifies missing evidence, searches the repository for relevant
context, reads targeted document excerpts, updates the case, and challenges
remaining hypotheses. It never promotes its own conclusions to canon or rules.
"""
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

def overlap_score(a,b):
 sa=signals(a,read(a,ROOT)); sb=signals(b,read(b,ROOT)); return sum(len(set(sa[k])&set(sb[k])) for k in sa)

def related_candidates(a,b,root):
 paths=files(root); base=signals(a,read(a,root)); terms=set(sum(base.values(),[]))
 scored=[]
 for p in paths:
  if p in {a,b}: continue
  s=signals(p,read(p,root)); score=sum(len(terms & set(sum(s.values(),[]))) for _ in [0])
  # Structural bonus: same regional/function words matter more than raw token count.
  for k in base: score += 2*len(set(base[k])&set(s[k]))
  if score: scored.append((score,p))
 return [p for _,p in sorted(scored,reverse=True)[:3]]

def evidence_for(case,root):
 """Search for small amounts of relevant context rather than dumping all files."""
 a,b=case['documents']['a'],case['documents']['b']; targets=related_candidates(a,b,root); snippets=[]
 focus=['AUTHORITY','LEADERSHIP','HOUSE','VILLAGE','SETTLEMENT','REGIONAL','CONTINENT','FAMILY','BIRTH','SUPPORT','REFERENCE','HISTORICAL']
 for p in [a,b]+targets:
  body=read(p,root)
  hits=[]
  lines=body.splitlines()
  for i,line in enumerate(lines):
   u=line.upper()
   if any(w in u for w in focus):
    lo=max(0,i-1);hi=min(len(lines),i+2);hits.append(' '.join(lines[lo:hi]).strip())
  if hits: snippets.append({'path':p,'excerpts':hits[:4]})
 return targets,snippets

def investigate(r,root):
 a,b=r.get('left',''),r.get('right',''); sa,sb=signals(a,read(a,root)),signals(b,read(b,root)); known=[];unknown=[];assumptions=[]
 for dim in sa:
  common=sorted(set(sa[dim])&set(sb[dim])); diff=sorted(set(sa[dim])^set(sb[dim]))
  if common: known.append(f'{dim}: shared indicators {", ".join(common)}')
  if diff: known.append(f'{dim}: differing indicators {", ".join(diff)}')
 if sa['authority'] or sb['authority']: unknown.append('authority role and organizational level require contextual confirmation')
 if sa['support'] or sb['support']: unknown.append('whether one document explicitly supports the other is not established by indicators alone')
 if sa['historical'] or sb['historical']: unknown.append('temporal precedence/supersession is not established by indicators alone')
 if sa['family'] and sb['family'] and (sa['scope'] or sb['scope']): assumptions.append('shared family vocabulary may indicate a shared subject without implying duplicate content')
 if sa['authority'] and sb['specialist']: assumptions.append('authority and specialist signals may describe overlapping roles rather than separate institutions')
 hypotheses=[];overlap=set(sum(sa.values(),[]))&set(sum(sb.values(),[]))
 if overlap: hypotheses.append({'label':'VARIANT','basis':'shared subject signals with possible scope differences','status':'candidate'})
 if sa['support'] or sb['support']: hypotheses.append({'label':'SUPPORTING','basis':'support/audit/reference indicators present','status':'candidate'})
 if sa['historical'] or sb['historical']: hypotheses.append({'label':'HISTORICAL','basis':'historical/revision indicators present','status':'candidate'})
 if set(sa['authority'])&set(sb['authority']): hypotheses.append({'label':'RELATED','basis':'shared authority/governance signals','status':'candidate'})
 if not hypotheses: hypotheses=[{'label':'REVIEW','basis':'insufficient structural evidence','status':'candidate'}]
 questions=[]
 if unknown: questions=['Which document sections explicitly define the disputed scope, authority, or support relationship?','Is there another document that describes the same people/institution at a different scale?']
 targets,snippets=evidence_for({'documents':{'a':a,'b':b}},root)
 evidence_summary=[]
 for s in snippets:
  evidence_summary.append({'path':s['path'],'relevant_excerpts':s['excerpts'][:3]})
 # Update only by evidence actually found; do not convert absence into a fact.
 remaining=list(unknown)
 if any('authority' in e.lower() for e in sum((x['excerpts'] for x in snippets),[])): remaining=[u for u in remaining if 'authority role' not in u]
 challenge=[f'What evidence would falsify {h["label"]}?' for h in hypotheses]
 return {'relationship_id':r.get('relationship_id'),'documents':{'a':a,'b':b},'known':known,'unknown_before':sorted(set(unknown)),'assumptions':sorted(set(assumptions)),'questions':questions,'evidence_targets':targets,'evidence_found':evidence_summary,'unknown_after':sorted(set(remaining)),'hypotheses':hypotheses,'challenge_questions':challenge,'investigation_rounds':2,'stop_reason':'targeted repository evidence pass; human review remains authoritative','safety':{'self_training':False,'automatic_rule_promotion':False,'automatic_canon_change':False}}

def main():
 global ROOT
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();ROOT=Path(x.root).resolve();out=ROOT/x.out;blind=load(out/'CORE_BLIND_TEST.json',{'predictions':[]});cases=[investigate(r,ROOT) for r in blind.get('predictions',[])]
 report={'engine':'CORE A.C.E. Detective','schema_version':'1.1','mode':'READ_ONLY','purpose':'bounded evidence-seeking investigation before relationship classification','cases':cases,'summary':{'cases':len(cases),'with_unknowns_before':sum(bool(c['unknown_before']) for c in cases),'with_unknowns_after':sum(bool(c['unknown_after']) for c in cases),'cases_with_evidence':sum(bool(c['evidence_found']) for c in cases),'cases_with_targets':sum(bool(c['evidence_targets']) for c in cases),'average_rounds':2},'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
 (out/'CORE_DETECTIVE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(out/'CORE_DETECTIVE_REPORT.md').write_text('# CORE A.C.E. Detective Report\n\nEvidence-seeking investigation trace: knowns, unknowns, hypotheses, repository targets, retrieved excerpts, and challenge questions.\n\n'+f"Cases: **{len(cases)}**\nCases with unknowns before investigation: **{report['summary']['with_unknowns_before']}**\nCases with unknowns after investigation: **{report['summary']['with_unknowns_after']}**\nCases with evidence retrieved: **{report['summary']['cases_with_evidence']}**\nCases with evidence targets: **{report['summary']['cases_with_targets']}**\n",encoding='utf-8');print(f"Detective: {len(cases)} cases; evidence retrieved for {report['summary']['cases_with_evidence']}; unknowns after investigation {report['summary']['with_unknowns_after']}.")
if __name__=='__main__':main()
