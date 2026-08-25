#!/usr/bin/env python3
"""Canonical-grounded context for CORE relationship classification.

The engine answers the question before the relationship question: what is
already canonically known about the subject/context represented by a document?
It is read-only and evidence-producing; it never changes canon.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
EXCLUDED={'07_ARCHIVE','08_RELEASES','REPORTS','TOOLS','.GIT'}
CANONICAL_HINTS=('WORLD_BIBLE','FOUNDATION','CANON','CORE','CULTURES','CONTINENTS','REGIONS','PEOPLES')
def read(root,p,limit=30000):
 try:return (root/p).read_text(encoding='utf-8',errors='replace')[:limit]
 except:return ''
def tokens(p):
 return {x for x in re.split(r'[^a-z0-9]+',Path(p).stem.lower()) if len(x)>=4 and x not in {'family','document','regional','comparative','draft','final','version','hearth'}}
def eligible(p):
 u=p.upper().replace('\\','/')
 return not any('/'+x+'/' in '/'+u+'/' or u.startswith(x+'/') for x in EXCLUDED)
def canonical_score(path,subject_tokens):
 u=path.upper(); score=sum(3 for h in CANONICAL_HINTS if h in u); score+=5*len(tokens(path)&subject_tokens)
 if '/03_PEOPLES/CULTURES/' in u: score+=4
 if '/01_WORLD/' in u: score+=4
 return score
def extract_claims(text,subject_tokens,limit=12):
 lines=[re.sub(r'\s+',' ',x).strip() for x in text.splitlines() if x.strip()]
 out=[];seen=set()
 for line in lines:
  low=line.lower()
  if any(t in low for t in subject_tokens) or any(k in low for k in ('canonical','culture','region','coast','river','desert','plains','mountains','wetlands')):
   if line not in seen:
    seen.add(line);out.append(line[:500])
 return out[:limit]
def build_context(path,root,all_paths=None):
 subject=tokens(path); paths=all_paths or [str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*.md') if '.git' not in p.parts and 'REPORTS' not in p.parts]
 scored=sorted(((canonical_score(p,subject),p) for p in paths if eligible(p) and p!=path),reverse=True)
 known=[{'path':p,'score':s,'claims':extract_claims(read(root,p),subject)} for s,p in scored[:8] if s>0]
 own={'path':path,'is_canonical_candidate':canonical_score(path,subject)>=8,'claims':extract_claims(read(root,path),subject)}
 return {'target_document':path,'subject_tokens':sorted(subject),'canonical_knowns':[own]+known,'canonical_question':f'What is canonically known about {Path(path).stem}?','evidence_status':'GROUNDED_IN_REPOSITORY','read_only':True}
def build_for_pair(case,root):
 paths=[str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*.md') if '.git' not in p.parts and 'REPORTS' not in p.parts]
 a,b=case.get('left',''),case.get('right','')
 ca,cb=build_context(a,root,paths),build_context(b,root,paths)
 overlap=set(ca['subject_tokens'])&set(cb['subject_tokens'])
 aclaims='\n'.join(x for k in ca['canonical_knowns'] for x in k['claims']); bclaims='\n'.join(x for k in cb['canonical_knowns'] for x in k['claims'])
 at=read(root,a).lower();bt=read(root,b).lower()
 def relation(claims,text):
  ct=claims.lower(); return {'known_claim_count':len(claims.splitlines()),'claim_overlap':sum(1 for l in claims.splitlines() if l.lower()[:120] in text),'conflict_signals':sum(1 for w in ('not','never','instead','unlike','contrary','supersedes','replaces') if w in text and w in ct)}
 return {'relationship_id':case.get('relationship_id'),'documents':{'a':a,'b':b},'canonical_context':{'a':ca,'b':cb,'shared_subject_tokens':sorted(overlap),'a_against_knowns':relation(aclaims,at),'b_against_knowns':relation(bclaims,bt),'canonical_grounding':'Each document is evaluated against repository-known subject/context evidence before relationship classification.'}}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
 q=json.loads((out/'CORE_ADJUDICATION_QUEUE.json').read_text()) if (out/'CORE_ADJUDICATION_QUEUE.json').exists() else {'queue':[]}
 cases=[build_for_pair(c,root) for c in q.get('queue',[])]
 payload={'engine':'CORE A.C.E. Canonical Context','schema_version':'1.0','mode':'READ_ONLY','purpose':'ground document relationship decisions in canonical repository knowns before pair classification','cases':cases,'summary':{'cases':len(cases),'canonical_grounded_cases':len(cases)},'safety':{'automatic_canon_change':False,'automatic_rule_promotion':False}}
 (out/'CORE_CANONICAL_CONTEXT.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_CANONICAL_CONTEXT.md').write_text('# CORE Canonical Context\n\n'+json.dumps(payload['summary'],indent=2),encoding='utf-8');print(json.dumps(payload['summary'],indent=2))
if __name__=='__main__':main()
