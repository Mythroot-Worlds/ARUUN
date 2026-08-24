#!/usr/bin/env python3
"""CORE Oracle: broad-to-narrow association and retrieval intelligence."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from core_blackboard import new_board,add,observation

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def read(p,root):
 try:return (root/p).read_text(encoding='utf-8')[:60000]
 except:return ''

def terms(text):
 return sorted(set(re.findall(r'\b[A-Za-z][A-Za-z0-9_-]{3,}\b',text.lower())))

def related(a,b):
 A=set(terms(a));B=set(terms(b));return len(A&B)

def case_oracle(case,root):
 docs=case.get('documents',{});a=docs.get('a','');b=docs.get('b','');ta=terms(read(a,root));tb=terms(read(b,root));shared=sorted(set(ta)&set(tb),key=lambda x:(-len(x),x))[:25]
 board=new_board(case.get('relationship_id','unknown'));obs=[]
 for t in shared[:12]:
  o=observation('oracle',t,'shared_concept',t,a,'lexical association across investigation documents',.35,association_type='shared_term');add(board,o);obs.append(o)
 # Build a cheap repository map: files sharing several meaningful terms become candidates.
 candidates=[];files=[p for p in root.rglob('*.md') if '.git' not in p.parts and 'REPORTS' not in p.parts]
 focus=set(shared)
 for p in files:
  rel=str(p.relative_to(root)).replace('\\','/');
  if rel in {a,b}: continue
  score=len(focus & set(terms(read(rel,root))))
  if score>=3:candidates.append((score,rel))
 candidates=sorted(candidates,key=lambda x:(-x[0],x[1]))[:15]
 board['oracle']={'shared_terms':shared,'association_candidates':[{'path':p,'overlap':s} for s,p in candidates],'strategy':'broad lexical map, then narrow by multi-term association'}
 return board

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out;det=load(out/'CORE_DETECTIVE_REPORT.json',{'cases':[]});boards=[case_oracle(c,root) for c in det['cases']];payload={'engine':'CORE A.C.E. Oracle','schema_version':'1.0','mode':'READ_ONLY','purpose':'broad-to-narrow association discovery and context mapping','cases':boards,'summary':{'cases':len(boards),'association_items':sum(len(b['items']) for b in boards),'cases_with_repository_candidates':sum(bool(b['oracle']['association_candidates']) for b in boards)},'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}};out.mkdir(parents=True,exist_ok=True);(out/'CORE_ORACLE_REPORT.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_ORACLE_REPORT.md').write_text('# CORE Oracle Report\n\n'+json.dumps(payload['summary'],indent=2),encoding='utf-8');print(json.dumps(payload['summary'],indent=2))
if __name__=='__main__':main()
