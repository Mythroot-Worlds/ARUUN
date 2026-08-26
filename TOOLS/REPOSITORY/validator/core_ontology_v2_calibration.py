#!/usr/bin/env python3
"""Corrected relationship ontology v2 calibration.

This suite deliberately separates legacy/raw human labels from the current
ontology. Raw historical choices remain preserved; they are never silently
promoted into current calibration truth.
"""
from pathlib import Path
from core_document_identity import identify, identity_match
from core_layered_relationship import compare

def read(root,p):
    return (root/p).read_text(encoding='utf-8') if (root/p).exists() else ''

def main():
    root=Path('.')
    cases=[
      ('revision variant','07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/HEARTH_DESERT_PEOPLES_CULTURAL_BASE_v0.1.md','07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/HEARTH_DESERT_PEOPLES_CULTURAL_BASE_v0.2.md','VARIANT'),
      ('regional related','03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md','03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md','RELATED'),
      ('root versus regional','03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md','03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md','RELATED'),
      ('comparative support','03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md','03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md','SUPPORTING'),
    ]
    failed=[]
    for label,a,b,expected in cases:
      result=compare(a,read(root,a),b,read(root,b))
      actual=result['decision']
      print(('PASS' if actual==expected else 'FAIL')+f': {label}: {actual} == {expected}')
      if actual!=expected: failed.append(label)
    unknown='03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md'; desert='03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md'
    im=identity_match(identify(unknown),identify(desert))
    if im['status']!='UNCERTAIN': failed.append('unresolved-vs-known identity must be UNCERTAIN'); print('FAIL: unresolved-vs-known identity')
    else: print('PASS: unresolved-vs-known identity is UNCERTAIN')
    if failed: raise SystemExit('Ontology v2 calibration failed: '+', '.join(failed))
    print('All corrected ontology v2 calibrations passed.')
if __name__=='__main__': main()
