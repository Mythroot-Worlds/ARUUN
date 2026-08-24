#!/usr/bin/env python3
"""Mythroot CORE: validate documents against the World Bible layout/schema.

This is intentionally non-file/file-first. It asks what a document is, where it
belongs, what structure it should contain, whether it appears current, and what
canonical constraints it conflicts with. Cross-document comparison is only used
for version/authority checks when necessary.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from collections import Counter

WORLD_BIBLE = Path("00_MASTER/WORLD_BIBLE.md")
EXCLUDED = {".git", "REPORTS", "__pycache__"}
ARCHIVE_MARKERS = ("ARCHIVE", "HISTORICAL", "RETIRED", "SUPERSEDED")
CANON_MARKERS = ("LOCKED CANON", "FLEXIBLE / PROVISIONAL", "OPEN", "UNKNOWN", "WORKING INFERENCE", "RETIRED")
ROLE_RULES = [
    ("00_MASTER", "master_world", "master/world-level", ("WORLD_BIBLE", "WORLD_STATUS", "MASTER")),
    ("01_FOUNDATION", "foundation", "world-foundation", ("FOUNDATION", "PLANET", "TECTONIC", "CLIMATE", "OCEAN")),
    ("02_GEOGRAPHY", "geography", "geography", ("MAP", "GEOGRAPH", "CLIMATE", "OCEAN", "REGION", "CONTINENT")),
    ("03_PEOPLES", "peoples", "people/culture", ("PEOPLE", "CULTURE", "FAMILY", "GOVERNANCE", "LANGUAGE", "FOOD", "CHILD", "KIN", "HOUSE")),
    ("04_ECOLOGY", "ecology", "ecology", ("FAUNA", "FLORA", "ECOLOG", "CREATURE", "PLANT", "ANIMAL", "BIOME")),
    ("05_CULTURE", "culture", "culture", ("CULTURE", "CUSTOM", "BELIEF", "RITUAL", "MATERIAL", "SOCIAL")),
    ("06_HISTORY", "history", "history", ("HISTORY", "TIMELINE", "ERA", "EVENT", "HISTOR")),
    ("07_ARCHIVE", "archive", "historical/archive", ("ARCHIVE", "HISTORICAL", "RETIRED", "SUPERSEDED")),
]
EXPECTED_HEARTH = {
    "FAMILY_BIRTH_CHILDHOOD": ("family/childhood", ("FAMILY", "BIRTH", "CHILD", "KIN", "PARENT", "CARE")),
    "FAMILY_PARTNERSHIP": ("family/partnership", ("FAMILY", "PARTNER", "MARRIAGE", "KIN", "HOUSEHOLD")),
    "GOVERNANCE_AND_AUTHORITY": ("governance/authority", ("GOVERNANCE", "AUTHORITY", "LEADER", "LEADERSHIP", "COUNCIL", "HOUSE")),
    "CULTURAL_AUDIT_CHECKLIST": ("audit/checklist", ("AUDIT", "CHECKLIST", "CANON", "MISSING", "CONFLICT")),
    "PLAINS": ("regional cultural entry", ("PLAINS", "REGION", "PEOPLE", "CULTURE")),
    "MOUNTAINS": ("regional cultural entry", ("MOUNTAIN", "REGION", "PEOPLE", "CULTURE")),
    "RIVER": ("regional cultural entry", ("RIVER", "REGION", "PEOPLE", "CULTURE")),
    "WETLANDS": ("regional cultural entry", ("WETLAND", "REGION", "PEOPLE", "CULTURE")),
    "DESERT": ("regional cultural entry", ("DESERT", "REGION", "PEOPLE", "CULTURE")),
    "COAST": ("regional cultural entry", ("COAST", "REGION", "PEOPLE", "CULTURE")),
}

def text(path, root):
    try: return (root / path).read_text(encoding="utf-8", errors="replace")[:120000]
    except Exception: return ""

def markdown_files(root):
    out=[]
    for p in root.rglob("*.md"):
        if any(x in EXCLUDED for x in p.parts): continue
        out.append(p.relative_to(root).as_posix())
    return sorted(out)

def headings(body):
    return [re.sub(r"^#+\s*", "", x).strip() for x in body.splitlines() if re.match(r"^#{1,6}\s+", x)]

def world_bible_categories(body): return headings(body)

def role_for(path):
    parts=path.split("/")
    for prefix, role, label, _ in ROLE_RULES:
        if parts and parts[0] == prefix: return role, label
    return "unmapped", "unmapped"

def filename_type(path):
    stem=Path(path).stem.upper()
    if stem in {"WORLD_BIBLE", "WORLD_STATUS"}: return "master_world"
    if "CHECKLIST" in stem or "AUDIT" in stem: return "audit_reference"
    if any(x in stem for x in ("REVISION", "WORKING", "DRAFT")): return "working_document"
    if any(x in stem for x in ("HISTORY", "TIMELINE", "ERA")): return "historical_or_timeline"
    if any(x in stem for x in ("FAMILY", "GOVERNANCE", "AUTHORITY", "LANGUAGE", "CULTURE", "PEOPLE", "CHILD")): return "domain_reference"
    if stem in {"PLAINS","MOUNTAINS","RIVER","WETLANDS","DESERT","COAST"}: return "regional_culture"
    return "reference_document"

def version(path, body):
    # Versions are decimal semantic values (e.g. v1.5), not integers.
    mentions=re.findall(r"\bv(\d+(?:\.\d+)?)\b", body, re.I)
    mentions += re.findall(r"[_ -]v(\d+(?:\.\d+)?)\b", path, re.I)
    versions=[]
    for raw in mentions:
        try: versions.append(float(raw))
        except ValueError: continue
    m=re.search(r"(?:VERSION|REVISION|RELEASE)\s*[:#]?\s*v?(\d+(?:\.\d+)?)", body, re.I)
    declared=float(m.group(1)) if m else (max(versions) if versions else None)
    archived=any(x in path.upper().split("/") for x in ARCHIVE_MARKERS)
    return {"declared_version":declared,"version_mentions":versions,"archived_path":archived}

def canonical_status(body):
    u=body.upper(); hits=[marker for marker in CANON_MARKERS if marker in u]
    line=next((x.strip() for x in body.splitlines() if "STATUS:" in x.upper()), "")
    return {"markers":hits,"status_line":line}

def expected_terms(path, role):
    stem=Path(path).stem.upper()
    if "03_PEOPLES/CULTURES/HEARTH" in path and stem in EXPECTED_HEARTH:
        label, terms=EXPECTED_HEARTH[stem]; return label, terms
    for prefix, _, label, terms in ROLE_RULES:
        if role != "unmapped" and path.startswith(prefix+"/"): return label, terms
    return role, ()

def assess(path, root, bible_categories):
    body=text(path,root); role,label=role_for(path); ftype=filename_type(path); ver=version(path,body); status=canonical_status(body); expected_label,terms=expected_terms(path,role); u=body.upper()
    present=[t for t in terms if t in u]; missing=[] if not terms else [t for t in terms if t not in u]
    proper_location=role != "unmapped" and not ver["archived_path"]
    if role == "archive": proper_location=True
    structure_score=(len(present)/len(terms)) if terms else 1.0
    flags=[]
    if role == "unmapped": flags.append("UNMAPPED_LOCATION")
    if ver["archived_path"] and role != "archive": flags.append("ARCHIVE_PATH_ROLE_MISMATCH")
    if structure_score < 0.25 and terms: flags.append("LOW_SCHEMA_SIGNAL")
    if not body.strip(): flags.append("EMPTY_DOCUMENT")
    if ftype == "working_document" and role in {"master_world","peoples","ecology","culture","history"}: flags.append("WORKING_FILE_IN_AUTHORITATIVE_AREA")
    return {"path":path,"file_type":ftype,"role":role,"expected_category":expected_label,"proper_location":proper_location,"version":ver,"canonical_status":status,"world_bible_category_candidates":bible_categories[:50],"schema_signal":{"matched":present,"missing":missing,"coverage":round(structure_score,3)},"conflicts":flags,"comparison_mode":"DOCUMENT_TO_WORLD_BIBLE_SCHEMA","cross_file_comparison_used":False,"provenance":{"source":"repository_file","world_bible":"00_MASTER/WORLD_BIBLE.md"}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",default="."); ap.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS"); x=ap.parse_args()
    root=Path(x.root).resolve(); out=root/x.out; out.mkdir(parents=True,exist_ok=True)
    bible=text("00_MASTER/WORLD_BIBLE.md",root); cats=world_bible_categories(bible)
    docs=markdown_files(root); rows=[assess(p,root,cats) for p in docs]
    counts=Counter(r["file_type"] for r in rows)
    report={"engine":"CORE Mythroot World Bible Layout Engine","schema_version":"1.0","mode":"READ_ONLY","comparison_mode":"DOCUMENT_TO_WORLD_BIBLE_SCHEMA","world_bible":{"path":"00_MASTER/WORLD_BIBLE.md","status":"current authoritative World Bible for development"},"summary":{"documents":len(rows),"proper_location":sum(r["proper_location"] for r in rows),"unmapped":sum(r["role"]=="unmapped" for r in rows),"low_schema_signal":sum("LOW_SCHEMA_SIGNAL" in r["conflicts"] for r in rows),"conflict_flags":sum(len(r["conflicts"]) for r in rows),"file_types":dict(counts)},"documents":rows,"safety":{"read_only":True,"automatic_canon_change":False,"automatic_rule_promotion":False,"file_file_comparison_primary":False}}
    (out/"CORE_WORLD_BIBLE_LAYOUT_REPORT.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    md=['# CORE World Bible Layout Report','',f"Documents: {len(rows)}",f"Proper location: {report['summary']['proper_location']}",f"Unmapped: {report['summary']['unmapped']}",f"Low schema signal: {report['summary']['low_schema_signal']}",'','## Flags']
    for r in rows:
        if r['conflicts']: md.append(f"- **{r['path']}** — {', '.join(r['conflicts'])}")
    (out/"CORE_WORLD_BIBLE_LAYOUT_REPORT.md").write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps(report['summary'],indent=2))

if __name__ == "__main__": main()
