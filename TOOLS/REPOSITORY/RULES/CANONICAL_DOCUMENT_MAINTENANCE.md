# CANONICAL DOCUMENT MAINTENANCE RULE

**Status:** CANONICAL REPOSITORY WORKFLOW RULE
**Purpose:** Prevent duplicate, competing, or version-suffixed active documents and preserve a clean knowledge base for CORE.

## Non-negotiable rule

**One subject = one active canonical file.**

When an existing canonical document needs new information, corrections, expansion, or refinement, update the existing file in place.

Do **not** create a second active copy merely because editing the original is inconvenient.

Avoid active filenames such as:

- `*_v2.md`
- `*_v3.md`
- `*_UPDATED.md`
- `*_FINAL.md`
- `*_FINAL2.md`
- `*_REVISED.md`
- `*_NEW.md`
- `*_WORKING.md`

unless the file is intentionally a distinct document with a distinct subject.

## Version history

**Git history is the version history.**

Do not encode ordinary revisions into active filenames. Git commits, diffs, and repository history preserve how a canonical document changed over time.

## Existing-file rule

Before creating a new document, check whether an active document already represents the same subject and scope.

If one exists:

1. update the existing document;
2. preserve its identity/path;
3. preserve its machine-readable ID when one exists;
4. update metadata if the document's scope or subject genuinely changes;
5. update dependent references when necessary.

If the existing file cannot safely be edited, **do not silently create a competing replacement**. Report the limitation and identify the existing file for controlled modification.

## Duplicate prevention

A document must not be duplicated simply because:

- a new batch of worldbuilding was created;
- a later conversation produced additional information;
- a document needs more sections;
- an audit discovered missing material;
- an AI workflow finds the original inconvenient to modify.

New information belongs in the existing authoritative document unless the information represents a genuinely different subject, scope, or layer.

## Supporting documents

Supporting, comparative, audit, and historical documents may exist alongside canonical documents, but they must be explicitly identifiable through path, metadata, and/or authority.

A supporting document must not silently become a competing source of truth.

When a supporting document records a decision that belongs in an authoritative source, the authoritative source should be updated rather than leaving the decision only in the supporting document.

## Deprecated material

When material is superseded, use Git history and the repository's established status/authority model. If an obsolete document must remain for historical reasons, mark it as historical/retired and ensure it cannot be mistaken for the current source of truth.

Do not maintain multiple active versions of the same canon merely to preserve history; Git already preserves that history.

## CORE compatibility principle

The repository is part of CORE's knowledge environment.

CORE should be able to determine, with minimal ambiguity:

**what the subject is → what its scope is → which file is authoritative → what supporting material exists → what historical material has been superseded.**

Duplicate active documents undermine retrieval, conflict resolution, learning, and recall. Therefore, canonical document identity and source-of-truth discipline take priority over convenience.

## Operational instruction for AI contributors

Before writing a new worldbuilding file:

> **SEARCH FIRST. IF THE SUBJECT ALREADY EXISTS AT THE SAME SCOPE, PATCH THE EXISTING CANONICAL FILE. DO NOT CREATE A DUPLICATE.**

If the intended change would require replacing, splitting, merging, or renaming an existing canonical document, stop and make that structural change explicit rather than creating an unofficial parallel version.
