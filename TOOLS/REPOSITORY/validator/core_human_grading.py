#!/usr/bin/env python3
"""CORE human blind-test grading bridge.

The human judgments collected in chat are preserved as a separate, auditable
review set. They are NOT promoted into the training ledger until each judgment
is matched to a stable relationship_id from the blind-test artifact.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

JUDGMENTS=[
(1,["VARIANT"],"Hearth is the full-continent framework; Plains is basic information about one group."),
(2,["RELATED"],"Both cover different groups' birth-related information."),
(3,["VARIANT"],"Same broad-versus-regional relationship as case 1."),
(4,["CONFLICT"],"One is about childbirth; the other is about leadership."),
(5,["VARIANT"],"Regional variants."),(6,["VARIANT"],"Regional variants."),(7,["VARIANT"],"Regional variants."),
(8,["SUPPORTING"],"Audit document ensures the substantive document covers its information."),
(9,["SUPPORTING"],"Same as case 8."),(10,["RELATED"],"Partnership and reproduction overlap conceptually."),
(11,["SUPPORTING","CONFLICT"],"Broader regional leadership overlaps with narrower specialist-house leadership."),
(12,["VARIANT","RELATED","SUPPORTING","CONFLICT"],"Same subject with multiple overlapping dimensions."),
(13,["CONFLICT"],"Family versus leadership."),
(14,["VARIANT","RELATED"],"Specialist Houses and Specialist Lineages share the underlying subject."),
(15,["VARIANT","RELATED"],"Broad region versus narrow settlement."),
(16,["RELATED","CONFLICT"],"Leadership versus mountain-region lineage, with overlap."),
(17,["RELATED","SUPPORTING"],"Broad versus narrow."),(18,["CONFLICT"],"Leadership versus childbirth."),
(19,["RELATED","SUPPORTING","CONFLICT"],"Support document versus family-life document."),
(20,["RELATED"],"Same type of material, different peoples/regions."),
(21,["RELATED"],"Regional family versus settlement family."),
(22,["RELATED","SUPPORTING","CONFLICT"],"Regional leadership versus mountain Houses; Houses are local leaders."),
(23,["RELATED","SUPPORTING"],"Regional versus settlement family."),
(24,["RELATED","SUPPORTING","CONFLICT"],"Same as case 22."),(25,["SUPPORTING","CONFLICT"],"Supporting document versus leadership document."),
(26,["VARIANT","RELATED"],"Same subject, different regions."),(27,["RELATED","SUPPORTING"],"Regional versus settlement."),
(28,["RELATED","SUPPORTING","CONFLICT"],"Same as case 22."),(29,["RELATED","SUPPORTING"],"Same as case 26."),
(30,["RELATED","SUPPORTING","CONFLICT"],"Supporting document versus family-life document."),
]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--out',default='TOOLS/REPOSITORY/REPORTS');a=ap.parse_args();out=Path(a.root).resolve()/a.out;out.mkdir(parents=True,exist_ok=True)
 data={'engine':'CORE Human Blind-Test Grading Bridge','status':'UNMATCHED_REVIEW','case_count':len(JUDGMENTS),'judgments':[{'case_number':n,'human_labels':labels,'reason':reason,'relationship_id':None,'matched':False} for n,labels,reason in JUDGMENTS],'safety':{'not_training_data':True,'not_scored_until_stable_relationship_ids_match':True,'automatic_canon_change':False}}
 (out/'CORE_HUMAN_BLIND_GRADES.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 (out/'CORE_HUMAN_BLIND_GRADES.md').write_text('# CORE Human Blind-Test Grades\n\n30 human judgments have been preserved separately. They are **not yet training data or a score** because the conversational case list must be matched to stable relationship IDs from the blind-test artifact before evaluation.\n\nThis separation prevents accidental contamination or false accuracy claims.\n',encoding='utf-8')
 print('Preserved 30 human judgments as an unmatched, non-training review set.')
if __name__=='__main__':main()
