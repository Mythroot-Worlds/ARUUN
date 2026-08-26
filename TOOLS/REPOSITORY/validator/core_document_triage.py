#!/usr/bin/env python3
"""CORE A.C.E. document triage: identity and placement first; relationship detail second."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from core_layered_relationship import compare,CALIBRATION_CASES
from core_canonical_context import build_for_pair
from core_document_identity import identify
REGIONS=("PLAINS","MOUNTAINS","RIVER","WETLANDS","DESERT","COAST")
HEARTH_ROOT="03_PEOPLES/CULTURES/HEARTH"
def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d
def text(root,p):
    try:return (root/p).read_text(encoding='utf-8',errors='replace')
    except:return ''
def canonical_result(case,root): return build_for_pair(case,root)['canonical_context']
def placement(ident):
    path=Path(ident['path']);scope=ident.get('scope',{});region=scope.get('region');layer=ident.get('identity_layer');parent=path.parent.as_posix()
    if layer=='CANONICAL_ROOT' and ident.get('content_type')=='CULTURE' and region:
        if path.stem.upper()==region: parent=f'{HEARTH_ROOT}'
        elif 'COMPARATIVE' in path.parts: parent=f'{HEARTH_ROOT}/COMPARATIVE'
    elif layer=='REGIONAL_SPECIALIZATION' and region: parent=f'{HEARTH_ROOT}/{region}'
    elif layer=='HISTORICAL_ARTIFACT' and '07_ARCHIVE/HISTORICAL' in parent.upper(): parent='07_ARCHIVE/HISTORICAL'
    elif layer=='SUPPORTING_ARTIFACT' and 'COMPARATIVE' in path.as_posix().upper(): parent=f'{HEARTH_ROOT}/COMPARATIVE'
    return {'content_type':ident['content_type'],'scope':scope,'identity_layer':layer,'role':ident['role'],'repository_parent':parent,'placement_basis':['document_identity_layer','document_scope','filename_when_canonical_regional_root']}
def _is_hearth_culture(ident): return ident.get('content_type')=='CULTURE' and ident.get('path','').upper().startswith(HEARTH_ROOT)
def _is_hearth_canonical_root(ident):
    path=Path(ident.get('path',''))
    return _is_hearth_culture(ident) and ident.get('role')=='AUTHORITATIVE' and path.parent.as_posix().upper()==HEARTH_ROOT
def _is_regional_root(ident):
    path=Path(ident.get('path',''));region=ident.get('scope',{}).get('region')
    return bool(region and path.parent.as_posix().upper()==HEARTH_ROOT and path.stem.upper()==region)
def _is_broad_hearth_root(ident):
    path=Path(ident.get('path',''))
    return _is_hearth_culture(ident) and not ident.get('scope',{}).get('regional_scope') and path.parent.as_posix().upper()==HEARTH_ROOT
def triage(case,root):
    a,b=case.get('left',''),case.get('right','');result=compare(a,text(root,a),b,text(root,b));canon=canonical_result(case,root);result['canonical_context']=canon
    ia,ib=identify(a),identify(b);pa,pb=placement(ia),placement(ib);same_subject=ia['content_type']==ib['content_type'] and ia['subject']==ib['subject'];same_scope=ia['scope']==ib['scope'];regional_siblings=bool(ia['scope'].get('regional_scope') and ib['scope'].get('regional_scope') and ia['scope']!=ib['scope']);supporting_layer=ia['role']=='SUPPORTING' or ib['role']=='SUPPORTING';authoritative_pair=ia['role']=='AUTHORITATIVE' and ib['role']=='AUTHORITATIVE';time_compatible=ia['role']!='HISTORICAL' and ib['role']!='HISTORICAL';hint=canon.get('canonical_relationship_hint','REVIEW');base=result['decision']
    broad_regional_pair=(_is_broad_hearth_root(ia) and _is_regional_root(ib)) or (_is_broad_hearth_root(ib) and _is_regional_root(ia))
    both_canonical_roots=ia.get('identity_layer')=='CANONICAL_ROOT' and ib.get('identity_layer')=='CANONICAL_ROOT'
    both_hearth_canonical_roots=_is_hearth_canonical_root(ia) and _is_hearth_canonical_root(ib)
    if regional_siblings and same_subject:
        result['decision']='RELATED';result['canonical_decision_basis']='same canonical subject represented in distinct regional scopes'
    elif broad_regional_pair and authoritative_pair:
        result['decision']='VARIANT';result['canonical_decision_basis']='broad Hearth canonical framework and regional canonical root are layered representations of the same cultural domain'
    elif both_hearth_canonical_roots and not same_subject:
        result['decision']='RELATED';result['canonical_decision_basis']='distinct authoritative Hearth root documents cover different subjects; relationship is organizational, not a variant'
    elif both_canonical_roots and not same_subject:
        result['decision']='RELATED';result['canonical_decision_basis']='distinct authoritative canonical roots cover different subjects; relationship is organizational, not a variant'
    elif hint=='VARIANT' and not same_subject:
        result['decision']='RELATED';result['canonical_decision_basis']='variant hint rejected because document subjects differ; retain organizational relationship instead'
    elif hint=='CONFLICT':
        evidence=canon.get('a_against_knowns',{}).get('conflict_evidence',[])+canon.get('b_against_knowns',{}).get('conflict_evidence',[])
        if same_subject and same_scope and authoritative_pair and time_compatible and evidence:
            result['decision']='CONFLICT';result['canonical_decision_basis']='explicit claim-level contradiction evidence between authoritative same-scope documents'
        else: result['decision']=base if base in {'RELATED','SUPPORTING','HISTORICAL','COINCIDENTAL'} else 'REVIEW';result['canonical_decision_basis']='conflict hint rejected because structural gates were not satisfied'
    elif hint=='RELATED' and base in {'VARIANT','DUPLICATE','REVIEW'} and not same_scope:
        result['decision']='RELATED';result['canonical_decision_basis']=canon.get('canonical_hint_reason')
    elif hint=='SUPPORTING' and base in {'VARIANT','DUPLICATE','REVIEW'} and same_subject and same_scope:
        result['decision']='SUPPORTING';result['canonical_decision_basis']=canon.get('canonical_hint_reason')
    elif same_category(result) and same_scope and not same_subject and authoritative_pair:
        result['decision']='RELATED';result['canonical_decision_basis']='same cultural scope and document category establish a useful organizational relationship despite different subjects'
    elif same_category(result) and not same_scope and authoritative_pair and _is_hearth_culture(ia) and _is_hearth_culture(ib):
        result['decision']='RELATED';result['canonical_decision_basis']='same cultural domain with distinct scope is sufficient for organizational relationship; content similarity is not required'
    relationship_tags=[]
    if same_subject: relationship_tags.append('RELATED')
    if supporting_layer: relationship_tags.append('SUPPORTING')
    if ia['role']=='HISTORICAL' or ib['role']=='HISTORICAL': relationship_tags.append('HISTORICAL')
    result['relationship_tags']=list(dict.fromkeys(relationship_tags));status='DIRECT' if result['decision'] in {'DUPLICATE','VARIANT','RELATED','SUPPORTING','HISTORICAL','CONFLICT','COINCIDENTAL'} else 'ESCALATE'
    return {'relationship_id':case.get('relationship_id'),'documents':{'a':a,'b':b},'triage_status':status,'decision':result['decision'],'reason':'identity and placement resolved before relationship detail' if status=='DIRECT' else 'identity/canonical context insufficient for safe direct disposition','placement':{'a':pa,'b':pb},'identity':{'a':ia,'b':ib,'same_subject':same_subject,'same_scope':same_scope,'regional_siblings':regional_siblings,'supporting_layer':supporting_layer,'authoritative_pair':authoritative_pair,'time_compatible':time_compatible},'layered_comparison':result,'canonical_context':canon,'deep_investigation_required':status!='DIRECT','safety':{'automatic_canon_change':False,'automatic_rule_promotion':False}}
def same_category(result): return result.get('layers',{}).get('category',{}).get('state')=='SAME'
def run_calibration(root):
    out=[]
    for a,b,expected in CALIBRATION_CASES:
        r=compare(a,text(root,a),b,text(root,b));out.append({'left':a,'right':b,'expected':expected,'actual':r['decision'],'pass':r['decision']==expected,'comparison':r,'canonical_context':build_for_pair({'left':a,'right':b},root)['canonical_context']})
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out;queue=load(out/'CORE_ADJUDICATION_QUEUE.json',{'queue':[]});results=[triage(c,root) for c in queue.get('queue',[])];cal=run_calibration(root);summary={'cases':len(results),'direct_triage':sum(x['triage_status']=='DIRECT' for x in results),'deep_investigation':sum(x['deep_investigation_required'] for x in results),'canonical_grounded_cases':sum(bool(x.get('canonical_context')) for x in results),'canonical_hint_counts':{h:sum(x.get('canonical_context',{}).get('canonical_relationship_hint')==h for x in results) for h in ('VARIANT','RELATED','SUPPORTING','HISTORICAL','CONFLICT','MISPLACED','DUPLICATE','REVIEW')},'identity_layer_counts':{'supporting_layer':sum(x['identity']['supporting_layer'] for x in results),'regional_siblings':sum(x['identity']['regional_siblings'] for x in results),'same_subject_same_scope':sum(x['identity']['same_subject'] and x['identity']['same_scope'] for x in results),'authoritative_pairs':sum(x['identity']['authoritative_pair'] for x in results)},'decisions':{},'calibration_cases':len(cal),'calibration_passed':sum(x['pass'] for x in cal),'calibration_failed':sum(not x['pass'] for x in cal)}
    for x in results: summary['decisions'][x['decision']]=summary['decisions'].get(x['decision'],0)+1
    payload={'engine':'CORE A.C.E. Document Triage','schema_version':'3.7','mode':'READ_ONLY','purpose':'identify and place documents before describing pair relationships','cases':results,'calibration':cal,'summary':summary,'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
    (out/'CORE_DOCUMENT_TRIAGE.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_DOCUMENT_TRIAGE.md').write_text('# CORE Document Triage\n\n'+json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
    if any(not x['pass'] for x in cal): raise SystemExit('Layered relationship calibration failed')
if __name__=='__main__':main()
