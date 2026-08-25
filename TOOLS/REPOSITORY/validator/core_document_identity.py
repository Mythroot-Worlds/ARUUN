#!/usr/bin/env python3
"""CORE document identity: structural identity before semantic reasoning.

Identity is advisory/read-only. It answers what an artifact is, its subject,
scope, and functional role from path/name/metadata before content similarity
or relationship reasoning is allowed to influence placement or lineage.
"""
from __future__ import annotations
import re
from pathlib import Path

REGIONS=("PLAINS","MOUNTAINS","RIVER","WETLANDS","DESERT","COAST")
STOP={"the","and","for","with","from","that","this","document","regional","family","final","draft","version","comparative","variant","duplicate","supporting","historical","canonical","canon","hearth","region","regions","reference","audit","checklist"}

def subject_from_path(path):
    stem=Path(path).stem.lower()
    stem=re.sub(r"_comparative$|_revision\d*$|_v\d+$|_draft\d*$","",stem)
    parts=[x for x in re.split(r"[^a-z0-9]+",stem) if x and x not in STOP and x.upper() not in REGIONS]
    return "_".join(parts)

def scope_from_path(path):
    parts=[p.upper().replace("-","_") for p in Path(path).parts]
    region=next((r for r in reversed(parts) if r in REGIONS),None)
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

def identify(path):
    scope=scope_from_path(path)
    return {"path":Path(path).as_posix(),"subject":subject_from_path(path),"content_type":content_type(path),"scope":scope,"role":role_from_path(path),"identity_basis":["path","filename"]}

def same_identity(a,b):
    return a["subject"]==b["subject"] and a["content_type"]==b["content_type"] and a["scope"]==b["scope"]
