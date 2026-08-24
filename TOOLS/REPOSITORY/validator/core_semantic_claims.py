#!/usr/bin/env python3
"""Extract conservative semantic relationship claims from repository prose.

This layer does not decide final relationships. It finds explicit relational
verbs and nearby context so investigators can reason from language rather than
noun overlap. Claims without enough context remain unresolved candidates.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from core_semantic_library import LIBRARY, CLAIM_FIELDS

SKIP={'.git','.github','TOOLS','07_ARCHIVE','node_modules','__pycache__'}
VERB_MAP={verb.replace('_',' '): ident for ident,data in LIBRARY.items() for verb in data['verb']}
VERB_MAP.update({'supports':'SUPPORTING','supported by':'SUPPORTING','corroborates':'CORROBORATIVE','confirms':'CORROBORATIVE','contradicts':'CONFLICT','supersedes':'HISTORICAL','replaces':'HISTORICAL','derives from':'DERIVED','summarizes':'DERIVED','extends':'COMPLEMENTARY','complements':'COMPLEMENTARY','contextualizes':'COMPLEMENTARY','specializes':'SCOPE_SPECIALIZATION','narrows':'SCOPE_SPECIALIZATION','localizes':'SCOPE_SPECIALIZATION','duplicates':'DUPLICATE','copies':'DUPLICATE'})
PATTERN=re.compile(r'\b('+'|'.join(sorted(map(re.escape,VERB_MAP),key=len,reverse=True))+r')\b',re.I)

def files(root):
    for p in root.rglob('*.md'):
        if any(x in SKIP for x in p.parts): continue
        yield p

def sentence_lines(body):
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+|\n+',body) if x.strip()]

def extract(path):
    try: body=path.read_text(encoding='utf-8',errors='replace')[:120000]
    except Exception:return []
    claims=[]
    for line_no,s in enumerate(sentence_lines(body),1):
        m=PATTERN.search(s)
        if not m: continue
        verb=m.group(1).lower(); ident=VERB_MAP[verb]
        # Conservative: preserve the actual sentence as evidence instead of inventing entities.
        claims.append({'source':path.as_posix(),'line_context':line_no,'relation_identifier':ident,'verb':verb,'subject':None,'object':None,'modifiers':[], 'scope':None,'time':None,'authority':None,'context':s[:600],'evidence_status':'EXPLICIT_VERB_CONTEXT','requires_entity_resolution':True,'provenance':{'source_file':path.as_posix(),'source_line_context':line_no}})
    return claims

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');a=ap.parse_args();root=Path(a.root).resolve();out=root/a.out;out.mkdir(parents=True,exist_ok=True)
    claims=[]
    for p in files(root): claims.extend(extract(p))
    by={k:sum(c['relation_identifier']==k for c in claims) for k in LIBRARY}
    report={'engine':'CORE Semantic Claim Extraction','schema_version':'1.0','mode':'READ_ONLY','claims':claims,'summary':{'documents_with_claims':len({c['source'] for c in claims}),'claims':len(claims),'by_identifier':by,'entity_resolution_required':sum(c['requires_entity_resolution'] for c in claims)},'claim_fields':CLAIM_FIELDS,'safety':{'final_relationship_decision':False,'automatic_canon_change':False,'provenance_required':True}}
    (out/'CORE_SEMANTIC_CLAIMS.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    md=['# CORE Semantic Claim Extraction','','Explicit relational language is evidence, not a final decision.','',f"Claims extracted: **{len(claims)}**",f"Documents with claims: **{report['summary']['documents_with_claims']}**",'','## Descriptor counts']
    for k,n in by.items(): md.append(f'- **{k}**: {n}')
    md += ['','## Rule','- Entity, scope, time, authority, and context must be resolved before a descriptor is accepted.','- `VARIANT` is not a final relationship. Insufficient evidence becomes `UNRESOLVED`.']
    (out/'CORE_SEMANTIC_CLAIMS.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(f"CORE semantic claims: {len(claims)} explicit relational contexts across {report['summary']['documents_with_claims']} documents.")
if __name__=='__main__':main()
