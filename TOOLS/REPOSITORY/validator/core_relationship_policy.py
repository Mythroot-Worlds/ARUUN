#!/usr/bin/env python3
"""Validate CORE relationship decisions against the current relationship ontology.

The human annotation set is historical calibration data. When the relationship
ontology changes, an older label may conflict with the current policy; that is
reported as a POLICY_CONFLICT rather than silently treated as a current gold label.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from core_layered_relationship import compare

REGIONS={'COAST','DESERT','MOUNTAINS','PLAINS','RIVER','WETLANDS'}

def load(p,d=None):
    if not p.exists(): return d if d is not None else {}
    return json.loads(p.read_text(encoding='utf-8'))

def expected_from_layers(result):
    l=result['layers']; category=l['category']['state']; subject=l['subject']['state']; context=l['context']['state']; info=l['information_overlap']['state']; revision=l['revision_lineage']['state'];
    if revision=='SAME' and category=='SAME' and subject=='SAME' and context=='SAME': return 'VARIANT'
    if category=='SAME' and subject=='SAME' and context=='DIFFERENT': return 'RELATED'
    if result['decision'] in {'DUPLICATE','VARIANT','RELATED','SUPPORTING','HISTORICAL','CONFLICT','MISPLACED','COINCIDENTAL'}: return result['decision']
    return 'REVIEW'

def region_from_path(path):
    parts=[p.upper() for p in Path(path).parts]
    for p in parts:
        if p in REGIONS:return p
    return None

def policy_cases():
    return [
      ('07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/HEARTH_DESERT_PEOPLES_CULTURAL_BASE_v0.1.md','07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/HEARTH_DESERT_PEOPLES_CULTURAL_BASE_v0.2.md','VARIANT','explicit revision example'),
      ('03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md','03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md','RELATED','same subject, different regional context'),
      ('03_PEOPLES/CULTURES/HEARTH/COAST/FAMILY_BIRTH_CHILDHOOD.md','03_PEOPLES/CULTURES/HEARTH/WETLANDS/FAMILY_BIRTH_CHILDHOOD.md','RELATED','same subject, different regional context'),
      ('03_PEOPLES/CULTURES/HEARTH/PLAINS/FAMILY_BIRTH_CHILDHOOD.md','03_PEOPLES/CULTURES/HEARTH/MOUNTAINS/FAMILY_BIRTH_CHILDHOOD.md','RELATED','same subject, different regional context'),
    ]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');args=ap.parse_args();root=Path(args.root).resolve();out=root/args.out
    cases=[]
    for a,b,expected,reason in policy_cases():
        pa,pb=root/a,root/b
        if not pa.exists() or not pb.exists():
            cases.append({'left':a,'right':b,'expected':expected,'actual':None,'status':'FIXTURE_MISSING','reason':reason});continue
        r=compare(a,pa.read_text(encoding='utf-8',errors='replace'),b,pb.read_text(encoding='utf-8',errors='replace'))
        cases.append({'left':a,'right':b,'expected':expected,'actual':r['decision'],'pass':r['decision']==expected,'reason':reason,'layers':r['layers'],'decision_basis':r['decision_basis']})
    human=load(out/'CORE_HUMAN_RECONCILIATION.json',{'matched':[]})
    conflicts=[]
    for m in human.get('matched',[]):
        choices=set(m.get('human_raw_choices',[])); left,right=m.get('left',''),m.get('right','')
        la,lb=region_from_path(left),region_from_path(right)
        # Current policy explicitly rejects regional siblings as VARIANT.
        if la and lb and la!=lb and 'VARIANT' in choices:
            conflicts.append({'relationship_id':m.get('relationship_id'),'left':left,'right':right,'legacy_human_label':'VARIANT','current_policy':'RELATED','status':'POLICY_CONFLICT','reason':'different regional groups are related, not variants'})
    summary={'policy_cases':len(cases),'policy_passed':sum(c.get('pass',False) for c in cases),'policy_failed':sum(c.get('pass') is False for c in cases),'missing_fixtures':sum(c['status']=='FIXTURE_MISSING' for c in cases),'legacy_policy_conflicts':len(conflicts)}
    report={'engine':'CORE Relationship Policy Validator','ontology_version':'2.0','policy':{'variant':'same underlying information in the same relevant context; wording/detail/version differences allowed','related':'meaningful conceptual relationship with materially different context or information','regional_rule':'different regional groups are RELATED, not VARIANT'},'cases':cases,'legacy_policy_conflicts':conflicts,'summary':summary,'safety':{'historical_human_labels_preserved':True,'automatic_rule_promotion':False,'automatic_canon_change':False}}
    (out/'CORE_RELATIONSHIP_POLICY.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (out/'CORE_RELATIONSHIP_POLICY.md').write_text('# CORE Relationship Policy\n\n'+json.dumps(summary,indent=2)+'\n\nLegacy human labels that conflict with the current ontology are reported, not silently rewritten.\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    if summary['policy_failed'] or summary['missing_fixtures']: raise SystemExit('Current relationship policy validation failed')
if __name__=='__main__':main()
