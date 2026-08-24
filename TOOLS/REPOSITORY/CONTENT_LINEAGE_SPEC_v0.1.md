# ARUUN Content Lineage & Consolidation Specification v0.1

## Purpose

Turn scattered drafts and rewrites into a reviewable subject lineage without losing information.

## Core rule

Multiple documents that appear to describe one subject are a **lineage**, not competing canon by default.

The engine must surface:

- source documents;
- sections present in each source;
- sections present in one source but absent from another;
- potentially changed sections;
- coarse similarity;
- unresolved status.

## Canon rule

The engine never selects a canonical winner. Current canon is established by the creator through the authoritative document and World Bible hierarchy.

## Preservation rule

No source is deleted or overwritten by this engine. After human consolidation, historical sources may be moved to Archive while remaining available for provenance and recovery.

## Decision vocabulary

- `KEEP` — source remains authoritative as-is.
- `MERGE` — contributions from multiple sources are consolidated into one authoritative document.
- `MOVE` — content belongs at a different repository location.
- `LINK` — source remains separate but should be explicitly referenced.
- `ARCHIVE` — source is superseded/historical after its useful content is preserved.
- `UNRESOLVED` — requires creator decision.

## Important limitation

Similarity is a discovery aid, not a semantic truth test. A high similarity score does not prove equivalence; a low score does not prove contradiction. Human review remains authoritative.
