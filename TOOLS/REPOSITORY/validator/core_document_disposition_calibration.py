#!/usr/bin/env python3
"""Small regression suite for document-centric disposition routing."""
from core_document_disposition import infer_destination


def ident(content_type, region=None, role='AUTHORITATIVE', lifecycle=None):
    return {'content_type':content_type,'scope':{'region':region,'regional_scope':region is not None},'role':role,'lifecycle_status':lifecycle}


def main():
    cases=[
        ('Desert regional culture','03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md',ident('CULTURE','DESERT'),'RELATED', '03_PEOPLES/CULTURES/HEARTH/DESERT/'),
        ('Coast regional culture','03_PEOPLES/CULTURES/HEARTH/COAST/FAMILY_BIRTH_CHILDHOOD.md',ident('CULTURE','COAST'),'RELATED', '03_PEOPLES/CULTURES/HEARTH/COAST/'),
        ('Comparative support','03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md',ident('CULTURE',None,'SUPPORTING'),'SUPPORTING','03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/'),
        ('Geography must stay geography','01_WORLD/CONTINENTS/HEARTH/REGIONS/SUNSCOUR_OASIS_NETWORK.md',ident('GEOGRAPHY','DESERT'),'RELATED',None),
        ('Historical archive','07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/HEARTH_DESERT_PEOPLES_CULTURAL_BASE_v0.1.md',ident('CULTURE','DESERT','HISTORICAL','HISTORICAL'),'HISTORICAL','07_ARCHIVE/HISTORICAL/'),
    ]
    failed=[]
    for label,path,identity,relationship,expected in cases:
        actual=infer_destination(path,identity,relationship,{})
        ok=actual==expected
        print(f"{'PASS' if ok else 'FAIL'}: {label}: {actual!r} == {expected!r}")
        if not ok: failed.append(label)
    if failed: raise SystemExit('Disposition calibration failed: '+', '.join(failed))

if __name__=='__main__':main()
