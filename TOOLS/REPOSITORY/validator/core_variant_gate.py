#!/usr/bin/env python3
"""Apply evidence-gated VARIANT arbitration using document identity + information evidence.

Mythroot VARIANT is deliberately narrow: same informational subject, same
regional/organizational scope, same document role/purpose, and substantially
equivalent underlying information. Similar subject matter across different
regions is NOT a variant.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from core_variant_arbitration import assess_variant
from core_semantic_comparator import compare_units

SKIP={'.git','.github','TOOLS','07_ARCHIVE','node_modules','__pycache__'}
REGIONS={'HEARTH','PLAINS','MOUNTAINS','RIVER','WETLANDS','DESERT','COAST'}

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def normalize_name(v):
    return re.sub(r'[^a-z0-9]+','_',v.lower()).strip('_') if v else None

def path_context(rel):
    """Derive stable identity from repository structure before prose heuristics."""
    p=Path(rel); parts=[x.upper() for x in p.parts]; stem=p.stem.upper()
    region='HEARTH'
    if 'HEARTH' in parts:
        i=parts.index('HEARTH')
        if i+1<len(parts) and parts[i+1] in REGIONS: region=parts[i+1]
        elif i+2<len(parts) and parts[i+1] in REGIONS: region=parts[i+1]
    # The filename is the strongest available document-subject identifier.
    subject=normalize_name(re.sub(r'_V\d+(?:\.\d+)?$','',stem))
    # Role/purpose are intentionally coupled to the document's structural job.
    role=subject
    if 'SPECIALIST_HOUSES' in stem: role='specialist_houses'
    if 'SPECIALIST_LINEAGES' in stem: role='specialist_lineages'
    if 'GOVERNANCE' in stem: role='governance_authority'
    if 'PARTNERSHIP' in stem: role='family_partnership'
    if 'BIRTH_CHILDHOOD' in stem: role='family_birth_childhood'
    purpose=role
    return {'subject':subject,'scope':region,'purpose':purpose,'role':role}

def front_context(path):
    try: body=path.read_text(encoding='utf-8',errors='replace')[:30000]
    except:return {}
    ctx={'subject':None,'scope':None,'time':None,'purpose':None,'role':None}
    for line in body.splitlines()[:120]:
        m=re.match(r'^\s*[-#]*\s*(subject|scope|time|date|purpose|role|document\s*role|type)\s*[:=-]\s*(.+?)\s*$',line,re.I)
        if not m:continue
        key=re.sub(r'\s+','_',m.group(1).lower());val=m.group(2).strip()
        if key=='date':key='time'
        if key in ('document_role','type'):key='role'
        if key in ctx and val:ctx[key]=val
    return ctx

def for_source(source,report,key):return [x for x in report.get(key,[]) if x.get('source')==source]

def doc_context(root,rel,claims,units):
    c=path_context(rel)
    front=front_context(root/rel)
    # Explicit metadata may refine path identity, but cannot erase structural scope.
    for k,v in front.items():
        if v and k!='scope': c[k]=v
    c['scope']=path_context(rel)['scope']
    c['claims']=for_source(rel,claims,'claims')
    c['information_units']=for_source(rel,units,'units')
    return c

def discover_same_scope_pairs(root):
    """Find possible variants the relationship discovery layer may omit."""
    files=[]
    for p in root.rglob('*.md'):
        rel=p.relative_to(root).as_posix()
        if any(part in SKIP for part in p.parts): continue
        if not rel.startswith('03_PEOPLES/CULTURES/HEARTH/'): continue
        files.append(rel)
    return files

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    discovery=load(out/'CORE_RELATIONSHIP_DISCOVERY.json',{'relationships':[]});claims=load(out/'CORE_SEMANTIC_CLAIMS.json',{'claims':[]});units=load(out/'CORE_INFORMATION_UNITS.json',{'units':[]})
    rows=[];seen=set();eligible=rejected=0
    def assess_pair(left_rel,right_rel,source='relationship_discovery'):
        nonlocal eligible,rejected
        key=tuple(sorted((left_rel,right_rel)))
        if key in seen or left_rel==right_rel:return
        seen.add(key)
        left=doc_context(root,left_rel,claims,units);right=doc_context(root,right_rel,claims,units)
        assessment=assess_variant(left,right);comparison=compare_units(left['information_units'],right['information_units'])
        # Same-scope identity is a hard Mythroot gate. Unknown time is allowed when
        # neither document declares a temporal qualifier; an explicit mismatch fails.
        x={'relationship_id':f'VAR-{abs(hash(key)) & 0xffffffff:08x}','left':left_rel,'right':right_rel,'source':source,'pairwise_semantic_comparison':comparison.as_dict(),'variant_arbitration':assessment.as_dict()}
        x['variant_status']='ELIGIBLE' if assessment.eligible else 'REJECTED';eligible+=int(assessment.eligible);rejected+=int(not assessment.eligible);rows.append(x)
    for r in discovery.get('relationships',[]): assess_pair(r['left'],r['right'])
    # Add same-scope/same-role candidate comparisons so true variants are not lost
    # merely because generic relationship discovery favored cross-scope similarity.
    files=discover_same_scope_pairs(root);ctx={f:doc_context(root,f,claims,units) for f in files}
    buckets={}
    for f,c in ctx.items(): buckets.setdefault((c['scope'],c['role'],c['purpose']),[]).append(f)
    for bucket,items in buckets.items():
        if len(items)<2: continue
        for i,left in enumerate(items):
            for right in items[i+1:]:
                assess_pair(left,right,'same_scope_role_candidate')
    result={'engine':'CORE VARIANT Gate','schema_version':'3.0','mode':'READ_ONLY','definition':'VARIANT means near-equivalent informational content for the same subject within the same scope, document role, purpose, and applicable time. Wording, presentation, formatting, and modest detail may differ. Similar information across different regions is not VARIANT.','candidate_count':len(rows),'variant_candidates':eligible,'rejected_variant_candidates':rejected,'relationships':rows,'safety':{'automatic_variant_acceptance':False,'automatic_canon_change':False,'provenance_required':True}}
    (out/'CORE_VARIANT_GATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    md=['# CORE VARIANT Gate','','VARIANT is informational near-equivalence within the same identity/scope. Similar subject matter across different regions is **not** VARIANT.','',f"Candidates assessed: **{len(rows)}**",f"Eligible VARIANT candidates: **{eligible}**",f"Rejected VARIANT candidates: **{rejected}**",'','## Required identity','- Same subject','- Same regional/organizational scope','- Same applicable time, when explicitly specified','- Same purpose','- Same document role','- Substantially equivalent underlying information','', 'The gate also evaluates same-scope/same-role candidate pairs so variants are not missed merely because broad relationship discovery favors cross-scope similarity.']
    (out/'CORE_VARIANT_GATE.md').write_text('\n'.join(md)+'\n',encoding='utf-8');print(f'CORE VARIANT gate: {len(rows)} assessed; {eligible} eligible; {rejected} rejected.')
if __name__=='__main__':main()
