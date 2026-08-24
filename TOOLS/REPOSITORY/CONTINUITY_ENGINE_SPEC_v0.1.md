# ARUUN Continuity Engine v0.1

## Purpose

Detect information loss and unintended scope drift when a canonical worldbuilding document is rewritten.

## Identity rule

Folder/scope is authoritative. Stable IDs and metadata strengthen identity. Filename and content similarity are supporting evidence only.

## Version rule

Git history is the version store. Rewriting a file does not erase prior states. Historical versions remain evidence until a creator reviews them.

## Findings

- PRESERVED — information appears in both versions.
- ADDED — information appears in the new version only.
- MODIFIED — existing information changed.
- POTENTIAL_CANON_LOSS — prior information is not detected in the current version.
- NUMERIC_CHANGE — numerical values changed and require review.
- SCOPE_MISMATCH — content appears inconsistent with the document's folder/scope.
- UNMATCHED — content cannot be reconciled with the expected subject lineage.

## Safety

The engine is read-only. It never decides canon, restores omitted information, renames files, moves files, archives files, or deletes files automatically.

## Consolidation lifecycle

`working -> review -> canonical -> superseded -> archive`

Only one active canonical document should represent a logical subject. Historical material remains recoverable and is excluded from current-canon resolution unless explicitly requested.
