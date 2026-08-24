#!/usr/bin/env python3
"""ARUUN read-only canonical assembly review.

Consumes CONTENT_LINEAGE_REPORT.json and creates a provenance-preserving
assembly packet. It proposes structure; it never selects canon or changes
source documents.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--report',default='TOOLS/REPOSITORY/REPORTS/CONTENT_LINEAGE_REPORT.json');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');a=ap.parse_args();root=Path(a.root).resolve(); data=json.loads((root/a.report).read_text(encoding='utf-8'))
 assemblies=[]
 for c in data.get('clusters_detail',[]):
  units=[]
  for cmp in c.get('comparisons',[]):
   for section,r in cmp.get('unit_analysis',{}).items():
    for x in r.get('shared_units',[]): units.append({'type':x['status'],'section':section,'sources':[cmp['a'],cmp['b']],'text_a':x['a'],'text_b':x['b'],'decision':'UNRESOLVED'})
    for x in r.get('unique_to_a',[]): units.append({'type':'SOURCE_SPECIFIC','section':section,'sources':[cmp['a']],'text':x,'decision':'UNRESOLVED'})
    for x in r.get('unique_to_b',[]): units.append({'type':'SOURCE_SPECIFIC','section':section,'sources':[cmp['b']],'text':x,'decision':'UNRESOLVED'})
    for x in r.get('possible_conflicts',[]): units.append({'type':'POSSIBLE_CONFLICT','section':section,'sources':[cmp['a'],cmp['b']],'text_a':x['a'],'text_b':x['b'],'decision':'UNRESOLVED'})
  assemblies.append({'subject':c['subject'],'status':'REVIEW_REQUIRED','sources':[x['path'] for x in c['documents']],'proposed_units':units})
 out=root/a.out;out.mkdir(parents=True,exist_ok=True); result={'mode':'READ_ONLY','rule':'PROPOSE ONLY — HUMAN CANON DECISION REQUIRED','assemblies':assemblies};(out/'CANONICAL_ASSEMBLY_REVIEW.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 lines=['# ARUUN Canonical Assembly Review','','**Mode:** READ-ONLY','','This is a provenance-preserving proposal. It does not establish canon and does not modify source documents.','','Allowed human decisions: `KEEP`, `MERGE`, `MOVE`, `LINK`, `ARCHIVE`, `UNRESOLVED`','']
 for c in assemblies:
  lines += [f"## {c['subject']}",f"**Status:** {c['status']}","","### Sources"]+[f"- `{s}`" for s in c['sources']]+["","### Proposed Information Units"]
  for i,u in enumerate(c['proposed_units'],1):
   lines += [f"#### {i}. {u['type']}",f"- **Section:** `{u['section']}`",f"- **Sources:** {', '.join('`'+s+'`' for s in u['sources'])}",f"- **Decision:** `{u['decision']}`"]
   if 'text' in u: lines.append(f"- **Contribution:** {u['text']}")
   if 'text_a' in u: lines += [f"- **First:** {u['text_a']}",f"- **Second:** {u['text_b']}"]
   lines.append('')
 (out/'CANONICAL_ASSEMBLY_REVIEW.md').write_text('\n'.join(lines),encoding='utf-8');print(f'Built {len(assemblies)} canonical assembly review packet(s).')
if __name__=='__main__':main()
