# ARUUN — DOCUMENT MIGRATION TABLE OF CONTENTS

**Prepared:** 2026-08-23

**Purpose:** Migration aid for moving the existing Aruun worldbuilding material into the `Mythroot-Worlds/ARUUN` repository.

## Important

This bundle is a **source-preservation package**. It does not decide canon status, overwrite existing decisions, or silently reconcile contradictions.

The repository architecture should treat:
- `00_MASTER/` as human-facing synthesis;
- `01_WORLD/` as physical/geographic world structure;
- `02_ECOLOGY/` as flora/fauna/ecological systems;
- `03_PEOPLES/` as Aruunite/species/culture material;
- `06_WORKING/` for active models that have not been locked;
- `07_ARCHIVE/` for historical snapshots, old versions, and source packages;
- `08_RELEASES/` for controlled distributions.

Git history remains technical version history. `CHANGELOG.md` records meaningful worldbuilding decisions.

## Migration rules

- `MYTHROOT_PREHISTORIC_MASTER_WORLD_BIBLE_v1.5.md` becomes the current World Bible source for `00_MASTER/WORLD_BIBLE.md`.
- Earlier World Bible versions remain historical snapshots under `07_ARCHIVE/HISTORICAL/MASTER_WORLD_BIBLE/`.
- HPGL v0.3 is the current working population-geography reference; v0.1 and v0.2 remain historical.
- Current climate/ocean/tectonic references belong in `01_WORLD/`; historical versions remain archived.
- Canonical flora/fauna libraries remain standalone references under `02_ECOLOGY/`.
- Hearth cultural, demographic, family, leadership, and specialist-lineage material is separated by function; working revisions remain marked as working.
- Existing ZIP packages should be unpacked into their proper domains while preserving the original package as a source artifact where practical.
- Visual assets are intentionally outside this document-focused bundle and can be migrated separately.

## Current source categories

### Master
- Foundation world profile
- Current World Bible v1.5

### World
- Climate overlay
- Ocean and marine climate reference v0.2
- Climate/currents package
- Hearth geography and hydrology
- Sunscour oasis network
- Hearth, Lost, Rift, and Shattered continental dossiers
- Tectonic model v0.2

### Ecology
- Canonical creature library
- Faunal function matrix
- Creature necessity sheet
- Predictive evolution matrix
- Canonical flora library
- Edible flora expansion handoff/library
- Flora function matrix
- Flora creation package

### Peoples
- Human population geography layer v0.3
- Human evolution research track
- Hearth coastal, desert, plains, wetland, mountain, family, leadership, and demographic material

### Archive
- World Bible v0.1–v1.4
- HPGL v0.1–v0.2
- Tectonic model v0.1
- Ocean reference v0.1
- Project changelog additions
- Unclassified pack/milking/honey-insectoid design material

## Preservation rule

New versions preserve prior material. Nothing is intentionally deleted unless explicitly marked `RETIRED` or `SUPERSEDED`.
