# Document Naming & Status Codes

**Status:** CANON  
**Effective:** 2026-08-25

## Purpose

ARUUN documents will use a consistent, machine-readable naming convention so CORE can identify scope, subject, and authority without relying entirely on document prose.

## Naming Convention

Use:

`[SCOPE]_[SUBJECT]_[STATUS]-[ID].md`

Example:

`RIVER_FAMILY_C-0001.md`

Where:

- `SCOPE` identifies the cultural/regional scope, such as `RIVER`.
- `SUBJECT` identifies the document subject, such as `FAMILY` or `LEADERSHIP`.
- `STATUS` identifies the authority state.
- `ID` is the unique record identifier and does **not** represent document version number.

## Status Codes

- `C` — **CANON**: human-approved setting truth.
- `P` — **PROVISIONAL**: accepted working material that is not yet locked.
- `O` — **OPEN**: intentionally unanswered or unresolved.
- `X` — **CONFLICTED**: competing information requires resolution.
- `D` — **DEPRECATED**: superseded material retained for historical/reference purposes.

Example set:

```text
RIVER_FAMILY_C-0001.md
RIVER_LEADERSHIP_C-0002.md
RIVER_BELIEF_P-0001.md
RIVER_SETTLEMENTS_O-0001.md
```

## Rules

1. **One subject = one active canonical file.**
2. Git history provides revision history; do not create `v2`, `FINAL`, `UPDATED`, etc. for ordinary revisions.
3. A record ID remains attached to its document; editing a document does not create a new ID.
4. Supporting documents must be clearly distinguishable from authoritative canon.
5. Deprecated material must not be treated as current canon.
6. Search for an existing document before creating one. If the same subject exists at the same scope, update the existing canonical file rather than creating a duplicate.
7. If an existing file cannot safely be edited, do not silently create a competing copy.
8. The document itself should repeat its identity/status in its metadata header so CORE can identify it even when the file is encountered outside its normal directory.

This convention is effective for new and subsequently normalized ARUUN documents. Existing files should be migrated only when they are intentionally edited or when a dedicated normalization pass is performed; do not create duplicates solely to rename files.
