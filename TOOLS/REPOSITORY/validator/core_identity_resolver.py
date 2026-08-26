#!/usr/bin/env python3
"""CORE identity resolver: structural identity before semantic comparison."""
from __future__ import annotations
import re
from pathlib import Path

REGIONS={"HEARTH","PLAINS","MOUNTAINS","RIVER","WETLANDS","DESERT","COAST"}

def normalize_name(value):
    return re.sub(r"[^a-z0-9]+","_",value.lower()).strip("_") if value else None

def _front_context(path):
    try: body=path.read_text(encoding="utf-8",errors="replace")[:30000]
    except Exception: return {}
    out={}
    for line in body.splitlines()[:120]:
        m=re.match(r"^\s*[-#]*\s*(subject|scope|population|region|subregion|entity|purpose|role|document\s*role|type)\s*[:=-]\s*(.+?)\s*$",line,re.I)
        if not m: continue
        key=re.sub(r"\s+","_",m.group(1).lower())
        if key in ("document_role","type"): key="role"
        out[key]=m.group(2).strip()
    return out

def resolve_identity(root, rel):
    path=Path(rel); parts=[p.upper() for p in path.parts]; stem=path.stem.upper()
    entity=None; region=None; subregion=None
    if "HEARTH" in parts:
        entity="HEARTH"; i=parts.index("HEARTH")
        if i+1<len(parts) and parts[i+1] in REGIONS:
            region=parts[i+1]
            if i+2<len(parts) and parts[i+2] != path.name.upper(): subregion=parts[i+2]
    subject=normalize_name(re.sub(r"_V\d+(?:\.\d+)?$","",stem))
    role=subject
    if "SPECIALIST_HOUSES" in stem: role="specialist_houses"
    elif "SPECIALIST_LINEAGES" in stem: role="specialist_lineages"
    elif "GOVERNANCE" in stem: role="governance_authority"
    elif "PARTNERSHIP" in stem: role="family_partnership"
    elif "BIRTH_CHILDHOOD" in stem: role="family_birth_childhood"
    elif "AUDIT" in stem or "CHECKLIST" in stem: role="audit_support"
    purpose=role
    front=_front_context(root/path)
    if front.get("subject"): subject=normalize_name(front["subject"])
    if front.get("role"): role=normalize_name(front["role"])
    if front.get("purpose"): purpose=normalize_name(front["purpose"])
    if front.get("region"):
        fr=normalize_name(front["region"]).upper()
        if fr in REGIONS: region=fr
    if front.get("scope"):
        fs=normalize_name(front["scope"]).upper()
        if fs in REGIONS: region=fs
        elif fs in {"HEARTH_WIDE","HEARTH","WORLD","GLOBAL"}: region=None
    if front.get("subregion"): subregion=normalize_name(front["subregion"])
    population=region
    scope=region
    return {"entity":entity,"population":population,"region":region,"subregion":subregion,"subject":subject,"role":role,"purpose":purpose,"scope":scope,
            "identity_confidence": "HIGH" if region or entity or front.get("subject") else "MEDIUM",
            "identity_source": "frontmatter" if front else "path"}

def identity_match(left,right):
    """Return (same_identity, reasons). Missing structural identity is uncertain, never agreement."""
    reasons=[]; uncertain=[]
    for key,label in (("entity","entity"),("population","population"),("region","region"),("subregion","subregion"),("subject","subject"),("role","document role"),("purpose","purpose")):
        a,b=left.get(key),right.get(key)
        if a is not None and b is not None and a!=b: reasons.append(f"{label} mismatch: {a} != {b}")
        elif a is None or b is None: uncertain.append(f"{label} unresolved")
    if left.get("region") and right.get("region") and left["region"]!=right["region"]: reasons.append("regional scope mismatch")
    if reasons: return (False,reasons)
    if uncertain: return (False,[*uncertain,"identity uncertain: missing structural field cannot be treated as agreement"])
    return (True,[])
