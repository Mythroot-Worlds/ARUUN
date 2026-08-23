#!/usr/bin/env python3
"""ARUUN repository audit validator.

Read-only. Audits repository structure, metadata, filenames, and selected
known claims. Existing ARUUN status language is classified as legacy metadata,
not automatically treated as an error. The validator never edits canon.
"""
from __future__ import annotations
import argparse,re
from dataclasses import dataclass
from pathlib import Path
IGNORE_DIRS={".git",".github","node_modules"}; ARCHIVE_TOP="07_ARCHIVE"
VALID_LAYERS={"world","tool","reference","audit","archive","release"}
VALID_STATUS={"canon","working_model","inference","proposal","open","unknown","retired","canon_reference","working","provisional"}
VALID_AUTHORITY={"world","regional","continental","tool","reference","supporting","historical","audit"}
STATUS_MAP={
 "authoritative":"canon","current authoritative world bible for development.":"canon",
 "canonical consolidation / current state":"canon","working canon — creative geography decision":"canon",
 "working canon — science-derived geographic decision":"canon","working canon":"working_model",
 "broad working pass. nothing here is locked canon unless explicitly approved.":"working_model",
 "proposed working layer — not cultural canon":"proposal",
 "broad working framework. not locked canon.":"working_model",
 "working canon. built per `01_master_instructions.md` and `05_batch_prompt.md`. no world-name has been assigned; none is used here.":"working_model",
}
SUBJECT_ALIASES={"family_birth_childhood":"family.birth_childhood","birth_childhood":"family.birth_childhood","family_partnership":"family.partnership","governance_and_authority":"governance.authority","governance_authority":"governance.authority","food_subsistence":"food.subsistence","settlement_housing":"settlement.housing"}
KNOWN_CLAIMS=[
 ("DEMO-001",r"(?:~|about\s*)?1[.,]?5\s*(?:million|M)\b",r"~?1[.,]?91\s*(?:million|M)\b","Superseded Hearth population claim (~1.5M) conflicts with the newer ~1.91M working demographic model.","Review current active demographic references; preserve historical/archive occurrences."),
 ("DEMO-002",r"450[,.]?000|450k\b",r"650[,.]?000|650k\b","Superseded Plains population claim (~450k) conflicts with the newer ~650k working model.","Review current active demographic references."),
 ("DEMO-003",r"375[,.]?000|375k\b",r"500[,.]?000|500k\b","Superseded River population claim (~375k) conflicts with the newer ~500k working model.","Review current active demographic references."),
 ("DEMO-004",r"225[,.]?000|225k\b",r"290[,.]?000|290k\b","Superseded Wetlands population claim (~225k) conflicts with the newer ~290k working model.","Review current active demographic references."),
 ("DEMO-005",r"180[,.]?000|180k\b",r"290[,.]?000|290k\b","Superseded Coast population claim (~180k) conflicts with the newer ~290k working model.","Review current active demographic references."),
 ("DEMO-006",r"120[,.]?000|120k\b",r"95[,.]?000|95k\b","Superseded Mountains population claim (~120k) conflicts with the newer ~95k working model.","Review current active demographic references."),
 ("DEMO-007",r"105[,.]?000|105k\b",r"85[,.]?000|85k\b","Superseded Desert/dry-interior population claim (~105k) conflicts with the newer ~85k working model.","Review current active demographic references."),]
@dataclass
class Finding: id:str; severity:str; category:str; path:str; message:str; recommendation:str=""; related:str=""
@dataclass
class Document: path:str; filename:str; title:str=""; id:str=""; domain:str=""; layer:str=""; scope:str=""; status:str=""; authority:str=""; continent:str=""; people:str=""; subject:str=""; archive:bool=False

def parse_frontmatter(text):
 if not text.startswith("---\n"): return {}
 end=text.find("\n---",4)
 if end<0:return {}
 d={}
 for line in text[4:end].splitlines():
  if ":" in line:
   k,v=line.split(":",1); d[k.strip()]=v.strip().strip("\"'")
 return d

def inline_status(text):
 m=re.search(r"\*\*Status:\*\*\s*([^\n]+)",text,re.I); return m.group(1).strip().lower().rstrip(".") if m else ""

def first_heading(text):
 m=re.search(r"^#\s+(.+)$",text,re.M); return m.group(1).strip() if m else ""

def subject_from_stem(stem):
 k=stem.lower().replace("-","_").replace(" ","_")
 if k.endswith("_comparative"): k=k[:-12]
 return SUBJECT_ALIASES.get(k,".".join(x for x in k.split("_") if x))

def expected(rel):
 p=rel.parts;o={}
 if not p:return o
 if p[0]=="03_PEOPLES":
  o.update(domain="peoples",layer="reference" if "COMPARATIVE" in p else "world")
  if len(p)>=3 and p[1]=="CULTURES":
   o["continent"]=p[2].title()
   if len(p)>=4 and p[3]!="COMPARATIVE":o.update(people=p[3].title(),scope="people")
   elif len(p)>=4:o["scope"]="subject"
 elif p[0]=="02_ECOLOGY":
  o["domain"]="ecology";o["layer"]="tool" if any(x in rel.name.upper() for x in ("MATRIX","CREATION","PREDICTIVE","NECESSITY","PACKAGE")) else "world"
 elif p[0]=="01_WORLD":o.update(domain="world",layer="world")
 elif p[0]=="00_MASTER":o.update(domain="master",layer="reference")
 elif p[0]=="TOOLS":o.update(domain="repository",layer="tool")
 elif p[0]==ARCHIVE_TOP:o["layer"]="archive"
 return o

def normalized_status(raw):
 s=raw.strip().lower().rstrip(".")
 return STATUS_MAP.get(s,s)

def scan(root):
 docs=[];findings=[];texts={};n=1
 for path in sorted(root.rglob("*.md")):
  if any(x in IGNORE_DIRS for x in path.parts):continue
  rel=path.relative_to(root);text=path.read_text(encoding="utf-8",errors="replace");texts[str(rel)]=text
  fm=parse_frontmatter(text);exp=expected(rel);archive=bool(rel.parts and rel.parts[0]==ARCHIVE_TOP)
  raw_status=fm.get("status",inline_status(text));status=normalized_status(raw_status)
  d=Document(str(rel),path.name,fm.get("title",first_heading(text)),fm.get("id",""),fm.get("domain",exp.get("domain","")),fm.get("layer",exp.get("layer","")),fm.get("scope",""),status,fm.get("authority",""),fm.get("continent",exp.get("continent","")),fm.get("people",exp.get("people","")),fm.get("subject",subject_from_stem(path.stem)),archive);docs.append(d)
  if archive:continue
  if not d.id:findings.append(Finding(f"META-{n:04d}","WARNING","metadata",str(rel),"Missing stable document id.","Assign a stable ID when the document is next actively edited."));n+=1
  if not fm and not inline_status(text):findings.append(Finding(f"META-{n:04d}","WARNING","metadata",str(rel),"No recognized frontmatter or inline Status metadata.","Migrate metadata when actively editing; do not rewrite historical files."));n+=1
  if d.layer not in VALID_LAYERS:findings.append(Finding(f"META-{n:04d}","WARNING","metadata",str(rel),f"Unknown/missing layer: {d.layer or '<missing>'}.","Map to the repository schema."));n+=1
  if raw_status and status not in VALID_STATUS:findings.append(Finding(f"META-{n:04d}","INFO","status",str(rel),f"Unnormalized status: {raw_status}.","Map to the target status vocabulary when edited."));n+=1
  if d.authority and d.authority not in VALID_AUTHORITY:findings.append(Finding(f"META-{n:04d}","WARNING","authority",str(rel),f"Unknown authority: {d.authority}.","Map to the schema authority vocabulary."));n+=1
  for field in ("domain","layer","continent","people"):
   if field in exp and getattr(d,field) and getattr(d,field).lower()!=exp[field].lower():findings.append(Finding(f"PATH-{n:04d}","ERROR","path_metadata",str(rel),f"{field}={getattr(d,field)!r} conflicts with path expectation {exp[field]!r}.","Review path and metadata; do not auto-rewrite."));n+=1
  upper=path.stem.upper()
  if any(t in upper for t in ("FINAL","FINAL2","TEMP","NEW_","UPDATED")) or ("REVISION" in upper and "DEMOGRAPHIC_MOUNTAIN_REVISION.md" in path.name):
   findings.append(Finding(f"NAME-{n:04d}","WARNING","filename",str(rel),"Filename contains a production/temporary naming pattern.","Recommend a stable subject-based filename after collision/reference review."));n+=1
  if "COMPARATIVE" in rel.parts and not path.stem.endswith("_COMPARATIVE"):findings.append(Finding(f"NAME-{n:04d}","WARNING","filename",str(rel),"Comparative document is not explicitly marked in its filename.","Use <SUBJECT>_COMPARATIVE.md."));n+=1
 return docs,findings,texts

def semantic_claim_audit(docs,findings,texts):
 for code,old,new,msg,rec in KNOWN_CLAIMS:
  old_paths=[];new_paths=[]
  for d in docs:
   if d.archive:continue
   t=texts[d.path]
   if re.search(old,t,re.I):old_paths.append(d.path)
   if re.search(new,t,re.I):new_paths.append(d.path)
  if old_paths:findings.append(Finding(code,"WARNING","semantic_conflict",old_paths[0],msg,rec,"; ".join(new_paths) if new_paths else "Newer working model not yet found in active Markdown"))

def duplicate_audit(docs,findings):
 groups={}
 for d in docs:
  if d.archive:continue
  key=(d.continent.lower(),d.people.lower(),d.subject.lower(),d.scope.lower());groups.setdefault(key,[]).append(d)
 for i,(key,items) in enumerate(groups.items(),1):
  if len(items)>1 and key[2] and key[1] and not all("comparative" in x.path.lower() for x in items):findings.append(Finding(f"DUP-{i:04d}","WARNING","duplicate_subject",items[0].path,f"Multiple active documents appear to represent {key[2]!r} for {key[1]}.","Review authority/source-of-truth and legacy aliases.","; ".join(x.path for x in items)))

def write_reports(out,docs,findings):
 out.mkdir(parents=True,exist_ok=True)
 (out/"REPOSITORY_INDEX.md").write_text("# ARUUN Repository Index\n\nGenerated by read-only validator.\n\n| Path | ID | Layer | Scope | Status | Authority |\n|---|---|---|---|---|---|\n"+"\n".join(f"| `{d.path}` | `{d.id}` | `{d.layer}` | `{d.scope}` | `{d.status}` | `{d.authority}` |" for d in docs)+"\n",encoding="utf-8")
 naming="# ARUUN Naming Report\n\n"+"\n".join(f"## {f.id} — {f.severity}\n- **Path:** `{f.path}`\n- **Finding:** {f.message}\n- **Recommendation:** {f.recommendation}\n" for f in findings if f.category=="filename")+"\n"
 (out/"NAMING_REPORT.md").write_text(naming,encoding="utf-8")
 ledger="# ARUUN Discrepancy Ledger\n\nRead-only findings. Historical/archive occurrences are excluded from semantic conflict checks.\n\n"+"\n".join(f"## {f.id} — {f.severity}\n- **Category:** {f.category}\n- **Path:** `{f.path}`\n- **Finding:** {f.message}\n- **Recommendation:** {f.recommendation}\n- **Related:** {f.related or '—'}\n- **Status:** open\n" for f in findings if f.category!="filename")+"\n"
 (out/"DISCREPANCY_LEDGER.md").write_text(ledger,encoding="utf-8")
 e=sum(f.severity=="ERROR" for f in findings);w=sum(f.severity=="WARNING" for f in findings);i=sum(f.severity=="INFO" for f in findings)
 (out/"AUDIT_SUMMARY.md").write_text(f"# ARUUN Repository Audit Summary\n\n**Mode:** READ-ONLY\n\n| Metric | Count |\n|---|---:|\n| Documents scanned | {len(docs)} |\n| Findings | {len(findings)} |\n| Errors | {e} |\n| Warnings | {w} |\n| Info | {i} |\n",encoding="utf-8")

def main():
 p=argparse.ArgumentParser();p.add_argument("--root",default=".");p.add_argument("--out",default="TOOLS/REPOSITORY/REPORTS");a=p.parse_args();root=Path(a.root).resolve();out=(root/a.out).resolve() if not Path(a.out).is_absolute() else Path(a.out);docs,findings,texts=scan(root);semantic_claim_audit(docs,findings,texts);duplicate_audit(docs,findings);write_reports(out,docs,findings);print(f"Scanned {len(docs)} Markdown documents; generated {len(findings)} findings. Reports: {out}")
if __name__=="__main__":main()
