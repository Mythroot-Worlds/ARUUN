#!/usr/bin/env python3
"""Build a conservative human-adjudication queue from real CORE discoveries."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');ap.add_argument('--limit',type=int,default=30);a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out
 data=json.loads((out/'CORE_RELATIONSHIP_DISCOVERY.json').read_text(encoding='utf-8')); rows=data.get('relationships',[])
 by={5:[],4:[],3:[],2:[],1:[]}
 for r in rows: by.setdefault(int(r.get('match_strength',1)),[]).append(r)
 order=[]
 for n in (5,4,3,2,1): order.extend(by.get(n,[]))
 queue=order[:a.limit]
 review=[]
 for i,r in enumerate(queue,1):
  review.append({'review_id':f"ADJ-{i:03d}",'relationship_id':r['relationship_id'],'match_strength':r['match_strength'],'left':r['left'],'right':r['right'],'suggested_classification':'UNCLASSIFIED','human_label':None,'human_reason':None,'review_status':'PENDING'})
 result={'engine':'CORE Human Adjudication Queue','mode':'REVIEW_ONLY','source_discoveries':data.get('relationships_discovered',0),'queue_size':len(review),'instructions':['Assign a human_label only after reviewing both records.','Use existing labels where applicable: VARIANT, SUPPORTING, HISTORICAL, MISPLACED, CONFLICT, RELATED, COINCIDENTAL, REVIEW.','Do not infer canon from match strength alone.','Record a reason and preserve the relationship_id.'],'queue':review}
 (out/'CORE_ADJUDICATION_QUEUE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 md=['# CORE Human Adjudication Queue','','**Human review required. No labels are inferred automatically.**','',f"Source discoveries: **{result['source_discoveries']}**",f"Review queue: **{result['queue_size']}**",'','| Review | Strength | Relationship | Status |','|---|---:|---|---|']
 for r in review: md.append(f"| `{r['review_id']}` | **{r['match_strength']}/5** | `{r['left']}` ↔ `{r['right']}` | PENDING |")
 (out/'CORE_ADJUDICATION_QUEUE.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
 print(f'CORE adjudication queue: {len(review)} real discoveries queued for human review.')
if __name__=='__main__':main()
