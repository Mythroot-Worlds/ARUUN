#!/usr/bin/env python3
"""Layered document relationship model for CORE A.C.E.

Relationships are decided from ordered layers: category -> subject -> context
-> content -> purpose -> information overlap. VARIANT means the same underlying
information in the same relevant context, allowing wording/detail/version
changes. RELATED means meaningful conceptual overlap with materially different
context or information.
"""
from __future__ import annotations
import re
from pathlib import Path
from core_document_identity import identify
STOP=set("the and for with from that this document regional family final draft version comparative variant duplicate supporting historical canonical canon hearth region regions reference audit checklist base peoples cultural oasis integrated working first pass".split())
def words(text): return {w for w in re.findall(r"[a-z][a-z0-9_]{3,}",text.lower()) if w not in STOP}
def overlap_stats(a,b):
    aa,bb=words(a),words(b); shared=len(aa&bb)
    return {'jaccard':shared/max(1,len(aa|bb)),'containment_left':shared/max(1,len(aa)),'containment_right':shared/max(1,len(bb)),'shared_terms':shared,'left_terms':len(aa),'right_terms':len(bb)}
def base_document_key(path):
    stem=Path(path).stem.lower();stem=re.sub(r"(?:_v\d+(?:\.\d+)?)$|(?:_revision_?\d+)$|(?:_rev_?\d+)$|(?:_draft_?\d+)$", "", stem);stem=re.sub(r"_comparative$", "", stem);return (str(Path(path).parent).lower(), stem)
def layer_profile(path,text):
    i=identify(path);return {'category':i['content_type'],'subject':i['subject'],'context':i['scope'],'purpose':i['role'],'content_fingerprint_size':len(words(text)),'path':path,'base_document_key':base_document_key(path)}
def compare(a_path,a_text,b_path,b_text):
    a,b=layer_profile(a_path,a_text),layer_profile(b_path,b_text);stats=overlap_stats(a_text,b_text);same_category=a['category']==b['category'];same_subject=bool(a['subject'] and b['subject'] and a['subject']==b['subject']);same_context=a['context']==b['context'];same_purpose=a['purpose']==b['purpose'];same_revision_lineage=a['base_document_key']==b['base_document_key'] and same_context
    informational_equivalence=(stats['containment_left']>=0.62 and stats['jaccard']>=0.28) or same_revision_lineage
    layers={'category':{'state':'SAME' if same_category else 'DIFFERENT','left':a['category'],'right':b['category']},'subject':{'state':'SAME' if same_subject else 'DIFFERENT','left':a['subject'],'right':b['subject']},'context':{'state':'SAME' if same_context else 'DIFFERENT','left':a['context'],'right':b['context']},'content':{'state':'NEAR_SAME' if informational_equivalence else ('OVERLAPPING' if stats['jaccard']>=0.20 else 'DIFFERENT'),'statistics':{k:round(v,4) if isinstance(v,float) else v for k,v in stats.items()}},'purpose':{'state':'SAME' if same_purpose else 'DIFFERENT','left':a['purpose'],'right':b['purpose']},'information_overlap':{'state':'HIGH' if informational_equivalence else ('MEDIUM' if stats['jaccard']>=0.20 else 'LOW'),'informational_equivalence':informational_equivalence},'revision_lineage':{'state':'SAME' if same_revision_lineage else 'DIFFERENT','left':a['base_document_key'],'right':b['base_document_key']},'path':{'left':a['path'],'right':b['path']}}
    if same_category and same_subject and same_context and informational_equivalence: decision='DUPLICATE' if stats['jaccard']>=0.85 and max(stats['containment_left'],stats['containment_right'])>=0.90 and not same_revision_lineage else 'VARIANT'
    elif same_category and same_subject and not same_context: decision='RELATED'
    elif same_category and informational_equivalence: decision='RELATED'
    elif same_category and stats['jaccard']>=0.20: decision='RELATED'
    elif not same_category and stats['jaccard']<0.12: decision='COINCIDENTAL'
    else: decision='REVIEW'
    return {'decision':decision,'layers':layers,'decision_basis':{'category':layers['category']['state'],'subject':layers['subject']['state'],'context':layers['context']['state'],'information':layers['information_overlap']['state'],'purpose':layers['purpose']['state'],'revision_lineage':layers['revision_lineage']['state']},'rules':{'variant_requires':['same category','same subject','same relevant context','same underlying information'],'revision_evidence':['same normalized document key in same directory is explicit revision lineage'],'related_trigger':['same conceptual category/subject with different context or materially different information']}}
CALIBRATION_CASES=(('07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/HEARTH_DESERT_PEOPLES_CULTURAL_BASE_v0.1.md','07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/HEARTH_DESERT_PEOPLES_CULTURAL_BASE_v0.2.md','VARIANT'),('03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md','03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md','RELATED'))
