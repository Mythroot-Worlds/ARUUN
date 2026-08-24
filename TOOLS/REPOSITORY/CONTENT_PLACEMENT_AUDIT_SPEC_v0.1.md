# ARUUN Content Placement Audit v0.1

## Purpose

The placement audit answers a different question from continuity:

> **Does this information appear to live in the repository location where it belongs?**

It is designed for source-preserving cleanup of legacy/random documents before consolidation.

## Non-negotiable rule

The audit **never moves, deletes, rewrites, or promotes content automatically**. It produces review candidates.

## Candidate classes

- `REGIONAL_PLACEMENT_CANDIDATE` — content strongly points to a Hearth region but lives outside that region's normal directory.
- `SUBJECT_PLACEMENT_CANDIDATE` — a known subject appears in a location/name that may not match the regional architecture.
- `LEGACY_FLAT_REGIONAL_FILE` — older flat files may contain material that should now be distributed into regional subject files.
- `TOOL_CANDIDATE` — content appears to describe a matrix, algorithm, formula, simulation, creation method, or other creator-facing machinery rather than ordinary lore.
- `METADATA_PATH_MISMATCH` — declared regional metadata disagrees with the repository path.
- `SUBJECT_LINEAGE_CLUSTER` — multiple active files appear to represent the same subject and should be reviewed as one lineage.

## Evidence model

The audit uses multiple signals rather than filename alone:

1. path and filename;
2. frontmatter when present;
3. regional names and ecological terms in the body;
4. known subject aliases;
5. repository architecture/schema;
6. whether the document is already a tool, reference, master, or archive layer.

A candidate is **not** a claim that the information is misplaced. It means the material deserves human review.

## Regional architecture

The target development pattern is one People/region per directory with one authoritative entry per subject. Comparative sheets remain reference products and do not replace regional sources.

## Tool distinction

Tools are world-package material, but they are separate from ordinary lore. Matrices, algorithms, formulas, simulations, creation packages, and design methods can be identified as `TOOL_CANDIDATE` without being treated as non-canonical. A tool may itself be an authoritative tool specification while remaining non-authoritative for the resulting world content.

## Cleanup workflow

```text
SOURCE DOCUMENT
      ↓
CONTENT PLACEMENT AUDIT
      ↓
CANDIDATE ROUTING
      ↓
HUMAN REVIEW
      ↓
EXTRACT / MERGE / RENAME / ARCHIVE
      ↓
CONTINUITY AUDIT
      ↓
CLEAN CANON
```

The original source remains available until its useful information has been deliberately reconciled and the creator approves archival treatment.

## Current ARUUN examples informing this layer

The repository already distinguishes world, tool, reference, audit, archive, and release layers. The Canon Index identifies `02_ECOLOGY` as the flora/fauna/ecology domain and identifies matrices and creation packages as supporting tools. The project operating rules likewise require repository-first research, preserve historical material, and establish one authoritative regional entry per subject.

This specification is therefore an implementation of the existing repository architecture, not a new canon rule.
