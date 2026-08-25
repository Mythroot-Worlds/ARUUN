#!/usr/bin/env python3
"""CORE A.C.E. Robin: independent deciding-factor investigator.

Robin builds a complete factor matrix. Path identity is structural evidence:
subject identity is normalized from the artifact name, while regional scope is
resolved from the containing region path before language evidence is considered.
Robin never decides the final relationship.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from core_deciding_factor_questions import QUESTIONS

MAX_WINDOW=3
RELATIONS={
    'subject':['same','different','subject','about','describes','concerns'],
    'scope':['continent','regional','region','settlement','village','local','hearth','mountain','river','plains','wetlands','desert','coast'],
    'scale':['personal','local','regional','national','political','global','cosmic','hearth-wide'],
    'function':['family','birth','childhood','governance','authority','leadership','specialist','lineage','support','checklist','audit','reference','historical','archive','revision'],
    'depth':['level 0','level 1','level 2','level 3','level 4','foundation','functional','developed','deep'],
    'canon_status':['hard canon','flexible canon','open','unknown','canon'],
    'importance':['core','supporting','optional'],
    'development_state':['developed','partial','open','n/a'],
    'relationship':['related','variant','supporting','historical','conflict','misplaced','duplicate','coincidental','review'],
    'dependency':['based on','builds on','derived from','references','informs'],
    'consequence':['affects','influences','consequence','impacts'],
    'provenance':['source','provenance','author','version','last reviewed'],
    'intentionality':['intentionally open','deliberately open','creator-expandable','unexplored','withheld'],
    'coherence':['geography','settlement','economy','politics','law','history','culture','daily life','ecology'],
    'usability':['usability','creator-ready','license-ready','world usage guide'],
    'story_relevance':['story','conflict','mystery','story opportunity','narrative','story generation'],
}
PATH_HINTS={
    'scope':['REGIONS','PLAINS','MOUNTAINS','RIVER','WETLANDS','DESERT','COAST','HEARTH','CONTINENTS','WORLD'],
    'function':['FAMILY','BIRTH','CHILDHOOD','GOVERNANCE','AUTHORITY','PARTNERSHIP','FOOD','SUBSISTENCE','SETTLEMENT','HOUSING','CULTURE','CHECKLIST','AUDIT','REFERENCE'],
    'depth':['LEVEL_0','LEVEL_1','LEVEL_2','LEVEL_3','LEVEL_4'],
    'canon_status':['CANON','ARCHIVE','HISTORICAL','DRAFT'],
    'importance':['CORE','SUPPORTING','OPTIONAL'],
    'development_state':['DEVELOPED','PARTIAL','OPEN'],
    'relationship':['COMPARATIVE','VARIANT','DUPLICATE','SUPPORTING','HISTORICAL'],
}
REGION_ALIASES={'PLAINS':'PLAINS','MOUNTAINS':'MOUNTAINS','RIVER':'RIVER','RIVERLANDS':'RIVER','WETLANDS':'WETLANDS','DESERT':'DESERT','COAST':'COAST'}
STOP={'family','regional','document','draft','final','version','comparative','variant','duplicate','supporting','historical','canonical','canon','hearth','region','regions','the','and','for','with'}

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def read(path,root,limit=60000):
    try:return (root/path).read_text(encoding='utf-8')[:limit]
    except:return ''

def sentences(text):return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+',text) if s.strip()]

def relation_hits(sentence,dimension):
    u=sentence.lower();return [w for w in RELATIONS.get(dimension,[]) if re.search(r'\b'+re.escape(w)+r'\w*\b',u)]

def named_spans(sentence):
    vals=[]
    for m in re.finditer(r'\b([A-Z][A-Za-z0-9_-]{2,}(?:\s+[A-Z][A-Za-z0-9_-]{2,}){0,4})\b',sentence):
        v=m.group(1).strip(' .,;:()[]')
        if v not in vals and v.upper() not in {'THE','THIS','THAT','WHICH','DOCUMENT','SOURCE','CURRENT','FORMER'}:vals.append(v)
    return vals[:10]

def local_analysis(path,root,dimension):
    ss=sentences(read(path,root));out=[]
    for i,s in enumerate(ss):
        hits=relation_hits(s,dimension)
        if not hits:continue
        lo=max(0,i-MAX_WINDOW);hi=min(len(ss),i+MAX_WINDOW+1);window=ss[lo:hi];entities=named_spans(s)
        syntax_signal=bool(re.search(r'\b(?:is|are|has|have|governs?|rules?|leads?|supports?|informs?|derives?|replaces?|supersedes?|belongs?|contains?|within|under|from|for|differs?|same)\b',s,re.I))
        out.append({'source':path,'dimension':dimension,'sentence':s,'window':window,'relation_terms':hits,'entities':entities,'syntax_signal':syntax_signal,'subject_candidate':entities[0] if entities else None,'object_candidates':entities[1:] if len(entities)>1 else [],'relation_candidate':hits[0],'context_depth':len(window)})
    return out[:12]

def path_evidence(path,dimension):
    u=path.upper();return [h.lower() for h in PATH_HINTS.get(dimension,[]) if h in u]

def normalize_subject(path):
    stem=Path(path).stem.lower()
    tokens=[x for x in re.split(r'[^a-z0-9]+',stem) if x and x not in STOP and x not in REGION_ALIASES]
    return '_'.join(tokens)

def region_from_path(path):
    parts=[x.upper().replace('-','_') for x in Path(path).parts]
    for p in reversed(parts):
        for alias,region in REGION_ALIASES.items():
            if alias in p:return region
    return None

def identity_evidence(path,dimension):
    if dimension=='subject':return {'value':normalize_subject(path),'source':'filename_identity','confidence':0.95}
    if dimension=='scope':
        r=region_from_path(path);return {'value':r,'source':'region_path' if r else 'unresolved','confidence':0.98 if r else 0.0}
    return {'value':None,'source':'not_structural','confidence':0.0}

def lexical_evidence(text,dimension):
    u=text.lower();return sorted({w for w in RELATIONS.get(dimension,[]) if re.search(r'\b'+re.escape(w)+r'\w*\b',u)})

def document_factor(path,root,dimension):
    text=read(path,root);local=local_analysis(path,root,dimension);ph=path_evidence(path,dimension);lh=lexical_evidence(text,dimension);struct=identity_evidence(path,dimension);terms=sorted(set(ph+lh));explicit=[x for x in local if x['syntax_signal']];score=min(1.0,(len(terms)*.12)+(len(explicit)*.08))
    return {'path':path,'dimension':dimension,'evidence_terms':terms,'path_evidence':ph,'language_evidence':lh,'identity_evidence':struct,'observations':local[:8],'evidence_count':len(local),'explicit_relation_count':len(explicit),'presence':'PRESENT' if terms else 'ABSENT','evidence_strength':round(max(score,struct['confidence']),3) if struct['value'] else round(score,3)}

def compare_factor(a,b,dimension,root):
    left=document_factor(a,root,dimension);right=document_factor(b,root,dimension);lv=left['identity_evidence']['value'];rv=right['identity_evidence']['value']
    if dimension in {'subject','scope'} and lv is not None and rv is not None:
        shared=[lv] if lv==rv else [];different=[] if lv==rv else [f'{lv} != {rv}'];state='SAME' if lv==rv else 'DIFFERENT'
    else:
        ls=set(left['evidence_terms']);rs=set(right['evidence_terms']);shared=sorted(ls&rs);different=sorted(ls^rs)
        if not ls and not rs:state='UNKNOWN'
        elif shared and not different:state='SAME'
        elif shared and different:state='MIXED'
        else:state='DIFFERENT'
    deciding=state in {'DIFFERENT','MIXED'}
    return {'dimension':dimension,'question':QUESTIONS[dimension],'left':left,'right':right,'shared_evidence':shared,'differing_evidence':different,'relationship_state':state,'deciding_factor':deciding,'why_it_matters':'Structural identity and scope are resolved from artifact location/name first; language evidence explains content differences but does not redefine identity.','needs_batman_attention':deciding or state=='UNKNOWN'}

def robin_case(case,root):
    a,b=case.get('left',''),case.get('right','');matrix={d:compare_factor(a,b,d,root) for d in QUESTIONS};deciding=[d for d,v in matrix.items() if v['deciding_factor']];unknown=[d for d,v in matrix.items() if v['relationship_state']=='UNKNOWN'];same=[d for d,v in matrix.items() if v['relationship_state']=='SAME'];mixed=[d for d,v in matrix.items() if v['relationship_state']=='MIXED'];different=[d for d,v in matrix.items() if v['relationship_state']=='DIFFERENT']
    return {'relationship_id':case.get('relationship_id'),'documents':{'a':a,'b':b},'robin_results':{d:{'question':v['question'],'relationship_state':v['relationship_state'],'deciding_factor':v['deciding_factor'],'needs_batman_attention':v['needs_batman_attention'],'shared_evidence':v['shared_evidence'],'differing_evidence':v['differing_evidence'],'evidence_strength':{'left':v['left']['evidence_strength'],'right':v['right']['evidence_strength']},'identity_evidence':{'left':v['left']['identity_evidence'],'right':v['right']['identity_evidence']}} for d,v in matrix.items()},'factor_matrix':matrix,'summary':{'factor_dimensions':len(matrix),'same_dimensions':same,'mixed_dimensions':mixed,'different_dimensions':different,'unknown_dimensions':unknown,'deciding_factor_dimensions':deciding,'deciding_factor_count':len(deciding)},'observations':[o for v in matrix.values() for o in v['left']['observations']+v['right']['observations']],'method':'complete deciding-factor matrix with structural subject identity and region scope resolved before language evidence','role':'factor_investigator','independence':'Robin does not consume Batman conclusions; it investigates source text independently'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out;queue=load(out/'CORE_ADJUDICATION_QUEUE.json',{'queue':[]});cases=[robin_case(c,root) for c in queue.get('queue',[])]
    summary={'cases':len(cases),'factor_dimensions':len(QUESTIONS),'matrix_cells':len(cases)*len(QUESTIONS),'cases_with_deciding_factors':sum(bool(c['summary']['deciding_factor_dimensions']) for c in cases),'total_deciding_factor_cells':sum(c['summary']['deciding_factor_count'] for c in cases),'total_same_cells':sum(len(c['summary']['same_dimensions']) for c in cases),'total_mixed_cells':sum(len(c['summary']['mixed_dimensions']) for c in cases),'total_different_cells':sum(len(c['summary']['different_dimensions']) for c in cases),'total_unknown_cells':sum(len(c['summary']['unknown_dimensions']) for c in cases)}
    payload={'engine':'CORE A.C.E. Robin','schema_version':'3.1','mode':'READ_ONLY','purpose':'independent complete deciding-factor matrix; structural identity is resolved before semantic comparison','cases':cases,'summary':summary,'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
    (out/'CORE_ROBIN_REPORT.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_ROBIN_REPORT.md').write_text('# CORE A.C.E. Robin Factor Matrix\n\n'+json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
