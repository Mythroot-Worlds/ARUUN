#!/usr/bin/env python3
"""Regression suite for document-centric disposition and naming/status rules."""
from core_document_disposition import infer_destination
from core_document_identity import identify
from core_document_naming import parse

def ident(content_type,region=None,role='AUTHORITATIVE',lifecycle=None,layer=None):
    d={'content_type':content_type,'scope':{'region':region,'regional_scope':region is not None},'role':role,'lifecycle_status':lifecycle}
    if layer:d['identity_layer']=layer
    return d

def main():
    cases=[
        ('Hearth canonical root','03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md',ident('CULTURE',None,layer='CANONICAL_ROOT'),'RELATED','03_PEOPLES/CULTURES/HEARTH/'),
        ('Desert regional culture','03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md',ident('CULTURE','DESERT',layer='REGIONAL_SPECIALIZATION'),'RELATED','03_PEOPLES/CULTURES/HEARTH/DESERT/'),
        ('Coast regional culture','03_PEOPLES/CULTURES/HEARTH/COAST/FAMILY_BIRTH_CHILDHOOD.md',ident('CULTURE','COAST',layer='REGIONAL_SPECIALIZATION'),'RELATED','03_PEOPLES/CULTURES/HEARTH/COAST/'),
        ('Flat Coast regional root','03_PEOPLES/CULTURES/HEARTH/COAST.md',ident('CULTURE','COAST',layer='CANONICAL_ROOT'),'RELATED','03_PEOPLES/CULTURES/HEARTH/COAST/'),
        ('Comparative support','03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md',ident('CULTURE',None,'SUPPORTING'),'SUPPORTING','03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/'),
        ('Geography must stay geography','01_WORLD/CONTINENTS/HEARTH/REGIONS/SUNSCOUR_OASIS_NETWORK.md',ident('GEOGRAPHY','DESERT'),'RELATED',None),
        ('Historical archive','07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/HEARTH_DESERT_PEOPLES_CULTURAL_BASE_v0.1.md',ident('CULTURE','DESERT','HISTORICAL','HISTORICAL'),'HISTORICAL','07_ARCHIVE/HISTORICAL/'),
    ]
    failed=[]
    for label,path,identity,relationship,expected in cases:
        actual=infer_destination(path,identity,relationship,{})
        ok=actual==expected
        print(f"{'PASS' if ok else 'FAIL'}: {label}: {actual!r} == {expected!r}")
        if not ok:failed.append(label)
    naming=[
        ('RIVER_FAMILY_C-0001.md','C','CANON','RIVER','FAMILY','0001'),
        ('RIVER_BELIEF_P-0001.md','P','PROVISIONAL','RIVER','BELIEF','0001'),
        ('RIVER_SETTLEMENTS_O-0001.md','O','OPEN','RIVER','SETTLEMENTS','0001'),
        ('RIVER_FAMILY_X-0001.md','X','CONFLICTED','RIVER','FAMILY','0001'),
        ('RIVER_FAMILY_D-0001.md','D','DEPRECATED','RIVER','FAMILY','0001'),
    ]
    for filename,code,name,scope,subject,rid in naming:
        got=parse(filename);ok=got['normalized'] and got['status_code']==code and got['status_name']==name and got['scope_token']==scope and got['subject_token']==subject and got['record_id']==rid
        print(f"{'PASS' if ok else 'FAIL'}: naming {filename}")
        if not ok:failed.append('naming '+filename)
    legacy=identify('03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md')
    if legacy['naming']['normalized']:
        failed.append('legacy existing filename incorrectly treated as normalized')
        print('FAIL: legacy existing filename incorrectly treated as normalized')
    else:print('PASS: legacy existing filename remains legacy until intentional normalization')
    if failed:raise SystemExit('Disposition/naming calibration failed: '+', '.join(failed))
    print('All disposition and naming calibrations passed.')

if __name__=='__main__':main()
