#!/usr/bin/env python3
"""Group legacy ontology conflicts into repeatable review patterns.

This is intentionally advisory: it never changes raw human labels or promotes
any historical judgment to current truth. It identifies recurring reasons a
legacy relationship cannot be safely migrated.
"""
from __future__ import annotations
import json,re
from pathlib import Path

def norm(s): return re.sub(r'[^A-Z0-9]+','_',str(s or '').upper()).strip('_')
def pattern(case):
    h=norm(case.get('human_label')); a=norm(case.get('machine_label') or case.get('ontology_v2_label')); l=norm(case.get('legacy_label'))
    if h in {'VARIANT','DUPLICATE'} and a in {'RELATED','REVIEW','MISPLACED'}:
        return 'LEGACY_VARIANT_NEEDS_CONTEXT_REVIEW'
    if h=='VARIANT' and a=='VARIANT': return 'ALIGNED_VARIANT'
    if h=='RELATED' and a=='RELATED': return 'ALIGNED_RELATED'
    if h=='SUPPORTING' and a in {'RELATED','REVIEW'}: return 'ROLE_SUPPORT_REVIEW'
    if h=='HISTORICAL': return 'TEMPORAL_ROLE_REVIEW'
    if h=='CONFLICT': return 'CLAIM_CONFLICT_REVIEW'
    if h=='MISPLACED': return 'PLACEMENT_REVIEW'
    if h=='COINCIDENTAL': return 'LOW_RELATIONSHIP_REVIEW'
    return 'OTHER_REVIEW'

def main():
    p=Path('TOOLS/REPOSITORY/REPORTS/CORE_ONTOLOGY_MIGRATION.json')
    data=json.loads(p.read_text(encoding='utf-8')) if p.exists() else {'cases':[]}
    rows=[]
    for c in data.get('cases',[]):
        x=dict(c);x['review_pattern']=pattern(c);rows.append(x)
    counts={}
    for x in rows: counts[x['review_pattern']]=counts.get(x['review_pattern'],0)+1
    out={'schema_version':'2.0','mode':'ADVISORY_ONLY','raw_human_labels_immutable':True,'cases':rows,'pattern_counts':counts,'review_policy':'Patterns identify recurring ambiguity; no automatic relabeling is permitted.'}
    q=Path('TOOLS/REPOSITORY/REPORTS/CORE_ONTOLOGY_REVIEW_PATTERNS.json');q.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'cases':len(rows),'pattern_counts':counts},indent=2))
if __name__=='__main__':main()
