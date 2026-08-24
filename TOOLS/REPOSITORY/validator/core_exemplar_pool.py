#!/usr/bin/env python3
"""CORE A.C.E. exemplar pool builder.

Builds a growing, provenance-preserving example pool from human-adjudicated
relationships and abstract calibration decisions. Current blind-test holdouts
are explicitly excluded so exemplars cannot leak evaluation answers.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def pair_key(left,right): return tuple(sorted((left,right)))

def role(path):
    p=(path or '').upper()
    if 'ARCHIVE' in p:return 'HISTORICAL'
    if 'COMPARATIVE' in p:return 'COMPARATIVE'
    if 'TOOL' in p or '/TOOLS/' in p:return 'TOOL'
    if 'WORKING_CANON' in p:return 'WORKING_CANON'
    if 'WORKING' in p:return 'WORKING'
    return 'CANON'

def domain(path):
    p=(path or '').upper()
    if 'ECOLOGY' in p:return 'ECOLOGY'
    if 'TOOLS' in p:return 'TOOLS'
    if 'PEOPLES' in p or 'CULTURES' in p or 'HEARTH' in p:return 'PEOPLES'
    return 'UNKNOWN'

def build(root,out,holdout_ids=None,holdout_pairs=None):
    ledger=load(out/'CORE_DECISION_LEDGER.json',{'decisions':[]})
    annotations=load(out/'CORE_HUMAN_ANNOTATIONS.json',{'annotations':[]})
    if holdout_ids is None or holdout_pairs is None:
        blind=load(out/'CORE_BLIND_TEST.json',{'predictions':[]})
        holdout_ids={r.get('relationship_id') for r in blind.get('predictions',[]) if r.get('relationship_id')}
        holdout_pairs={pair_key(r.get('left',''),r.get('right','')) for r in blind.get('predictions',[]) if r.get('left') and r.get('right')}
    examples=[];seen=set()
    for d in ledger.get('decisions',[]):
        left=d.get('left') or d.get('path_a') or ''
        right=d.get('right') or d.get('path_b') or ''
        rid=d.get('relationship_id')
        # Abstract decisions are valid exemplars even when they have no concrete pair.
        concrete=bool(left and right)
        if rid and rid in holdout_ids: continue
        if concrete and pair_key(left,right) in holdout_pairs: continue
        key_basis=(rid or d.get('id') or '')+'|'+left+'|'+right
        k='LED-'+hashlib.sha1(key_basis.encode()).hexdigest()[:16]
        if k in seen:continue
        seen.add(k);ctx=d.get('context',{})
        examples.append({'example_id':k,'relationship_id':rid,'left':left or None,'right':right or None,'label':d.get('label'),'raw_choices':[d.get('label')] if d.get('label') else [],'proposed':d.get('proposed'),'reason':d.get('reason',''),'domain':ctx.get('domain') or domain(left),'role':ctx.get('role') or role(left),'source':'DECISION_LEDGER','confidence':'HUMAN_ADJUDICATED'})
    for a in annotations.get('annotations',[]):
        left,right=a.get('left',''),a.get('right','')
        if not left or not right or pair_key(left,right) in holdout_pairs:continue
        k='ANN-'+hashlib.sha1(('|'.join(pair_key(left,right))).encode()).hexdigest()[:16]
        if k in seen:continue
        seen.add(k);choices=a.get('raw_choices',[])
        examples.append({'example_id':k,'relationship_id':a.get('relationship_id'),'left':left,'right':right,'label':choices[0] if len(choices)==1 else 'MULTI','raw_choices':choices,'proposed':a.get('proposed'),'reason':a.get('reasoning',''),'domain':domain(left),'role':role(left),'source':'HUMAN_ANNOTATION','confidence':'HUMAN_REVIEWED_UNMATCHED'})
    examples.sort(key=lambda x:x['example_id'])
    pool={'engine':'CORE A.C.E. Exemplar Pool','schema_version':'1.1','mode':'READ_ONLY','example_count':len(examples),'examples':examples,'holdout_exclusion':{'relationship_ids':len(holdout_ids),'pairs':len(holdout_pairs),'leakage_prevented':True},'safety':{'automatic_rule_promotion':False,'automatic_canon_change':False,'holdout_training_leakage':False}}
    (out/'CORE_EXEMPLAR_POOL.json').write_text(json.dumps(pool,indent=2),encoding='utf-8')
    md=['# CORE A.C.E. Exemplar Pool','','Growing human-verified precedent library. Current blind-test holdouts are excluded.','',f'Examples: **{len(examples)}**',f'Excluded holdout IDs: **{len(holdout_ids)}**',f'Excluded holdout pairs: **{len(holdout_pairs)}**','', '## Sources']
    md.append(f'- Decision ledger examples: **{sum(x["source"]=="DECISION_LEDGER" for x in examples)}**')
    md.append(f'- Human annotation examples: **{sum(x["source"]=="HUMAN_ANNOTATION" for x in examples)}**')
    (out/'CORE_EXEMPLAR_POOL.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    return pool

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out;out.mkdir(parents=True,exist_ok=True);p=build(root,out);print(f"CORE exemplar pool: {p['example_count']} leakage-safe examples.")
if __name__=='__main__':main()
