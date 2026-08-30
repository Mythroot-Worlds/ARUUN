#!/usr/bin/env python3
"""CORE relationship discovery: conservative, read-only candidate generation.

Discovery proposes candidates; it does not classify relationships. Candidate
signals combine structural document identity, explicit front matter, headings,
and substantive information-unit prose so documents can be connected even when
they use different wording. Lexical overlap remains evidence, not the decision.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from collections import defaultdict
from pathlib import Path
SKIP={'.git','.github','node_modules','__pycache__','TOOLS'}
ARCHIVE='07_ARCHIVE/'; REPORTS='TOOLS/REPOSITORY/REPORTS/'
STOP=set('about after again against all also and are because been being but can could each for from have into its more most not other our over same should some than that their there these they this those through under was were what when where which while with would your'.split())
META_RE=re.compile(r'^([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*$')
HEAD_RE=re.compile(r'^\s{0,3}#{1,6}\s+(.+?)\s*$')
def words(t): return {w for w in re.findall(r'[a-z][a-z0-9_]{3,}',t.lower()) if w not in STOP}
def read(p): return p.read_text(encoding='utf-8',errors='replace')
def stable(a,b): return 'REL-'+hashlib.sha1((a+'|'+b).encode()).hexdigest()[:16]
def match_strength(score):
 if score>=.45:return 5
 if score>=.30:return 4
 if score>=.20:return 3
 if score>=.12:return 2
 return 1
def strength_label(n): return ['Minimal','Weak','Moderate','Strong','Near Certain'][n-1]
def metadata_and_headings(text):
 meta={}; headings=[]; in_front=False
 for i,line in enumerate(text.splitlines()):
  s=line.strip()
  if i==0 and s=='---': in_front=True; continue
  if in_front and s=='---': in_front=False; continue
  if in_front:
   m=META_RE.match(s)
   if m: meta[m.group(1).lower()]=m.group(2).strip().strip('"\'')
  m=HEAD_RE.match(line)
  if m: headings.append(m.group(1).strip())
 return meta,headings
def document_profile(path):
 text=read(path);meta,headings=metadata_and_headings(text)
 identity_terms=words(' '.join([meta.get('world',''),meta.get('domain',''),meta.get('subject','')] + headings))
 return {'identity_terms':identity_terms,'meta':meta,'headings':headings,'content_terms':words(text)}
def pair_score(a,b,min_overlap):
 identity=a['identity_terms'] & b['identity_terms']; content=a['content_terms'] & b['content_terms']
 union=max(1,len(a['content_terms']|b['content_terms']))
 lexical=len(content)/union
 identity_union=max(1,len(a['identity_terms']|b['identity_terms']))
 identity_score=len(identity)/identity_union
 subject_match=bool(a['meta'].get('subject') and b['meta'].get('subject') and words(a['meta']['subject'])==words(b['meta']['subject']))
 domain_match=bool(a['meta'].get('domain') and b['meta'].get('domain') and a['meta']['domain'].lower()==b['meta']['domain'].lower())
 world_match=bool(a['meta'].get('world') and b['meta'].get('world') and a['meta']['world'].lower()==b['meta']['world'].lower())
 # Structural/identity evidence can create a candidate even when prose wording differs.
 # It never classifies the relationship.
 score=max(lexical, identity_score*0.75)
 if subject_match: score=max(score,0.40)
 elif domain_match and world_match: score=max(score,0.22)
 elif world_match and identity_score>=.12: score=max(score,0.16)
 return score,identity,content,{'subject_match':subject_match,'domain_match':domain_match,'world_match':world_match,'lexical_jaccard':round(lexical,4),'identity_overlap':len(identity)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default=REPORTS);ap.add_argument('--scope',action='append',default=None,help='Corpus scope to include; repeat for multiple scopes.');ap.add_argument('--min-overlap',type=int,default=8);a=ap.parse_args();root=Path(a.root).resolve();scopes=a.scope or ['03_PEOPLES/CULTURES/HEARTH'];docs=[]
 seen=set()
 for scope in scopes:
  base=root/scope
  if not base.exists(): continue
  for p in base.rglob('*.md'):
   rel=p.relative_to(root).as_posix()
   if rel in seen or any(x in SKIP for x in p.parts) or rel.startswith(ARCHIVE) or rel.startswith(REPORTS):continue
   seen.add(rel); profile=document_profile(p)
   if profile['content_terms'] or profile['identity_terms']: docs.append((rel,profile))
 candidates=[]
 for i in range(len(docs)):
  for j in range(i+1,len(docs)):
   pa,a_profile=docs[i];pb,b_profile=docs[j];score,identity,content,signals=pair_score(a_profile,b_profile,a.min_overlap)
   if len(content)<a.min_overlap and not (signals['subject_match'] or (signals['domain_match'] and signals['world_match']) or signals['identity_overlap']>=2):continue
   if score<.12:continue
   rid=stable(min(pa,pb),max(pa,pb));strength=match_strength(score)
   candidates.append({'relationship_id':rid,'left':pa,'right':pb,'shared_terms':len(content),'identity_terms':len(identity),'score':round(score,4),'jaccard':signals['lexical_jaccard'],'match_strength':strength,'match_strength_label':strength_label(strength),'signals':signals,'classification':'UNCLASSIFIED','status':'DISCOVERED_UNREVIEWED','review_required':True})
 candidates.sort(key=lambda x:(x['match_strength'],x['score'],x['identity_terms'],x['shared_terms']),reverse=True);queue=candidates[:500]
 out=root/a.out;out.mkdir(parents=True,exist_ok=True)
 data={'engine':'CORE Relationship Discovery','mode':'READ_ONLY','scope':scopes,'documents_analyzed':len(docs),'relationships_discovered':len(candidates),'review_queue_size':len(queue),'relationships':queue,'match_strength_scale':{'5':'Near Certain','4':'Strong','3':'Moderate','2':'Weak','1':'Minimal'},'note':'Candidate strength combines structural identity, front matter, headings, and substantive prose overlap. It does not classify the relationship.','safety':{'automatic_merge':False,'automatic_canon_change':False,'provenance_required':True}}
 (out/'CORE_RELATIONSHIP_DISCOVERY.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 md=['# CORE Relationship Discovery','','**Read-only candidate generation. No relationship is accepted automatically.**','',f"**Scopes:** {', '.join(f'`{s}`' for s in scopes)}",f'**Documents analyzed:** **{len(docs)}**',f'**Relationship candidates discovered:** **{len(candidates)}**',f'**Review queue:** **{len(queue)}**','','## Candidate evidence','Discovery uses structural identity, explicit document metadata, headings, and substantive prose overlap. These signals only establish that two documents deserve comparison.','','## Match strength','**5** Near Certain · **4** Strong · **3** Moderate · **2** Weak · **1** Minimal','','Match strength is candidate strength, not relationship classification.','', '## Strongest candidates']
 for x in queue[:50]:
  s=x['signals'];md.append(f"- `{x['relationship_id']}` — `{x['left']}` ↔ `{x['right']}` — **{x['match_strength']}/5 {x['match_strength_label']}**, score {x['score']}, shared terms {x['shared_terms']}, identity terms {x['identity_terms']}, subject={s['subject_match']}, domain={s['domain_match']}, world={s['world_match']}")
 (out/'CORE_RELATIONSHIP_DISCOVERY.md').write_text('\n'.join(md)+'\n',encoding='utf-8');print(f'CORE discovery: {len(docs)} docs, {len(candidates)} candidate relationships, {len(queue)} queued.')
if __name__=='__main__':main()
