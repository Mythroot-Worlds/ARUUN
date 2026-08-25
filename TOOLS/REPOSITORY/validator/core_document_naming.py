#!/usr/bin/env python3
"""CORE parser for the canonical Document Naming & Status Codes rules."""
from __future__ import annotations
import re
from pathlib import Path

STATUS_CODES={
    'C':'CANON',
    'P':'PROVISIONAL',
    'O':'OPEN',
    'X':'CONFLICTED',
    'D':'DEPRECATED',
}
STATUS_NAMES={v:k for k,v in STATUS_CODES.items()}
REGIONS={'PLAINS','MOUNTAINS','RIVER','WETLANDS','DESERT','COAST'}

# Canon form: [SCOPE]_[SUBJECT]_[STATUS]-[ID].md
PATTERN=re.compile(r'^(?P<scope>[A-Z][A-Z0-9_-]*)_(?P<subject>[A-Z0-9][A-Z0-9_-]*)_(?P<status>[CPOXD])-(?P<id>[A-Z0-9][A-Z0-9_-]*)$')

def parse(path):
    stem=Path(path).stem.upper()
    m=PATTERN.fullmatch(stem)
    if not m:
        return {'normalized':False,'status_code':None,'status_name':None,'scope_token':None,'subject_token':None,'record_id':None,'basis':'legacy_or_unstructured_filename'}
    status=m.group('status')
    return {'normalized':True,'status_code':status,'status_name':STATUS_CODES[status],'scope_token':m.group('scope'),'subject_token':m.group('subject'),'record_id':m.group('id'),'basis':'document_naming_status_codes'}

def status_for_role(role,lifecycle=None):
    if role=='HISTORICAL' or lifecycle in {'ARCHIVE','HISTORICAL'}:
        return 'D','DEPRECATED'
    if role=='SUPPORTING':
        return None,None
    return 'C','CANON'

def expected_scope_token(scope):
    region=(scope or {}).get('region')
    if isinstance(region,str) and region.upper() in REGIONS:
        return region.upper()
    return 'HEARTH'
