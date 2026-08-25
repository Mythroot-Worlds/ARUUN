#!/usr/bin/env python3
"""Relationship hypothesis engine for Batman.

VARIANT is deliberately narrow: same normalized subject and same structural
region scope. Different regional instances are RELATED unless another stronger
relationship is evidenced.
"""
from __future__ import annotations

MODELS={
 "VARIANT":{"required":{"subject":"SAME","scope":"SAME"},"supports":{"function":{"SAME","MIXED"},"scale":{"SAME","MIXED"},"depth":{"SAME","MIXED"}},"blocks":{"subject":{"DIFFERENT","UNKNOWN"},"scope":{"DIFFERENT","UNKNOWN"}},"description":"same information, same scope, wording/detail difference"},
 "RELATED":{"supports":{"subject":{"SAME","MIXED","DIFFERENT"},"scope":{"DIFFERENT","MIXED"},"function":{"SAME","MIXED","DIFFERENT"}},"decisive":{"subject","scope","function"},"description":"meaningfully connected material without a stronger defining relationship"},
 "SUPPORTING":{"supports":{"function":{"MIXED","DIFFERENT"},"dependency":{"SAME","MIXED"},"importance":{"SAME","MIXED"}},"decisive":{"function","dependency","provenance"},"description":"one artifact supplies context, evidence, reference, or operational support"},
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

def evaluate_relationships(robin):
 cs=[candidate(n,m,robin) for n,m in MODELS.items()];cs.sort(key=lambda c:(c['status']=='VIABLE',c['score']),reverse=True);viable=[c for c in cs if c['status']=='VIABLE'];best=viable[0] if viable else None;competitors=viable[1:3] if best else []
 discriminators=sorted(set(best['decisive_dimensions'])-set().union(*(set(c['decisive_dimensions']) for c in competitors))) if best and competitors else (best['decisive_dimensions'] if best else [])
 decisive_unknown=sorted(d for d in discriminators if state(robin,d)=='UNKNOWN')
 if best: best['discriminating_factors']=discriminators;best['decisive_unknowns']=sorted(set(best['decisive_unknowns'])|set(decisive_unknown))
 if best and not best['decisive_unknowns'] and (not competitors or best['score']>competitors[0]['score']+3):
  decision=best['relationship'];confidence='HIGH' if best['score']>=10 else 'MEDIUM';basis='Strongest hypothesis wins on structural gates and discriminating factors.'
 elif best and not best['decisive_unknowns']:
  decision='REVIEW';confidence='MEDIUM';basis='Nearest viable hypotheses remain too close.'
 else:
  decision='REVIEW';confidence='LOW';basis='A factor needed to discriminate the strongest hypothesis remains unknown.'
 unknowns=sorted(d for d in robin if state(robin,d)=='UNKNOWN');relevant=sorted(set(best['decisive_unknowns']) if best else set())
 return {'decision':decision,'confidence':confidence,'decision_basis':basis,'reasoning_mode':'hypothesis_then_discriminator','candidates':cs,'viable_relationships':[c['relationship'] for c in viable],'uncertain_relationships':[c['relationship'] for c in cs if c['status']=='UNCERTAIN'],'decisive_unknowns':relevant,'non_decisive_unknowns':sorted(set(unknowns)-set(relevant)),'unresolved_dimensions':unknowns}
