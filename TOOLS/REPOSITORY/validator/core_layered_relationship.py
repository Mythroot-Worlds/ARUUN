#!/usr/bin/env python3
"""Layered document relationship model for CORE A.C.E.

Relationships are decided from ordered layers rather than one similarity score:
category -> subject -> context -> content -> purpose -> information overlap.
VARIANT means the same information in the same relevant context with wording,
detail, or revision differences. RELATED means meaningful conceptual overlap
with materially different context or information.
"""
from __future__ import annotations
import re
from pathlib import Path
from core_document_identity import identify

STOP=set("the and for with from that this document regional family final draft version comparative variant duplicate supporting historical canonical canon hearth region regions reference audit checklist base peoples cultural".split())

def words(text):
    return {w for w in re.findall(r"[a-z][a-z0-9_]{3,}", text.lower()) if w not in STOP}

def overlap(a,b):
    aa,bb=words(a),words(b)
    return len(aa&bb)/max(1,len(aa|bb))

def layer_profile(path, text):
    i=identify(path); u=path.upper()
    category=i["content_type"]
    subject=i["subject"]
    scope=i["scope"]
    purpose=i["role"]
    return {"category":category,"subject":subject,"context":scope,"purpose":purpose,
            "content_fingerprint_size":len(words(text)),"path":path}

def compare(a_path,a_text,b_path,b_text):
    a=layer_profile(a_path,a_text); b=layer_profile(b_path,b_text)
    content=overlap(a_text,b_text)
    same_category=a["category"]==b["category"]
    same_subject=bool(a["subject"] and b["subject"] and a["subject"]==b["subject"])
    same_context=a["context"]==b["context"]
    same_type=same_category
    same_purpose=a["purpose"]==b["purpose"]
    layers={
      "category":{"state":"SAME" if same_category else "DIFFERENT","left":a["category"],"right":b["category"]},
      "subject":{"state":"SAME" if same_subject else "DIFFERENT","left":a["subject"],"right":b["subject"]},
      "context":{"state":"SAME" if same_context else "DIFFERENT","left":a["context"],"right":b["context"]},
      "content":{"state":"NEAR_SAME" if content>=0.78 else ("OVERLAPPING" if content>=0.30 else "DIFFERENT"),"score":round(content,4)},
      "purpose":{"state":"SAME" if same_purpose else "DIFFERENT","left":a["purpose"],"right":b["purpose"]},
      "information_overlap":{"state":"HIGH" if content>=0.78 else ("MEDIUM" if content>=0.30 else "LOW"),"score":round(content,4)}
    }
    # Context is a hard discriminator for VARIANT. Content equivalence is also required.
    if same_category and same_subject and same_context and same_type and content>=0.78:
        decision="DUPLICATE" if content>=0.95 else "VARIANT"
    elif same_category and same_subject and not same_context:
        decision="RELATED"
    elif same_category and content>=0.30:
        decision="RELATED"
    elif not same_category and content<0.12:
        decision="COINCIDENTAL"
    else:
        decision="REVIEW"
    return {"decision":decision,"layers":layers,"decision_basis":{
        "category":layers["category"]["state"],"subject":layers["subject"]["state"],"context":layers["context"]["state"],
        "information":layers["information_overlap"]["state"],"purpose":layers["purpose"]["state"]},
        "rules":{"variant_requires":["same category","same subject","same context","high information overlap"],"related_trigger":["same conceptual category/subject with different context or materially different information"]}}

CALIBRATION_CASES=(
("07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/HEARTH_DESERT_PEOPLES_CULTURAL_BASE_v0.1.md","07_ARCHIVE/HISTORICAL/HEARTH_CULTURES/HEARTH_DESERT_PEOPLES_CULTURAL_BASE_v0.2.md","VARIANT"),
("03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md","03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md","RELATED"),
)
