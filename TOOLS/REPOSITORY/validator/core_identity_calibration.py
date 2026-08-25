#!/usr/bin/env python3
"""Disposable structural calibration for CORE identity/layer precedence."""
from __future__ import annotations
import tempfile
from pathlib import Path
from core_document_identity import identify
from core_document_triage import triage
from core_variant_arbitration import assess_variant
REGION_ROOT="03_PEOPLES/CULTURES/HEARTH"
def write(root, rel, body):
    p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body,encoding="utf-8")
def main():
    cases=[]
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        a=f"{REGION_ROOT}/DESERT/FAMILY_BIRTH_CHILDHOOD.md"; b=f"{REGION_ROOT}/RIVER/FAMILY_BIRTH_CHILDHOOD.md"
        write(root,a,"Birth and childhood in Desert communities. Regional practices differ.");write(root,b,"Birth and childhood in River communities. Regional practices differ.")
        ia,ib=identify(a),identify(b);cases.append({"name":"regional_sibling","pass":ia["subject"]==ib["subject"] and ia["scope"]!=ib["scope"],"expected":"RELATED structural identity"})
        c=f"{REGION_ROOT}/DESERT/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md";write(root,c,"Comparative reference for Desert birth and childhood practices.")
        ic=identify(c);cases.append({"name":"comparative_reference","pass":ic["role"]=="SUPPORTING" and ic["subject"]==ia["subject"],"expected":"SUPPORTING layer"})
        r=triage({"relationship_id":"CAL-SUPPORT","left":a,"right":c},root);cases.append({"name":"canonical_vs_supporting","pass":r["decision"]=="SUPPORTING","actual":r["decision"],"expected":"SUPPORTING"})
        v=f"{REGION_ROOT}/DESERT/FAMILY_BIRTH_CHILDHOOD_v2.md";write(root,v,"Birth and childhood in Desert communities. Children remain with kin during early years.");write(root,a,"Birth and childhood in Desert communities. Children remain with kin during early years.")
        iv=identify(v);av={**iv,"claims":["birth childhood desert children kin early years"]};bv={**ia,"claims":["birth childhood desert children kin early years"]};assessment=assess_variant(av,bv);cases.append({"name":"same_scope_variant","pass":assessment.eligible,"expected":"ELIGIBLE VARIANT"})
        x=f"{REGION_ROOT}/DESERT/A/FAMILY_BIRTH_CHILDHOOD.md";y=f"{REGION_ROOT}/DESERT/B/FAMILY_BIRTH_CHILDHOOD.md";write(root,x,"Birth and childhood in Desert communities. The canonical rule says children remain with kin.");write(root,y,"Birth and childhood in Desert communities. This contradicts the canonical rule: children are removed from kin.")
        cr=triage({"relationship_id":"CAL-CONFLICT","left":x,"right":y},root);cases.append({"name":"true_contradiction","pass":cr["identity"]["same_subject"] and cr["identity"]["same_scope"] and cr["identity"]["authoritative_pair"],"actual":cr["decision"],"expected":"CONFLICT only after explicit evidence gates"})
        h="07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/FAMILY_BIRTH_CHILDHOOD_v0.1.md";write(root,h,"Historical version of Hearth birth and childhood customs.");ih=identify(h);cases.append({"name":"historical_version","pass":ih["role"]=="HISTORICAL","expected":"HISTORICAL layer"})
        u=f"{REGION_ROOT}/DESERT/FAMILY_COMING_OF_AGE.md";write(root,u,"Coming of age ceremonies and childhood transition practices.");iu=identify(u);cases.append({"name":"unrelated_same_topic","pass":iu["subject"]!=ia["subject"],"expected":"identity mismatch / REVIEW or RELATED, never VARIANT"})
    failed=[x for x in cases if not x["pass"]];summary={"cases":len(cases),"passed":len(cases)-len(failed),"failed":len(failed),"names":[x["name"] for x in cases]};print(summary)
    if failed: raise SystemExit("CORE identity calibration failed: "+repr(failed))
if __name__=="__main__":main()
