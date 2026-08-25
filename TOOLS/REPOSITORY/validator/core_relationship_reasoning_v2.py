#!/usr/bin/env python3
"""Relationship hypothesis engine for Batman.

The active layered ontology is authoritative. Robin/exemplar evidence may
resolve ambiguity only after structural layers permit the candidate. Historical
human labels are provenance, never a veto over current structural identity.
"""
from __future__ import annotations
MODELS={
 "VARIANT":{"required":{"subject":"SAME","scope":"SAME"},"supports":{"function":{"SAME","MIXED"},"scale":{"SAME","MIXED"},"depth":{"SAME","MIXED"}},"blocks":{"subject":{"DIFFERENT","UNKNOWN"},"scope":{"DIFFERENT","UNKNOWN"}},"description":"same information, same scope, wording/detail difference"},
 "RELATED":{"supports":{"subject":{"SAME","MIXED","DIFFERENT"},"scope":{"DIFFERENT","MIXED"},"function":{"SAME","MIXED","DIFFERENT"}},"decisive":{"subject","scope","function"},"description":"meaningfully connected material without a stronger defining relationship"},
 "SUPPORTING":{"supports":{"function":{"MIXED","DIFFERENT"},"dependency":{"SAME","MIXED"},"importance":{"SAME","MIXED"}},"decisive":{"function","dependency","provenance"},"description":"one artifact supplies context, evidence, reference, comparative synthesis, or operational support"},
 "HISTORICAL":{"required":{"subject":"SAME"},"supports":{"canon_status":{"MIXED","DIFFERENT"},"development_state":{"MIXED","DIFFERENT"},"function":{"MIXED","DIFFERENT"}},"blocks":{"subject":{"DIFFERENT","UNKNOWN"}},"decisive":{"subject","canon_status","development_state"},"description":"temporal state, revision, or precedence explains the relationship"},
 "CONFLICT":{"required":{"subject":"SAME","scope":"SAME"},"supports":{"function":{"SAME","MIXED"},"canon_status":{"SAME","MIXED"}},"blocks":{"subject":{"DIFFERENT","UNKNOWN"},"scope":{"DIFFERENT","UNKNOWN"}},"decisive":{"subject","scope","function"},"description":"same subject and scope but incompatible claims"},
 "MISPLACED":{"supports":{"scope":{"DIFFERENT","MIXED"},"coherence":{"DIFFERENT"},"function":{"DIFFERENT","MIXED"}},"decisive":{"scope","coherence","function"},"description":"information appears where its role or scope does not belong"},
 "DUPLICATE":{"required":{"subject":"SAME","scope":"SAME"},"supports":{"function":{"SAME"},"scale":{"SAME"},"depth":{"SAME"}},"blocks":{"subject":{"DIFFERENT","UNKNOWN"},"scope":{"DIFFERENT","UNKNOWN"}},"description":"substantially the same information with no meaningful contextual distinction"},
 "COINCIDENTAL":{"supports":{"subject":{"DIFFERENT"},"scope":{"DIFFERENT"},"function":{"DIFFERENT"}},"decisive":{"subject","scope","function","dependency"},"description":"surface similarity without meaningful connection"},
}
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
def layered_adjudication(layered):
 s=layered_states(layered)
 if not s:return None
 layers=layered.get('layers',{}); basis=[]
 if s['category']!='SAME': return {'decision':'REVIEW','confidence':'LOW','basis':'Category differs or is unresolved; deep investigation required.','decisive_layers':['category'],'rejected_alternatives':['VARIANT','DUPLICATE','RELATED']}
 if s['subject']=='DIFFERENT': return {'decision':'RELATED','confidence':'HIGH','basis':'Same broad category but different subject; structural subject identity prevents VARIANT/DUPLICATE.','decisive_layers':['category','subject'],'rejected_alternatives':['VARIANT','DUPLICATE']}
 left_role=str(layers.get('purpose',{}).get('left','')).upper(); right_role=str(layers.get('purpose',{}).get('right','')).upper()
 paths=layers.get('path',{})
 left_path=str(paths.get('left','')).upper(); right_path=str(paths.get('right','')).upper()
 comparative='COMPARATIVE' in left_path or 'COMPARATIVE' in right_path
 if comparative and left_role!=right_role and 'SUPPORTING' in {left_role,right_role}:
  return {'decision':'SUPPORTING','confidence':'HIGH','basis':'One document is explicitly comparative/derived secondary material while the other is source material for the same subject.','decisive_layers':['subject','purpose','content'],'rejected_alternatives':['VARIANT','DUPLICATE','RELATED']}
 # Context is a hard semantic boundary for VARIANT. Historical exemplars,
 # similarity scores, and Robin hypotheses cannot override it.
 if s['scope']=='DIFFERENT':
  return {'decision':'RELATED','confidence':'HIGH','basis':'Same conceptual subject but different contextual scope; current ontology defines regional/contextual divergence as RELATED, regardless of legacy exemplar labels or lexical similarity.','decisive_layers':['subject','context','content'],'rejected_alternatives':['VARIANT','DUPLICATE','CONFLICT']}
 if s['scope']=='UNKNOWN':
  return {'decision':'REVIEW','confidence':'LOW','basis':'Context is unresolved; VARIANT cannot be promoted until relevant scope is known.','decisive_layers':['context'],'rejected_alternatives':['VARIANT','DUPLICATE']}
 if s['subject']=='SAME' and s['scope']=='SAME':
  if s['revision']=='SAME': return {'decision':'VARIANT','confidence':'HIGH','basis':'Same subject and context with explicit normalized revision lineage; version/detail changes are variants.','decisive_layers':['subject','context','revision'],'rejected_alternatives':['RELATED']}
  if s['information']=='HIGH' or s['content']=='NEAR_SAME': return {'decision':'VARIANT','confidence':'HIGH','basis':'Same subject and context with substantially equivalent information.','decisive_layers':['subject','context','content','information'],'rejected_alternatives':['RELATED']}
 if s['revision']=='SAME': return {'decision':'HISTORICAL','confidence':'HIGH','basis':'Explicit revision lineage explains the relationship but current content equivalence is insufficient for VARIANT.','decisive_layers':['revision'],'rejected_alternatives':['RELATED']}
 return None
def evaluate_relationships(robin,layered=None):
 la=layered_adjudication(layered)
 if la and la['decision'] in {'VARIANT','RELATED','HISTORICAL','SUPPORTING','REVIEW'}:
  return {'decision':la['decision'],'confidence':la['confidence'],'decision_basis':la['basis'],'reasoning_mode':'layered_ontology_authoritative','candidates':[la['decision']],'viable_relationships':[la['decision']] if la['decision']!='REVIEW' else [],'uncertain_relationships':['VARIANT','DUPLICATE'] if la['decision']=='REVIEW' else [],'decisive_unknowns':la.get('decisive_layers',[] ) if la['decision']=='REVIEW' else [],'non_decisive_unknowns':sorted(d for d in robin if state(robin,d)=='UNKNOWN'),'unresolved_dimensions':sorted(d for d in robin if state(robin,d)=='UNKNOWN'),'rejected_alternatives':la['rejected_alternatives'],'decisive_layers':la['decisive_layers'],'legacy_exemplar_override':False}
 cs=[candidate(n,m,robin) for n,m in MODELS.items()];cs.sort(key=lambda c:(c['status']=='VIABLE',c['score']),reverse=True);viable=[c for c in cs if c['status']=='VIABLE'];best=viable[0] if viable else None;competitors=viable[1:3] if best else []
 discriminators=sorted(set(best['decisive_dimensions'])-set().union(*(set(c['decisive_dimensions']) for c in competitors))) if best and competitors else (best['decisive_dimensions'] if best else [])
 decisive_unknown=sorted(d for d in discriminators if state(robin,d)=='UNKNOWN')
 if best: best['discriminating_factors']=discriminators;best['decisive_unknowns']=sorted(set(best['decisive_unknowns'])|set(decisive_unknown))
 if best and not best['decisive_unknowns'] and (not competitors or best['score']>competitors[0]['score']+3): decision=best['relationship'];confidence='HIGH' if best['score']>=10 else 'MEDIUM';basis='Strongest hypothesis wins on structural gates and discriminating factors.'
 elif best and not best['decisive_unknowns']: decision='REVIEW';confidence='MEDIUM';basis='Nearest viable hypotheses remain too close.'
 else: decision='REVIEW';confidence='LOW';basis='A factor needed to discriminate the strongest hypothesis remains unknown.'
 unknowns=sorted(d for d in robin if state(robin,d)=='UNKNOWN');relevant=sorted(set(best['decisive_unknowns']) if best else set())
 return {'decision':decision,'confidence':confidence,'decision_basis':basis,'reasoning_mode':'factor_adjudication_after_structural_gate','candidates':cs,'viable_relationships':[c['relationship'] for c in viable],'uncertain_relationships':[c['relationship'] for c in cs if c['status']=='UNCERTAIN'],'decisive_unknowns':relevant,'non_decisive_unknowns':sorted(set(unknowns)-set(relevant)),'unresolved_dimensions':unknowns,'rejected_alternatives':[],'decisive_layers':[],'legacy_exemplar_override':False}
