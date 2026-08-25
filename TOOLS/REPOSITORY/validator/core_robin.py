#!/usr/bin/env python3
"""CORE A.C.E. Robin: independent deciding-factor investigator.

Robin does not solve the case. Robin maps evidence across the complete deciding-
factor ontology so Batman can solve the relationship using a broader, explicit
factor record instead of treating every semantic difference as a conflict.
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

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def read(path,root,limit=60000):
    try:return (root/path).read_text(encoding='utf-8')[:limit]
    except:return ''

def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+',text) if s.strip()]

def relation_hits(sentence,dimension):
    u=sentence.lower();return [w for w in RELATIONS.get(dimension,[]) if re.search(r'\b'+re.escape(w)+r'\w*\b',u)]

def named_spans(sentence):
    vals=[]
    for m in re.finditer(r'\b([A-Z][A-Za-z0-9_-]{2,}(?:\s+[A-Z][A-Za-z0-9_-]{2,}){0,4})\b',sentence):
        v=m.group(1).strip(' .,;:()[]')
        if v not in vals and v.upper() not in {'THE','THIS','THAT','WHICH','DOCUMENT','SOURCE','CURRENT','FORMER'}: vals.append(v)
    return vals[:10]

def local_analysis(path,root,dimension):
    ss=sentences(read(path,root));out=[]
    for i,s in enumerate(ss):
        hits=relation_hits(s,dimension)
        if not hits: continue
        lo=max(0,i-MAX_WINDOW);hi=min(len(ss),i+MAX_WINDOW+1);window=ss[lo:hi];entities=named_spans(s)
        syntax_signal=bool(re.search(r'\b(?:is|are|has|have|governs?|rules?|leads?|supports?|informs?|derives?|replaces?|supersedes?|belongs?|contains?|within|under|from|for|differs?|same)\b',s,re.I))
        out.append({'source':path,'dimension':dimension,'sentence':s,'window':window,'relation_terms':hits,'entities':entities,'syntax_signal':syntax_signal,'subject_candidate':entities[0] if entities else None,'object_candidates':entities[1:] if len(entities)>1 else [],'relation_candidate':hits[0],'context_depth':len(window)})
    return out[:12]

def robin_case(case,root):
    docs=[case.get('left',''),case.get('right','')];analyses=[];results={}
    for d in QUESTIONS:
        items=[]
        for p in docs: items.extend(local_analysis(p,root,d))
        analyses.extend(items);explicit=[x for x in items if x['syntax_signal'] and x['relation_candidate']];entities=sum(len(x['entities']) for x in explicit);ambiguity=sum(1 for x in items if len(x['relation_terms'])>1 or len(x['entities'])>3)
        results[d]={'question':QUESTIONS[d],'relation_observations':len(items),'syntax_supported':len(explicit),'entity_observations':entities,'ambiguity_signals':ambiguity,'supports_semantic_relation':bool(explicit and entities>0),'confidence':'high' if explicit and entities>0 and ambiguity==0 else ('medium' if explicit else 'low'),'evidence_state':'SUPPORTED' if explicit else ('SIGNAL_ONLY' if items else 'NO_SIGNAL'),'contradiction_signal':bool(d=='relationship' and any('conflict' in x['relation_terms'] for x in items))}
    return {'relationship_id':case.get('relationship_id'),'documents':{'a':docs[0],'b':docs[1]},'robin_results':results,'observations':analyses,'method':'independent deciding-factor investigation across all ontology dimensions','role':'factor_investigator','independence':'Robin does not consume Batman conclusions; it investigates source text independently'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out
    queue=load(out/'CORE_ADJUDICATION_QUEUE.json',{'queue':[]});cases=[robin_case(c,root) for c in queue.get('queue',[])]
    summary={'cases':len(cases),'factor_dimensions':len(QUESTIONS),'supported_dimensions':sum(sum(v['evidence_state']=='SUPPORTED' for v in c['robin_results'].values()) for c in cases),'signal_only_dimensions':sum(sum(v['evidence_state']=='SIGNAL_ONLY' for v in c['robin_results'].values()) for c in cases),'no_signal_dimensions':sum(sum(v['evidence_state']=='NO_SIGNAL' for v in c['robin_results'].values()) for c in cases),'contradiction_signals':sum(sum(v['contradiction_signal'] for v in c['robin_results'].values()) for c in cases)}
    payload={'engine':'CORE A.C.E. Robin','schema_version':'2.1','mode':'READ_ONLY','purpose':'independent deciding-factor investigation; Robin maps evidence from the fresh adjudication queue, Batman solves the case','cases':cases,'summary':summary,'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
    (out/'CORE_ROBIN_REPORT.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');(out/'CORE_ROBIN_REPORT.md').write_text('# CORE A.C.E. Robin Factor Investigation\n\n'+json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
