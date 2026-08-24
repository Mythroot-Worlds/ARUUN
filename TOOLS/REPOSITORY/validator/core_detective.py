#!/usr/bin/env python3
"""CORE A.C.E. Detective: bounded investigation with evidence quality scoring."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

DEFAULT_POOL_SIZE=10
MAX_POOL_SIZE=20

def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
    except:return d

def read(path,root,limit=60000):
    p=root/path if path else None
    try:return p.read_text(encoding='utf-8')[:limit] if p and p.exists() else ''
    except:return ''

def signals(path,body):
    s=((path or '')+'\n'+body).upper(); groups={'scope':['CONTINENT','CONTINENTAL','HEARTH-WIDE','REGIONAL','REGION','MOUNTAIN','RIVER','WETLAND','PLAINS','DESERT','COAST','SETTLEMENT','VILLAGE','LOCAL','NARROW'],'population':['PEOPLE','PEOPLES','LINEAGE','FAMILY','CLAN','HOUSE','HOUSEHOLD'],'family':['FAMILY','BIRTH','CHILDHOOD','MARRIAGE','KIN','HOUSEHOLD'],'authority':['GOVERNANCE','AUTHORITY','LEADERSHIP','COUNCIL','LEADER','HEAD','HOUSE'],'specialist':['SPECIALIST','LINEAGE','HOUSE','CRAFT','KEEPER'],'support':['CHECKLIST','AUDIT','REFERENCE','FRAMEWORK','GUIDE'],'historical':['HISTORICAL','ARCHIVE','REVISION','FORMER','OBSOLETE']}
    return {k:sorted({w for w in ws if re.search(r'\b'+re.escape(w)+r'\b',s)}) for k,ws in groups.items()}

def files(root): return [str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*.md') if '.git' not in p.parts and 'REPORTS' not in p.parts]

def related_candidates(a,b,root,exclude=(),pool_size=DEFAULT_POOL_SIZE):
    base=signals(a,read(a,root));excluded={a,b,*exclude};scored=[]
    for p in files(root):
        if p in excluded: continue
        s=signals(p,read(p,root));score=2*sum(len(set(base[k])&set(s[k])) for k in base)
        if score: scored.append((score,p))
    return [p for _,p in sorted(scored,key=lambda x:(x[0],x[1]),reverse=True)[:max(1,min(pool_size,MAX_POOL_SIZE))]]

def evidence_for(a,b,root,extra_targets=(),exclude=(),pool_size=DEFAULT_POOL_SIZE):
    targets=[]
    for p in list(extra_targets)+related_candidates(a,b,root,exclude=set(exclude)|set(extra_targets),pool_size=pool_size):
        if p not in targets: targets.append(p)
    targets=targets[:max(1,min(pool_size,MAX_POOL_SIZE))];snippets=[];focus=['AUTHORITY','LEADERSHIP','HOUSE','VILLAGE','SETTLEMENT','REGIONAL','CONTINENT','FAMILY','BIRTH','SUPPORT','REFERENCE','HISTORICAL','REVISED','SUPERSEDE','DERIVED','BASED ON','INFORMS']
    for p in [a,b]+targets:
        lines=read(p,root).splitlines();hits=[]
        for i,line in enumerate(lines):
            if any(w in line.upper() for w in focus): hits.append(' '.join(lines[max(0,i-1):min(len(lines),i+2)]).strip())
        if hits: snippets.append({'path':p,'excerpts':hits[:4]})
    return targets,snippets

def question_for_unknown(u):
    lu=u.lower()
    if 'authority' in lu:return 'Which source explicitly establishes the organizational authority, leadership role, and scope of the disputed document?'
    if 'support' in lu:return 'Which source explicitly establishes that one document supports, informs, references, or derives from the other?'
    if 'temporal' in lu:return 'Which source establishes the temporal relationship, revision, supersession, or historical precedence between these documents?'
    return 'What specific source evidence would resolve the remaining uncertainty?'

def evidence_quality(question,source_path,excerpt):
    text=excerpt.upper();q=question.lower();score=0.0;basis=[]
    if 'authority' in q: patterns=[r'\b(?:AUTHORITY|LEADER|LEADERSHIP|GOVERNANCE|COUNCIL|HEAD)\b.{0,100}\b(?:VILLAGE|SETTLEMENT|REGION|REGIONAL|CONTINENT|CONTINENTAL)\b',r'\b(?:VILLAGE|SETTLEMENT|REGION|REGIONAL|CONTINENT|CONTINENTAL)\b.{0,100}\b(?:AUTHORITY|LEADER|LEADERSHIP|GOVERNANCE|COUNCIL|HEAD)\b']
    elif 'support' in q: patterns=[r'\b(?:SUPPORT|INFORMS|REFERENCES|DERIVED FROM|BASED ON|BUILDS ON)\b.{0,120}\b(?:DOCUMENT|GUIDE|FRAMEWORK|CHECKLIST|CANON|SOURCE)\b']
    elif 'temporal' in q: patterns=[r'\b(?:REVISED|SUPERSEDES|REPLACED|PREVIOUS|FORMER|EARLIER|CURRENT|OLDER|REVISION)\b.{0,120}\b(?:VERSION|DOCUMENT|CANON|SOURCE|TEXT)\b']
    else: patterns=[]
    direct=any(re.search(p,text) for p in patterns)
    contextual=bool(re.search(r'\b(?:AUTHORITY|LEADER|GOVERNANCE|SUPPORT|REFERENCE|HISTORICAL|REVISED|SUPERSEDES|DERIVED|BASED ON|VILLAGE|SETTLEMENT|REGION|CONTINENT)\b',text))
    if direct: score=1.0;basis.append('direct_explicit_statement_pattern')
    elif contextual: score=0.5;basis.append('contextual_signal_only')
    else: basis.append('no_question_specific_signal')
    upper=source_path.upper();source_type='primary_candidate'
    if any(x in upper for x in ['CHECKLIST','AUDIT','FRAMEWORK','GUIDE','OPERATING_RULES']): source_type='supporting_candidate'
    if any(x in upper for x in ['ARCHIVE','HISTORICAL','REVISION']): source_type='historical_candidate'
    return {'path':source_path,'quality_score':score,'quality_class':'direct' if score==1.0 else ('contextual' if score==0.5 else 'irrelevant'),'basis':basis,'source_type':source_type}

def evidence_validity(question,sources):
    qualities=[evidence_quality(question,p,x) for p,x in sources];best=max((q['quality_score'] for q in qualities),default=0.0);direct=sum(q['quality_class']=='direct' for q in qualities);contextual=sum(q['quality_class']=='contextual' for q in qualities)
    return {'question':question,'best_quality':best,'direct_evidence_count':direct,'contextual_evidence_count':contextual,'evidence_quality':qualities,'answerability':best,'answers_question':best>=1.0}

def missing_targets(unknown,root,a,b,used,pool_size):
    targets=[];reasons=[];used=set(used)|{a,b}
    for u in unknown:
        lu=u.lower();dimension='authority' if 'authority' in lu else ('support' if 'support' in lu else ('historical' if 'temporal' in lu else None))
        if not dimension: continue
        candidates=[]
        for p in files(root):
            if p in used: continue
            s=signals(p,read(p,root))
            if (dimension=='authority' and (s['authority'] or s['scope'])) or (dimension=='support' and s['support']) or (dimension=='historical' and s['historical']): candidates.append(p)
        for target in candidates[:max(1,min(pool_size,MAX_POOL_SIZE))]:
            targets.append(target);reasons.append({'missing':u,'dimension':dimension,'target':target,'reason':'round-one evidence did not contain direct question-specific evidence'})
    return list(dict.fromkeys(targets))[:max(1,min(pool_size,MAX_POOL_SIZE))],reasons

def investigate(r,root,pool_size=DEFAULT_POOL_SIZE):
    a,b=r.get('left',''),r.get('right','');sa,sb=signals(a,read(a,root)),signals(b,read(b,root));known=[];unknown=[];assumptions=[]
    for d in sa:
        common=sorted(set(sa[d])&set(sb[d]));diff=sorted(set(sa[d])^set(sb[d]))
        if common: known.append(f'{d}: shared {", ".join(common)}')
        if diff: known.append(f'{d}: differs {", ".join(diff)}')
    if sa['authority'] or sb['authority']: unknown.append('authority role and organizational level require contextual confirmation')
    if sa['support'] or sb['support']: unknown.append('explicit support relationship is not established by indicators alone')
    if sa['historical'] or sb['historical']: unknown.append('temporal precedence/supersession is not established by indicators alone')
    if sa['family'] and sb['family']: assumptions.append('shared family vocabulary may indicate shared subject without implying duplicate content')
    if sa['authority'] and sb['specialist']: assumptions.append('authority and specialist signals may describe overlapping roles')
    hypotheses=[];overlap=set(sum(sa.values(),[]))&set(sum(sb.values(),[]))
    if overlap: hypotheses.append({'label':'VARIANT','basis':'shared subject signals with possible scope differences','status':'candidate'})
    if sa['support'] or sb['support']: hypotheses.append({'label':'SUPPORTING','basis':'support/audit/reference indicators present','status':'candidate'})
    if sa['historical'] or sb['historical']: hypotheses.append({'label':'HISTORICAL','basis':'historical/revision indicators present','status':'candidate'})
    if set(sa['authority'])&set(sb['authority']): hypotheses.append({'label':'RELATED','basis':'shared authority/governance signals','status':'candidate'})
    if not hypotheses: hypotheses=[{'label':'REVIEW','basis':'insufficient structural evidence','status':'candidate'}]
    unknown_questions=[{'unknown':u,'question':question_for_unknown(u)} for u in unknown];rounds=[];all_targets=[];all_snippets=[];all_validity=[];resolved=[]
    t1,s1=evidence_for(a,b,root,pool_size=pool_size);all_targets.extend(t1);all_snippets.extend(s1);sources1=[(s['path'],e) for s in s1 for e in s['excerpts']];v1=[evidence_validity(q['question'],sources1) for q in unknown_questions];all_validity.extend(v1)
    for u,v in zip(unknown,v1):
        if v['answers_question']: resolved.append(u)
    remaining=[u for u in unknown if u not in resolved]
    rounds.append({'round':1,'trigger':'initial investigation','questions':unknown_questions,'evidence_targets':t1,'evidence_found':s1,'evidence_validity':v1,'unanswered_after_round':remaining,'decision':'answered' if unknown_questions and not remaining else ('no_investigation_needed' if not unknown_questions else 'insufficient'),'next_round_justified':bool(remaining)})
    second_targets=[];missing=[];s2=[];v2=[]
    if remaining: second_targets,missing=missing_targets(remaining,root,a,b,all_targets,pool_size)
    if remaining and second_targets:
        second_questions=[{'unknown':u,'question':question_for_unknown(u)} for u in remaining];t2,s2=evidence_for(a,b,root,extra_targets=second_targets,exclude=all_targets,pool_size=pool_size);all_targets.extend(t2);all_snippets.extend(s2);sources2=[(s['path'],e) for s in s2 for e in s['excerpts']];v2=[evidence_validity(q['question'],sources2) for q in second_questions];all_validity.extend(v2)
        second_resolved=[u for u,v in zip(remaining,v2) if v['answers_question']];resolved.extend(second_resolved);remaining=[u for u in remaining if u not in second_resolved]
        rounds.append({'round':2,'trigger':'round 1 was insufficient','trigger_evidence':missing,'questions':second_questions,'evidence_targets':t2,'evidence_found':s2,'evidence_validity':v2,'unanswered_after_round':remaining,'decision':'answered' if second_resolved and not remaining else 'insufficient','next_round_justified':False})
    updates=[]
    if resolved: updates.append({'type':'evidence_update','effect':'reduced_uncertainty','resolved_unknowns':sorted(set(resolved)),'basis':'retrieved evidence contained direct question-specific evidence','rounds':[x['round'] for x in rounds]})
    for h in hypotheses: h['post_evidence_status']='supported_candidate' if overlap else h['status']
    return {'relationship_id':r.get('relationship_id'),'documents':{'a':a,'b':b},'known':known,'unknown_before':sorted(set(unknown)),'assumptions':sorted(set(assumptions)),'questions':unknown_questions,'investigation_rounds':len(rounds),'investigation_rounds_detail':rounds,'evidence_pool_size':pool_size,'evidence_targets':all_targets,'evidence_found':all_snippets,'evidence_validity':all_validity,'evidence_updates':updates,'unknown_after':sorted(set(remaining)),'hypotheses':hypotheses,'challenge_questions':[f'What evidence would falsify {h["label"]}?' for h in hypotheses],'second_pass':{'attempted':len(rounds)>1,'causally_justified':len(rounds)>1 and rounds[1]['trigger']=='round 1 was insufficient','missing_evidence':missing,'targets':second_targets,'new_targets_distinct_from_round_one':bool(set(second_targets)-set(t1))},'stop_reason':'bounded investigation completed; human review remains authoritative','safety':{'self_training':False,'automatic_rule_promotion':False,'automatic_canon_change':False}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');ap.add_argument('--pool-size',type=int,default=DEFAULT_POOL_SIZE);x=ap.parse_args();root=Path(x.root).resolve();out=root/x.out;pool_size=max(1,min(x.pool_size,MAX_POOL_SIZE));blind=load(out/'CORE_BLIND_TEST.json',{'predictions':[]});cases=[investigate(r,root,pool_size) for r in blind.get('predictions',[])]
    before=sum(bool(c['unknown_before']) for c in cases);after=sum(bool(c['unknown_after']) for c in cases);updates=sum(bool(c['evidence_updates']) for c in cases);answered=sum(sum(1 for v in c['evidence_validity'] if v['answers_question']) for c in cases);second=sum(1 for c in cases if c['second_pass']['attempted']);causal=sum(1 for c in cases if c['second_pass']['causally_justified']);distinct=sum(1 for c in cases if c['second_pass']['new_targets_distinct_from_round_one']);rounds=sum(c['investigation_rounds'] for c in cases);evidence_docs=sum(len(c['evidence_targets']) for c in cases);direct=sum(sum(v['direct_evidence_count'] for v in c['evidence_validity']) for c in cases);contextual=sum(sum(v['contextual_evidence_count'] for v in c['evidence_validity']) for c in cases)
    report={'engine':'CORE A.C.E. Detective','schema_version':'1.7','mode':'READ_ONLY','purpose':'bounded evidence-seeking investigation with configurable evidence neighborhoods, evidence quality/provenance scoring, question-specific validity, and causally auditable second-pass targeting','cases':cases,'summary':{'cases':len(cases),'evidence_pool_size':pool_size,'with_unknowns_before':before,'with_unknowns_after':after,'cases_with_evidence':sum(bool(c['evidence_found']) for c in cases),'cases_with_updates':updates,'unknown_cases_reduced':before-after,'questions_fully_answered':answered,'direct_evidence_observations':direct,'contextual_evidence_observations':contextual,'cases_requiring_second_pass':second,'cases_with_causally_justified_second_pass':causal,'cases_with_distinct_second_pass_targets':distinct,'average_rounds':round(rounds/len(cases),2) if cases else 0,'total_investigation_rounds':rounds,'total_evidence_target_slots':evidence_docs},'safety':{'human_validation_required':True,'automatic_canon_change':False,'automatic_rule_promotion':False}}
    (out/'CORE_DETECTIVE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(out/'CORE_DETECTIVE_REPORT.md').write_text('# CORE A.C.E. Detective Report\n\nBounded evidence-seeking investigation with configurable evidence neighborhoods, evidence quality/provenance scoring, question-specific validity, and causally auditable second-pass targeting.\n\n'+f"Cases: **{len(cases)}**\nEvidence pool size: **{pool_size}**\nUnknown cases before: **{before}**\nUnknown cases after: **{after}**\nCases with evidence: **{report['summary']['cases_with_evidence']}**\nCases with evidence updates: **{updates}**\nUnknown cases reduced: **{before-after}**\nQuestions fully answered: **{answered}**\nDirect evidence observations: **{direct}**\nContextual evidence observations: **{contextual}**\nCases requiring second pass: **{second}**\nCausally justified second passes: **{causal}**\nDistinct second-pass targets: **{distinct}**\nAverage rounds: **{report['summary']['average_rounds']}**\nTotal evidence target slots: **{evidence_docs}**\n",encoding='utf-8');print(f"Detective: {len(cases)} cases; pool {pool_size}; second passes {second}; causally justified {causal}; distinct targets {distinct}; unknown cases reduced {before-after}; fully answered {answered}; direct evidence observations {direct}; contextual {contextual}.")
if __name__=='__main__':main()
