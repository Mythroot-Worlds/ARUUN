#!/usr/bin/env python3
"""Apply evidence-gated VARIANT arbitration using canonical-family identity."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from core_variant_arbitration import assess_variant
from core_semantic_comparator import compare_units
from core_identity_resolver import resolve_identity
from core_document_identity import identify
from core_canonical_family import resolve as resolve_family
from core_variant_calibration import variant_identity_compatible

SKIP={'.git','.github','TOOLS','07_ARCHIVE','node_modules','__pycache__'}
def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d
def for_source(source,report,key):return [x for x in report.get(key,[]) if x.get('source')==source]
def doc_context(root,rel,claims,units):
    legacy=resolve_identity(root,rel);identity=identify(rel);family=resolve_family(rel,identity)
    return {**legacy,'subject':identity['subject'] or legacy.get('subject'),'content_type':identity['content_type'],'structural_scope':identity['scope'],'canonical_family_id':family.get('canonical_family_id'),'canonical_family_key':family.get('canonical_family_key'),'canonical_family_basis':family.get('canonical_family_basis'),'relation_to_family':family.get('relation_to_family'),'claims':for_source(rel,claims,'claims'),'information_units':for_source(rel,units,'units')}
def discover_same_scope_pairs(root):
    files=[];base=root/'03_PEOPLES/CULTURES/HEARTH'
    if not base.exists():return files
    for p in base.rglob('*.md'):
        rel=p.relative_to(root).as_posix()
        if any(part in SKIP for part in p.parts):continue
        files.append(rel)
    return files
def scope_key(identity):
    scope=identity.get('structural_scope') or identity.get('scope')
    if isinstance(scope,dict):return tuple(sorted(scope.items()))
    return scope
def candidate_key(identity):
    return set(re.findall(r'[a-z0-9]+',identity.get('subject') or '')) | set(re.findall(r'[a-z0-9]+',identity.get('role') or '')) | ({identity.get('canonical_family_key')} if identity.get('canonical_family_key') else set())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    discovery=load(out/'CORE_RELATIONSHIP_DISCOVERY.json',{'relationships':[]});claims=load(out/'CORE_SEMANTIC_CLAIMS.json',{'claims':[]});units=load(out/'CORE_INFORMATION_UNITS.json',{'units':[]})
    rows=[];seen=set();eligible=rejected=0
    def assess_pair(left_rel,right_rel,source='relationship_discovery'):
        nonlocal eligible,rejected
        key=tuple(sorted((left_rel,right_rel)))
        if key in seen or left_rel==right_rel:return
        seen.add(key);left=doc_context(root,left_rel,claims,units);right=doc_context(root,right_rel,claims,units)
        identity_ok,identity_reasons=variant_identity_compatible(left,right)
        comparison=compare_units(left['information_units'],right['information_units']);assessment=assess_variant(left,right)
        if not identity_ok:
            assessment.eligible=False
            assessment.reasons.extend([f'identity_gate:{r}' for r in identity_reasons if r!='same_resolved_scope'])
        x={'relationship_id':f'VAR-{abs(hash(key)) & 0xffffffff:08x}','left':left_rel,'right':right_rel,'source':source,
           'left_identity':{k:left.get(k) for k in ('entity','population','region','subregion','subject','role','purpose','scope','content_type','structural_scope','canonical_family_id','canonical_family_key','relation_to_family')},
           'right_identity':{k:right.get(k) for k in ('entity','population','region','subregion','subject','role','purpose','scope','content_type','structural_scope','canonical_family_id','canonical_family_key','relation_to_family')},
           'identity_match':identity_ok,'identity_reasons':identity_reasons,
           'canonical_family_match':left.get('canonical_family_id')==right.get('canonical_family_id') and left.get('canonical_family_id') is not None,
           'pairwise_semantic_comparison':comparison.as_dict(),'variant_arbitration':assessment.as_dict()}
        x['variant_status']='ELIGIBLE' if assessment.eligible else 'REJECTED';eligible+=int(assessment.eligible);rejected+=int(not assessment.eligible);rows.append(x)
    for r in discovery.get('relationships',[]):assess_pair(r['left'],r['right'])
    files=discover_same_scope_pairs(root);ctx={f:doc_context(root,f,claims,units) for f in files};by_scope={}
    for f,c in ctx.items():by_scope.setdefault(scope_key(c),[]).append(f)
    for scope,items in by_scope.items():
        for i,left in enumerate(items):
            for right in items[i+1:]:
                if candidate_key(ctx[left]) & candidate_key(ctx[right]):assess_pair(left,right,'same_scope_identity_candidate')
    result={'engine':'CORE VARIANT Gate','schema_version':'5.2','mode':'READ_ONLY',
      'definition':'VARIANT means substantially equivalent informational content for the same canonical family, same regional/scope identity, and same document type. Regional variants may differ in wording, depth, presentation, or modest detail. Different regions are RELATED, not VARIANT.',
      'candidate_count':len(rows),'variant_candidates':eligible,'rejected_variant_candidates':rejected,'relationships':rows,
      'identity_gate':{'authoritative':True,'fields':['canonical_family_id','subject','structural_scope','content_type'],'compatibility_fields':['role','purpose'],'semantic_similarity_cannot_override':True,'scope_key_normalized':True},
      'safety':{'automatic_variant_acceptance':False,'automatic_canon_change':False,'provenance_required':True}}
    (out/'CORE_VARIANT_GATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    md=['# CORE VARIANT Gate','','VARIANT requires the same canonical family, same subject, same regional/scope identity, same document type, and substantial informational overlap. Different regions are **RELATED**, not VARIANT.','',f"Candidates assessed: **{len(rows)}**",f"Eligible VARIANT candidates: **{eligible}**",f"Rejected VARIANT candidates: **{rejected}**",'','Canonical family is the lineage layer. Identity remains authoritative; role/purpose are compatibility signals rather than blanket hard gates so legitimate same-scope variants can differ in presentation/depth.','']
    (out/'CORE_VARIANT_GATE.md').write_text('\n'.join(md)+'\n',encoding='utf-8');print(f'CORE VARIANT gate: {len(rows)} assessed; {eligible} eligible; {rejected} rejected.')
if __name__=='__main__':main()
