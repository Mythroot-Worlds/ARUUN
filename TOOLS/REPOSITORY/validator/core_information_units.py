#!/usr/bin/env python3
"""Extract conservative information units for semantic comparison.

This is deliberately broader than relational-verb extraction. It captures
section context and factual prose so equivalent information can be compared
even when documents use different wording and no explicit relationship verb.
It does not decide relationships or modify canon.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

SKIP={'.git','.github','TOOLS','07_ARCHIVE','node_modules','__pycache__'}
HEAD_RE=re.compile(r'^\s{0,3}#{1,6}\s+(.+?)\s*$')

def files(root):
    for p in root.rglob('*.md'):
        if any(x in SKIP for x in p.parts): continue
        yield p

def normalize(text):
    text=re.sub(r'[`*_>#\[\]()]',' ',text.lower())
    text=re.sub(r'\s+',' ',text).strip()
    return text

def units(path):
    try: body=path.read_text(encoding='utf-8',errors='replace')[:160000]
    except Exception:return []
    section='DOCUMENT'
    out=[]
    for line_no,raw in enumerate(body.splitlines(),1):
        s=raw.strip()
        if not s: continue
        hm=HEAD_RE.match(raw)
        if hm:
            section=hm.group(1).strip()
            continue
        if len(s)<30 or s.startswith('|') or s.startswith('```') or s.startswith('---'): continue
        # Keep prose statements and list items; avoid trying to invent entities.
        if not (s.startswith(('-', '*', '+')) or re.search(r'[.!?:;]',s)): continue
        text=re.sub(r'^[-*+]\s+','',s).strip()
        if len(text)<30: continue
        norm=normalize(text)
        if not norm: continue
        out.append({'source':path.as_posix(),'line':line_no,'section':section,'text':text[:1000],'normalized':norm,'fingerprint':hashlib.sha1(norm.encode()).hexdigest()[:16]})
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS'); a=ap.parse_args(); root=Path(a.root).resolve(); out=root/a.out; out.mkdir(parents=True,exist_ok=True)
    all_units=[]
    for p in files(root): all_units.extend(units(p))
    report={'engine':'CORE Information Unit Extraction','schema_version':'1.0','mode':'READ_ONLY','units':all_units,'summary':{'documents_with_units':len({u['source'] for u in all_units}),'information_units':len(all_units)},'safety':{'final_relationship_decision':False,'automatic_canon_change':False,'provenance_required':True}}
    (out/'CORE_INFORMATION_UNITS.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    md=['# CORE Information Units','','Information units capture what prose says before relationship adjudication.','They supplement—not replace—explicit semantic relationship claims.','',f"Documents with units: **{report['summary']['documents_with_units']}**",f"Information units: **{report['summary']['information_units']}**"]
    (out/'CORE_INFORMATION_UNITS.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(f"CORE information units: {len(all_units)} across {report['summary']['documents_with_units']} documents.")
if __name__=='__main__': main()
