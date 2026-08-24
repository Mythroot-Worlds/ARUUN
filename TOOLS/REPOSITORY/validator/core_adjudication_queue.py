#!/usr/bin/env python3
"""Build a conservative human-adjudication queue from real CORE discoveries."""
from __future__ import annotations
import argparse,json
from pathlib import Path

FINAL_LABELS = {'DUPLICATE','SUPPORTING','HISTORICAL','MISPLACED','CONFLICT','RELATED','COINCIDENTAL','REVIEW','UNRESOLVED','VARIANT'}
LEGACY_LABELS = {'VARIANT'}

def normalize_label(label):
    value = str(label or 'UNCLASSIFIED').strip().upper()
    return value

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');ap.add_argument('--limit',type=int,default=30);a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out
 data=json.loads((out/'CORE_RELATIONSHIP_DISCOVERY.json').read_text(encoding='utf-8')); gate_path=out/'CORE_VARIANT_GATE.json'; gate=json.loads(gate_path.read_text(encoding='utf-8')) if gate_path.exists() else {'relationships':[]}
 gate_by={r.get('relationship_id'):r.get('variant_arbitration',{}) for r in gate.get('relationships',[])}
 rows=data.get('relationships',[]); by={5:[],4:[],3:[],2:[],1:[]}
 for r in rows: by.setdefault(int(r.get('match_strength',1)),[]).append(r)
 order=[]
 for n in (5,4,3,2,1): order.extend(by.get(n,[]))
 queue=order[:a.limit]; review=[]
 for i,r in enumerate(queue,1):
  va=gate_by.get(r['relationship_id'],{})
  eligible=bool(va.get('eligible',False))
  review.append({'review_id':f"ADJ-{i:03d}",'relationship_id':r['relationship_id'],'match_strength':r['match_strength'],'left':r['left'],'right':r['right'],'variant_gate':{'eligible':eligible,'claim_overlap':va.get('claim_overlap',0),'gates':va.get('gates',{}),'reasons':va.get('reasons',[])},'suggested_classification':'VARIANT_CANDIDATE' if eligible else 'UNCLASSIFIED','human_label':None,'human_reason':None,'review_status':'PENDING'})
 result={'engine':'CORE Human Adjudication Queue','mode':'REVIEW_ONLY','source_discoveries':data.get('relationships_discovered',0),'queue_size':len(review),'final_label_vocabulary':sorted(FINAL_LABELS),'legacy_label_vocabulary':sorted(LEGACY_LABELS),'instructions':['Assign a human_label only after reviewing both records and their context.','VARIANT is now valid only when the variant gate passes: same subject, scope, time, purpose, role, and substantially equivalent claims.','A VARIANT_CANDIDATE is not an automatic final label; human/context review is still required.','A failed variant gate is evidence against VARIANT, not evidence for another relationship.','Do not infer canon from match strength alone.','Record a reason and preserve the relationship_id.'],'queue':review}
 (out/'CORE_ADJUDICATION_QUEUE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 md=['# CORE Human Adjudication Queue','','**Human review required. No labels are inferred automatically.**','',f"Source discoveries: **{result['source_discoveries']}**",f"Review queue: **{result['queue_size']}**",'','## Resolution vocabulary','- Current: `DUPLICATE`, `VARIANT`, `SUPPORTING`, `HISTORICAL`, `MISPLACED`, `CONFLICT`, `RELATED`, `COINCIDENTAL`, `REVIEW`, `UNRESOLVED`','- `VARIANT` is current but tightly gated: it means informational near-equivalence, not shared subject matter.','','| Review | Strength | Variant gate | Claim overlap | Relationship | Status |','|---|---:|---|---:|---|---|']
 for r in review: md.append(f"| `{r['review_id']}` | **{r['match_strength']}/5** | {'ELIGIBLE' if r['variant_gate']['eligible'] else 'REJECTED'} | **{r['variant_gate']['claim_overlap']:.2f}** | `{r['left']}` ↔ `{r['right']}` | PENDING |")
 (out/'CORE_ADJUDICATION_QUEUE.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
 print(f'CORE adjudication queue: {len(review)} discoveries queued; {sum(1 for r in review if r["variant_gate"]["eligible"])} pass the VARIANT gate.')
if __name__=='__main__':main()
