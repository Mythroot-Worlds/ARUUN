#!/usr/bin/env python3
"""Relationship hypothesis engine for Batman.

The layered ontology is authoritative for constraints, not a blanket terminal
classifier. Structural facts eliminate impossible relationships; Batman uses
Robin evidence to choose among the remaining viable relationships.
"""
from __future__ import annotations
MODELS={"VARIANT":{"required":{"subject":"SAME","scope":"SAME"},"supports":{"function":{"SAME","MIXED"}},"blocks":{"subject":{"DIFFERENT","UNKNOWN"},"scope":{"DIFFERENT","UNKNOWN"}},"description":"same information, same scope, wording/detail difference"},"RELATED":{"supports":{"subject":{"SAME","MIXED","DIFFERENT"},"scope":{"DIFFERENT","MIXED"},"function":{"SAME","MIXED","DIFFERENT"}},"decisive":{"subject","scope","function"},"description":"meaningfully connected material without a stronger defining relationship"},"SUPPORTING":{"supports":{"function":{"MIXED","DIFFERENT"},"dependency":{"SAME","MIXED"},"importance":{"SAME","MIXED"}},"decisive":{"function","dependency","provenance"},"description":"one artifact supplies context, evidence, reference, comparative synthesis, or operational support"},"HISTORICAL":{"required":{"subject":"SAME"},"supports":{"canon_status":{"MIXED","DIFFERENT"},"development_state":{"MIXED","DIFFERENT"},"function":{"MIXED","DIFFERENT"}},"blocks":{"subject":{"DIFFERENT","UNKNOWN"}},"decisive":{"subject","canon_status","development_state"},"description":"temporal state, revision, or precedence explains the relationship"},"CONFLICT":{"required":{"subject":"SAME","scope":"SAME"},"supports":{"function":{"SAME","MIXED"}},"blocks":{"subject":{"DIFFERENT","UNKNOWN"},"scope":{"DIFFERENT","UNKNOWN"}},"decisive":{"subject","scope","function"},"description":"same subject and scope but incompatible claims"},"MISPLACED":{"supports":{"scope":{"DIFFERENT","MIXED"},"coherence":{"DIFFERENT"},"function":{"DIFFERENT","MIXED"}},"decisive":{"scope","coherence","function"},"description":"information appears where its role or scope does not belong"},"DUPLICATE":{"required":{"subject":"SAME","scope":"SAME"},"supports":{"function":{"SAME"}},"blocks":{"subject":{"DIFFERENT","UNKNOWN"},"scope":{"DIFFERENT","UNKNOWN"}},"description":"substantially the same information with no meaningful contextual distinction"},"COINCIDENTAL":{"supports":{"subject":{"DIFFERENT"},"scope":{"DIFFERENT"},"function":{"DIFFERENT"}},"decisive":{"subject","scope","function","dependency"},"description":"surface similarity without meaningful connection"}}
def state(robin,dim): return str((robin.get(dim) or {}).get('relationship_state','UNKNOWN')).upper()
def dims(m): return set(m.get('decisive',set()))|set(m.get('required',{}))|set(m.get('blocks',{}))
def candidate(name,m,robin):
 reasons=[];supports=[];blocks=[];unknown=[]
 for d,e in m.get('required',{}).items():
  s=state(robin,d)
  if s==e: reasons.append(f'{d}={s}')
  elif s=='UNKNOWN': unknown.append(d)
  else: blocks.append(f'{d} expected {e}, observed {s}')
 for d,states in m.get('blocks',{}).items():
  s=state(robin,d)
  if s in states: blocks.append(f'{d}={s} blocks hypothesis')
  elif s=='UNKNOWN' and d in dims(m): unknown.append(d)
 for d,states in m.get('supports',{}).items():
  if state(robin,d) in states: supports.append(f'{d}={state(robin,d)}')
 score=10*len(reasons)+3*len(supports)-12*len(blocks)-5*len(set(unknown))
 return {'relationship':name,'status':'DISQUALIFIED' if blocks else ('UNCERTAIN' if unknown else 'VIABLE'),'score':score,'description':m['description'],'required_factors':reasons,'supporting_factors':supports,'blocking_factors':blocks,'decisive_dimensions':sorted(dims(m)),'decisive_unknowns':sorted(set(unknown))}
def layered_states(layered):
 if not layered:return {}
 layers=layered.get('layers',{})
 return {'category':str(layers.get('category',{}).get('state','UNKNOWN')).upper(),'subject':str(layers.get('subject',{}).get('state','UNKNOWN')).upper(),'scope':str(layers.get('context',{}).get('state','UNKNOWN')).upper(),'function':str(layers.get('purpose',{}).get('state','UNKNOWN')).upper(),'content':str(layers.get('content',{}).get('state','UNKNOWN')).upper(),'information':str(layers.get('information_overlap',{}).get('state','UNKNOWN')).upper(),'revision':str(layers.get('revision_lineage',{}).get('state','UNKNOWN')).upper()}
def layered_constraints(layered):
 s=layered_states(layered)
 if not s:return None
 layers=layered.get('layers',{});paths=layers.get('path',{});lp=str(paths.get('left','')).upper();rp=str(paths.get('right','')).upper();lr=str(layers.get('purpose',{}).get('left','')).upper();rr=str(layers.get('purpose',{}).get('right','')).upper();c={'excluded':set(),'supported':set(),'decisive_layers':[],'basis':[]}
 if s['category']!='SAME': c['excluded']|={'VARIANT','DUPLICATE','CONFLICT'};c['decisive_layers'].append('category');c['basis'].append('category differs')
 if s['subject']=='DIFFERENT': c['excluded']|={'VARIANT','DUPLICATE','CONFLICT','HISTORICAL'};c['supported'].add('COINCIDENTAL');c['decisive_layers'].append('subject');c['basis'].append('subject differs')
 elif s['subject']=='UNKNOWN': c['excluded']|={'VARIANT','DUPLICATE','CONFLICT'};c['decisive_layers'].append('subject');c['basis'].append('subject unresolved')
 if s['scope']=='DIFFERENT': c['excluded']|={'VARIANT','DUPLICATE','CONFLICT'};c['supported']|={'RELATED','MISPLACED','SUPPORTING'};c['decisive_layers'].append('context');c['basis'].append('different context vetoes VARIANT/DUPLICATE but does not itself force RELATED')
 elif s['scope']=='UNKNOWN': c['excluded']|={'VARIANT','DUPLICATE'};c['decisive_layers'].append('context');c['basis'].append('context unresolved')
 if 'COMPARATIVE' in lp or 'COMPARATIVE' in rp:
  if lr!=rr: c['supported'].add('SUPPORTING');c['decisive_layers']+=['purpose','path'];c['basis'].append('comparative path plus differing role supports SUPPORTING')
 if s['revision']=='SAME': c['supported'].add('VARIANT');c['decisive_layers'].append('revision');c['basis'].append('same normalized revision lineage')
 if s['scope']=='SAME' and s['subject']=='SAME' and (s['information']=='HIGH' or s['content']=='NEAR_SAME'): c['supported']|={'VARIANT','DUPLICATE'};c['decisive_layers']+=['content','information'];c['basis'].append('same context with high informational equivalence')
 return c
def evaluate_relationships(robin,layered=None):
 c=layered_constraints(layered) or {'excluded':set(),'supported':set(),'decisive_layers':[],'basis':[]};cs=[candidate(n,m,robin) for n,m in MODELS.items()]
 for x in cs:
  n=x['relationship']
  if n in c['excluded']: x['status']='DISQUALIFIED';x['blocking_factors'].append('layered ontology exclusion: '+'; '.join(c['basis']))
  elif n in c['supported']: x['score']+=8;x['supporting_factors'].append('layered ontology support')
 cs.sort(key=lambda x:(x['status']=='VIABLE',x['score']),reverse=True);viable=[x for x in cs if x['status']!='DISQUALIFIED'];best=viable[0] if viable else None;competitors=viable[1:3] if best else []
 decisive_unknown=sorted(set(best['decisive_unknowns']) & set(c['decisive_layers'])) if best else c['decisive_layers']
 if best and not decisive_unknown and best['status']=='VIABLE' and (not competitors or best['score']>competitors[0]['score']+3): decision=best['relationship'];confidence='HIGH' if best['score']>=10 else 'MEDIUM';basis='Layered constraints narrow the field; Robin evidence discriminates the surviving hypotheses.'
 else: decision='REVIEW';confidence='LOW' if decisive_unknown else 'MEDIUM';basis='Layered constraints leave multiple plausible relationships or a decisive factor unresolved.'
 return {'decision':decision,'confidence':confidence,'decision_basis':basis,'reasoning_mode':'layered_constraints_then_factor_adjudication','candidates':cs,'viable_relationships':[x['relationship'] for x in viable],'uncertain_relationships':[x['relationship'] for x in cs if x['status']=='UNCERTAIN'],'decisive_unknowns':decisive_unknown,'non_decisive_unknowns':sorted(d for d in robin if state(robin,d)=='UNKNOWN' and d not in decisive_unknown),'unresolved_dimensions':sorted(d for d in robin if state(robin,d)=='UNKNOWN'),'rejected_alternatives':[x['relationship'] for x in cs if x['status']=='DISQUALIFIED'],'decisive_layers':c['decisive_layers'],'legacy_exemplar_override':False,'layered_constraints':{'excluded':sorted(c['excluded']),'supported':sorted(c['supported']),'basis':c['basis']}}
