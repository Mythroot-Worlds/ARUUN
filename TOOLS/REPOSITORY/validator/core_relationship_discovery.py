#!/usr/bin/env python3
"""CORE relationship discovery: conservative, read-only candidate generation."""
from __future__ import annotations
import argparse,hashlib,json,re
from collections import defaultdict
from pathlib import Path
SKIP={'.git','.github','node_modules','__pycache__','TOOLS'}
ARCHIVE='07_ARCHIVE/'
REPORTS='TOOLS/REPOSITORY/REPORTS/'
STOP=set('about after again against all also and are because been being but can could each for from have into its more most not other our over same should some than that their there these they this those through under was were what when where which while with would your'.split())

def words(t): return {w for w in re.findall(r'[a-z][a-z0-9_]{3,}',t.lower()) if w not in STOP}
def read(p): return p.read_text(encoding='utf-8',errors='replace')
def stable(a,b): return 'REL-'+hashlib.sha1((a+'|'+b).encode()).hexdigest()[:16]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default=REPORTS);ap.add_argument('--scope',default='03_PEOPLES/CULTURES/HEARTH');ap.add_argument('--min-overlap',type=int,default=8);a=ap.parse_args();root=Path(a.root).resolve();base=root/a.scope
 docs=[]
 if base.exists():
  for p in base.rglob('*.md'):
   rel=p.relative_to(root).as_posix()
   if any(x in SKIP for x in p.parts) or rel.startswith(ARCHIVE) or rel.startswith(REPORTS):continue
   ws=words(read(p));
   if ws: docs.append((rel,ws))
 candidates=[]
 # Conservative blocking by shared distinctive terms keeps this tractable and avoids all-pairs noise.
 inv=defaultdict(set)
 for i,(rel,ws) in enumerate(docs):
  for w in ws: inv[w].add(i)
 pairs=set()
 for ids in inv.values():
  ids=list(ids)
  if len(ids)>80: continue
  for i in range(len(ids)):
   for j in range(i+1,len(ids)): pairs.add(tuple(sorted((ids[i],ids[j]))))
 for i,j in pairs:
  pa,wa=docs[i];pb,wb=docs[j]; inter=wa&wb
  if len(inter)<a.min_overlap: continue
  union=wa|wb;j=len(inter)/max(1,len(union))
  if j<0.08: continue
  rid=stable(min(pa,pb),max(pa,pb))
  candidates.append({'relationship_id':rid,'left':pa,'right':pb,'shared_terms':len(inter),'jaccard':round(j,4),'status':'DISCOVERED_UNREVIEWED','review_required':True})
 candidates.sort(key=lambda x:(x['shared_terms'],x['jaccard']),reverse=True)
 # Cap the review queue to the strongest candidates while retaining the total discovered count.
 queue=candidates[:500]
 out=root/a.out;out.mkdir(parents=True,exist_ok=True)
 data={'engine':'CORE Relationship Discovery','mode':'READ_ONLY','scope':a.scope,'documents_analyzed':len(docs),'relationships_discovered':len(candidates),'review_queue_size':len(queue),'relationships':queue,'safety':{'automatic_merge':False,'automatic_canon_change':False,'provenance_required':True}}
 (out/'CORE_RELATIONSHIP_DISCOVERY.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 md=['# CORE Relationship Discovery','','**Read-only candidate generation. No relationship is accepted automatically.**','',f'Documents analyzed: **{len(docs)}**',f'Relationship candidates discovered: **{len(candidates)}**',f'Review queue: **{len(queue)}**','', '## Strongest candidates']
 for x in queue[:50]: md.append(f"- `{x['relationship_id']}` — `{x['left']}` ↔ `{x['right']}` — shared terms {x['shared_terms']}, similarity {x['jaccard']}")
 (out/'CORE_RELATIONSHIP_DISCOVERY.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
 print(f'CORE discovery: {len(docs)} docs, {len(candidates)} candidate relationships, {len(queue)} queued.')
if __name__=='__main__':main()
