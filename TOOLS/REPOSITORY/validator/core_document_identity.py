#!/usr/bin/env python3
"""CORE A.C.E. document identity: structural identity before semantic reasoning."""
from __future__ import annotations
import re
from pathlib import Path
from core_document_naming import parse as parse_naming

REGIONS=("PLAINS","MOUNTAINS","RIVER","WETLANDS","DESERT","COAST")
STOP={"the","and","for","with","from","that","this","document","regional","family","final","draft","version","comparative","variant","duplicate","supporting","historical","canonical","canon","hearth","region","regions","reference","audit","checklist"}

def subject_from_path(path):
    stem=Path(path).stem.lower()
    stem=re.sub(r"_comparative$|_revision\d*(?:\.\d+)?$|_v\d+(?:\.\d+)?$|_draft\d*(?:\.\d+)?$","",stem)
    parts=[x for x in re.split(r"[^a-z0-9]+",stem) if x and x not in STOP and x.upper() not in REGIONS]
    return "_".join(parts)

def scope_from_path(path):
    path_obj=Path(path)
    parts=[p.upper().replace("-","_") for p in path_obj.parts]
    region=next((r for r in reversed(parts) if r in REGIONS),None)
    if region is None and path_obj.stem.upper() in REGIONS:
        region=path_obj.stem.upper()
    naming=parse_naming(path)
    if region is None and naming.get('normalized'):
        token=naming.get('scope_token')
        if token in REGIONS: region=token
    continent=None
    if "CONTINENTS" in parts:
        i=parts.index("CONTINENTS")
        if i+1<len(parts): continent=parts[i+1]
    return {"region":region,"continent":continent,"regional_scope":region is not None}

def content_type(path):
    u="/"+Path(path).as_posix().upper()+"/"
    if "/03_PEOPLES/CULTURES/" in u:return "CULTURE"
    if "/01_WORLD/CONTINENTS/" in u or "/01_WORLD/GEOGRAPHY/" in u or "/01_WORLD/HYDROLOGY/" in u:return "GEOGRAPHY"
    if "/02_ECOLOGY/" in u:return "ECOLOGY"
    if "/00_MASTER/" in u:return "MASTER"
    if "/TOOLS/" in u:return "TOOLING"
    return "WORLD_ARTIFACT"

def role_from_path(path):
    u=Path(path).as_posix().upper()
    if any(x in u for x in ("HISTORICAL","ARCHIVE","LEGACY","SUPERSEDED","PREVIOUS")):return "HISTORICAL"
    if any(x in u for x in ("CHECKLIST","AUDIT","FRAMEWORK","GUIDE","REFERENCE","OPERATING_RULES","COMPARATIVE")):return "SUPPORTING"
    return "AUTHORITATIVE"

def identity_layer(path, scope, role, content):
    stem=Path(path).stem.upper()
    if content=="CULTURE" and role=="AUTHORITATIVE":
        if stem in REGIONS or scope.get('region') and Path(path).parent.name.upper() in REGIONS and Path(path).stem.upper() in REGIONS:
            return "CANONICAL_ROOT"
        if scope.get('region'):
            return "REGIONAL_SPECIALIZATION"
        return "CANONICAL_ROOT"
    if role=="SUPPORTING": return "SUPPORTING_ARTIFACT"
    if role=="HISTORICAL": return "HISTORICAL_ARTIFACT"
    return "GENERAL_ARTIFACT"

def identify(path):
    scope=scope_from_path(path)
    content=content_type(path)
    role=role_from_path(path)
    naming=parse_naming(path)
    layer=identity_layer(path,scope,role,content)
    return {"path":Path(path).as_posix(),"subject":subject_from_path(path),"content_type":content,"scope":scope,"role":role,"identity_layer":layer,"naming":naming,"identity_basis":["path","filename","document_naming_status_codes"]}

def same_identity(a,b):
    return a["subject"]==b["subject"] and a["content_type"]==b["content_type"] and a["scope"]==b["scope"]
