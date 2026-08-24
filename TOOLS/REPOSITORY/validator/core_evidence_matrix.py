#!/usr/bin/env python3
"""CORE A.C.E. evidence matrix: multi-dimensional relationship reasoning."""
from __future__ import annotations
import argparse,json
from pathlib import Path

def load(p,d):
 try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
 except:return d

def read(path,root):
 p=root/path if path else None
 try:return p.read_text(encoding='utf-8')[:50000].upper() if p and p.exists() else ''
 except:return ''

def scope(s):
 if any(x in s for x in ['CONTINENT','CONTINENTAL','HEARTH-WIDE','ALL PEOPLES']): return 'BROAD'
 if any(x in s for x in ['SETTLEMENT','VILLAGE','LOCAL','HOUSE','NARROW']): return 'NARROW'
 if any(x in s for x in ['MOUNTAIN','RIVER','WETLAND','COAST','PLAINS','DESERT','REGIONAL','REGION']): return 'REGIONAL'
 return 'UNKNOWN'

def funcs(s):
 groups={'FAMILY':['FAMILY','BIRTH','CHILDHOOD','MARRIAGE','KIN','HOUSEHOLD'],'GOVERNANCE':['GOVERNANCE','AUTHORITY','LEADERSHIP','COUNCIL','LEADER','HEAD'],'SPECIALIST':['SPECIALIST','LINEAGE','HOUSE','CRAFT','KEEPER'],'SUPPORT':['CHECKLIST','AUDIT','REFERENCE','FRAMEWORK','GUIDE'],'HISTORICAL':['HISTORICAL','ARCHIVE','REVISION','FORMER','OBSOLETE']}
 return sorted(k for k,ws in groups.items() if any(w in s for w in ws))

def matrix(a,b):
 sa,sb=scope(a),scope(b);fa,fb=set(funcs(a)),set(funcs(b)); rel='SAME' if sa==sb else ('BROAD_TO_REGIONAL' if {sa,sb}=={'BROAD','REGIONAL'} else ('REGIONAL_TO_NARROW' if {sa,sb}=={'REGIONAL','NARROW'} else 'DIFFERENT'))
 return {'scope_a':sa,'scope_b':sb,'scope_relation':rel,'function_a':sorted(fa),'function_b':sorted(fb),'function_overlap':sorted(fa&fb),'function_difference':sorted(fa^fb)}

def classify(m,prior):
 if m['function_overlap'] and m['scope_relation'] in {'BROAD_TO_REGIONAL','REGIONAL_TO_NARROW'}: return 'VARIANT'
 if ('SUPPORT' in m['function_a'] or 'SUPPORT' in m['function_b']) and not m['function_overlap']: return 'SUPPORTING'
 if ('HISTORICAL' in m['function_a'] or 'HISTORICAL' in m['function_b']) and not m['function_overlap']: return 'HISTORICAL'
 if m['scope_relation']=='SAME' and m['function_a']==m['function_b']: return 'DUPLICATE'
 return prior if prior in {'DUPLICATE','VARIANT','SUPPORTING','HISTORICAL','COINCIDENTAL','MISPLACED','CONFLICT','RELATED','REVIEW'} else 'RELATED'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out;blind=load(out/'CORE_BLIND_TEST.json',{'predictions':[]});res=[]
 for r in blind.get('predictions',[]):
  a=read(r.get('left'),root)+' '+r.get('left','').upper();b=read(r.get('right'),root)+' '+r.get('right','').upper();m=matrix(a,b);pred=classify(m,r.get('predicted_classification','RELATED'));res.append({'relationship_id':r.get('relationship_id'),'matrix':m,'matrix_prediction':pred,'prior_prediction':r.get('predicted_classification'),'changed':pred!=r.get('predicted_classification')})
 report={'engine':'CORE A.C.E. Evidence Matrix','mode':'READ_ONLY','predictions':res,'summary':{'holdouts':len(res),'changed':sum(x['changed'] for x in res),'distinct_predictions':len(set(x['matrix_prediction'] for x in res)),'safety':{'automatic_rule_promotion':False,'automatic_canon_change':False,'human_validation_required':True}}}
 (out/'CORE_EVIDENCE_MATRIX.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(out/'CORE_EVIDENCE_MATRIX.md').write_text('# CORE A.C.E. Evidence Matrix\n\nMulti-dimensional scope/function comparison layered over precedent retrieval.\n\n'+f"Holdouts: **{len(res)}**\nChanged predictions: **{report['summary']['changed']}**\nDistinct predictions: **{report['summary']['distinct_predictions']}**\n",encoding='utf-8');print(f"Evidence matrix: {len(res)} holdouts; {report['summary']['changed']} changed; {report['summary']['distinct_predictions']} distinct predictions.")
if __name__=='__main__':main()
