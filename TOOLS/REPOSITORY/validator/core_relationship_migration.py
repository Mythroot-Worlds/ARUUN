#!/usr/bin/env python3
"""Migrate historical relationship annotations onto the active ontology.

Original human labels are immutable provenance. This module derives a separate
ontology-v2 label from the layered relationship model and records whether the
legacy label agrees, conflicts, or needs human review.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from core_layered_relationship import compare

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def classify(a,b,root):
    pa,pb=root/a,root/b
    if not pa.exists() or not pb.exists():
        return None,'FIXTURE_MISSING',{}
    result=compare(a,pa.read_text(encoding='utf-8',errors='replace'),b,pb.read_text(encoding='utf-8',errors='replace'))
    return result.get('decision'),'TESTED',result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    recon=load(out/'CORE_HUMAN_RECONCILIATION.json',{'matched':[]})
    records=[];counts={};
    for m in recon.get('matched',[]):
        left,right=m.get('left',''),m.get('right','');legacy=(m.get('human_raw_choices') or [])
        actual,status,detail=classify(left,right,root)
        if status=='FIXTURE_MISSING':
            state='ONTOLOGY_REQUIRES_REVIEW';active='REVIEW'
        elif actual in {'REVIEW',None}:
            state='ONTOLOGY_REQUIRES_REVIEW';active='REVIEW'
        elif actual in legacy:
            state='LEGACY_AGREES';active=actual
        else:
            state='LEGACY_CONFLICTS';active=actual
        rec={'relationship_id':m.get('relationship_id'),'left':left,'right':right,'legacy_human_labels':legacy,'legacy_reasoning':m.get('human_reasoning',''),'ontology_v2_label':active,'migration_status':state,'identity_layers':detail.get('layers',{}) if detail else {},'decision_basis':detail.get('decision_basis',{}) if detail else {},'source':'CORE_HUMAN_RECONCILIATION.json'}
        records.append(rec);counts[active]=counts.get(active,0)+1
    migration={'engine':'CORE Relationship Ontology Migration','ontology_version':'2.0','mode':'DERIVED_CALIBRATION','records':records,'summary':{'records':len(records),'legacy_agrees':sum(r['migration_status']=='LEGACY_AGREES' for r in records),'legacy_conflicts':sum(r['migration_status']=='LEGACY_CONFLICTS' for r in records),'requires_review':sum(r['migration_status']=='ONTOLOGY_REQUIRES_REVIEW' for r in records),'active_label_counts':counts},'safety':{'original_human_labels_immutable':True,'historical_provenance_preserved':True,'automatic_rule_promotion':False,'automatic_canon_change':False,'human_review_required_for_conflicts':True}}
    (out/'CORE_RELATIONSHIP_ONTOLOGY_V2.json').write_text(json.dumps(migration,indent=2),encoding='utf-8')
    lines=['# CORE Relationship Ontology v2 Migration','','Original human annotations remain immutable historical provenance. `ontology_v2_label` is a derived active-policy label.','','## Summary',f"- Records: **{len(records)}**",f"- Legacy agrees: **{migration['summary']['legacy_agrees']}**",f"- Legacy conflicts: **{migration['summary']['legacy_conflicts']}**",f"- Requires review: **{migration['summary']['requires_review']}**",'','## Active labels']
    lines += [f'- `{k}`: **{v}**' for k,v in sorted(counts.items())]
    lines += ['','## Conflicts requiring review']
    for r in records:
        if r['migration_status']=='LEGACY_CONFLICTS': lines.append(f"- `{r['relationship_id']}` — legacy `{', '.join(r['legacy_human_labels'])}` → ontology v2 `{r['ontology_v2_label']}`")
    (out/'CORE_RELATIONSHIP_ONTOLOGY_V2.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(migration['summary'],indent=2))
    if migration['summary']['requires_review']:
        print('Ontology migration contains human-review candidates; preserving them as REVIEW rather than failing the audit.')
if __name__=='__main__':main()
