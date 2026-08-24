#!/usr/bin/env python3
"""CORE A.C.E. exemplar pool builder with structured deciding factors."""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
from core_foundations import factor_snapshot, relationship_test

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def pair_key(left,right): return tuple(sorted((left or '',right or '')))

def role(path):
    p=(path or '').upper()
    if 'ARCHIVE' in p:return 'HISTORICAL'
    if 'COMPARATIVE' in p:return 'COMPARATIVE'
    if 'CHECKLIST' in p or 'AUDIT' in p or 'TOOL' in p or '/TOOLS/' in p:return 'TOOL'
    if 'WORKING_CANON' in p:return 'WORKING_CANON'
    if 'WORKING' in p or 'REVISION' in p or 'DEMOGRAPHIC' in p:return 'WORKING'
    return 'CANON'

def domain(path):
    p=(path or '').upper()
    if 'ECOLOGY' in p:return 'ECOLOGY'
    if 'TOOLS' in p:return 'TOOLS'
    if 'PEOPLES' in p or 'CULTURES' in p or 'HEARTH' in p:return 'PEOPLES'
    return 'UNKNOWN'

def build_features(left,right,reason=''):
    snap=factor_snapshot((left or '')+' '+(reason or ''),(right or '')+' '+(reason or ''))
    d=snap['dimensions']
    return {
        'scope':sorted(set(d['scope']['a']+d['scope']['b'])),
        'function':sorted(set(d['function']['a']+d['function']['b'])),
        'authority':sorted(set(d['coherence']['a']+d['coherence']['b'])) if d.get('coherence') else [],
        'population':[],
        'deciding_dimensions':{k:v for k,v in d.items() if v['a'] or v['b']},
        'principle':snap['principle'],
    }

def build(root,out,holdout_ids=None,holdout_pairs=None):
    ledger=load(out/'CORE_DECISION_LEDGER.json',{'decisions':[]}); annotations=load(out/'CORE_HUMAN_ANNOTATIONS.json',{'annotations':[]})
    if holdout_ids is None or holdout_pairs is None:
        blind=load(out/'CORE_BLIND_TEST.json',{'predictions':[]});holdout_ids={r.get('relationship_id') for r in blind.get('predictions',[]) if r.get('relationship_id')};holdout_pairs={pair_key(r.get('left'),r.get('right')) for r in blind.get('predictions',[])}
    examples=[];seen=set()
    for d in ledger.get('decisions',[]):
        left=d.get('left') or d.get('path_a') or '';right=d.get('right') or d.get('path_b') or '';rid=d.get('relationship_id')
        if rid and rid in holdout_ids:continue
        if left and right and pair_key(left,right) in holdout_pairs:continue
        k='LED-'+hashlib.sha1(((rid or d.get('id') or '')+'|'+left+'|'+right).encode()).hexdigest()[:16]
        if k in seen:continue
        seen.add(k);ctx=d.get('context',{});reason=d.get('reason','');label=d.get('label');examples.append({'example_id':k,'relationship_id':rid,'left':left or None,'right':right or None,'label':label,'raw_choices':[label] if label else [],'proposed':d.get('proposed'),'reason':reason,'domain':ctx.get('domain') or domain(left),'role':ctx.get('role') or role(left),'features':build_features(left,right,reason),'decision_factors':relationship_test(label,build_features(left,right,reason).get('deciding_dimensions',{})) if label else None,'source':'DECISION_LEDGER','confidence':'HUMAN_ADJUDICATED'})
    for a in annotations.get('annotations',[]):
        left,right=a.get('left',''),a.get('right','')
        if not left or not right or pair_key(left,right) in holdout_pairs:continue
        k='ANN-'+hashlib.sha1(('|'.join(pair_key(left,right))).encode()).hexdigest()[:16]
        if k in seen:continue
        seen.add(k);choices=a.get('raw_choices',[]);reason=a.get('reasoning','');label=choices[0] if len(choices)==1 else 'MULTI';features=build_features(left,right,reason);examples.append({'example_id':k,'relationship_id':a.get('relationship_id'),'left':left,'right':right,'label':label,'raw_choices':choices,'proposed':a.get('proposed'),'reason':reason,'domain':domain(left),'role':role(left),'features':features,'decision_factors':relationship_test(label,features.get('deciding_dimensions',{})) if label in {'RELATED','VARIANT','SUPPORTING','HISTORICAL','CONFLICT','MISPLACED','DUPLICATE'} else None,'source':'HUMAN_ANNOTATION','confidence':'HUMAN_REVIEWED_UNMATCHED'})
    examples.sort(key=lambda x:x['example_id']);pool={'engine':'CORE A.C.E. Exemplar Pool','schema_version':'2.0','mode':'READ_ONLY','example_count':len(examples),'examples':examples,'holdout_exclusion':{'relationship_ids':len(holdout_ids),'pairs':len(holdout_pairs),'leakage_prevented':True},'purpose':'precedent library; examples describe deciding factors and are never authoritative classifications','safety':{'automatic_rule_promotion':False,'automatic_canon_change':False,'holdout_training_leakage':False}}
    (out/'CORE_EXEMPLAR_POOL.json').write_text(json.dumps(pool,indent=2),encoding='utf-8');(out/'CORE_EXEMPLAR_POOL.md').write_text('# CORE A.C.E. Exemplar Pool\n\nHuman-verified precedent library with structured deciding-factor descriptions. Examples are advisory pattern references, not classification authority.\n\n'+f'Examples: **{len(examples)}**\n\nExcluded holdout IDs: **{len(holdout_ids)}**\n',encoding='utf-8');return pool

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out;out.mkdir(parents=True,exist_ok=True);p=build(root,out);print(f"CORE exemplar pool: {p['example_count']} leakage-safe examples with deciding factors.")
if __name__=='__main__':main()
