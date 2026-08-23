# ARUUN Document Migration — 2026-08-23

## Source reviewed

`ARUUN_DOCUMENT_MIGRATION_BUNDLE_2026-08-23.zip`

## Migration policy

This migration is source-preserving. It does not silently decide canon, reconcile contradictions, or delete historical versions.

The supplied repository table of contents establishes these roles:

- `00_MASTER/` — human-facing synthesis and authoritative overview
- `01_WORLD/` — physical/geographic world structure
- `02_ECOLOGY/` — flora, fauna, and ecological systems
- `03_PEOPLES/` — Aruunite species, demographics, and cultures
- `06_WORKING/` — active models that are not locked
- `07_ARCHIVE/` — historical snapshots, older versions, and source packages
- `08_RELEASES/` — controlled distributions
- `CHANGELOG.md` — meaningful worldbuilding decisions

## Current source-of-truth decisions identified in the bundle

- Planet/world name: **Aruun**; Mythroot remains the parent IP/umbrella.
- Current authoritative World Bible source: `MYTHROOT_PREHISTORIC_MASTER_WORLD_BIBLE_v1.5.md`.
- Earlier World Bible versions are historical snapshots and should remain archived.
- HPGL v0.3 is the current working population-geography reference.
- Lost isolation is approximately 700 million–1 billion years as a geological/evolutionary constraint, not a claim that Aruunites have been independently evolving there for that entire interval.
- Current working global human baseline is approximately 3.5–4 million, distributed across Hearth, Shattered, Rift, and Lost.
- Typical residential communities are approximately 80–150 people, with smaller and larger seasonal aggregations possible.
- The four continental identities are Hearth (connected abundance), Shattered (fragmentation/specialization), Rift (transition/instability), and Lost (deep-time independence).
- The project explicitly preserves standalone flora/fauna/matrix/reference documents rather than treating World Bible summaries as replacements.

## Important working-status rule

The bundle explicitly marks several models as working/provisional. In particular, the Mountain specialist-lineage revision is **not canon** merely because it appears in the source package.

## Migration execution note

The complete source package contains 72 top-level source files plus package contents. The branch for this migration is intentionally separate from `main`. The next migration pass should unpack the source material according to the supplied repository table of contents, preserving historical versions and package artifacts rather than flattening them into the current synthesis.
