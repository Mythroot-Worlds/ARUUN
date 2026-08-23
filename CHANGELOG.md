# Changelog

This changelog records **worldbuilding decisions and their meaning** — what was established or revised, why, and what it affects. It is separate from the Git commit log, which records the technical history of file changes.

Entries are listed newest first.

---

## 2026-08-23 — Migration Merged into Main; Canon Index and World Status Populated

### Decision
Merged the previously-unmerged `claude/git-push-kyp7tp` branch (which contained the full document migration) into `main`, and populated `00_MASTER/CANON_INDEX.md` and `00_MASTER/WORLD_STATUS.md` with the actual current state of the repository.

### Reason
`main` had been left on placeholder/scaffolding content while the real migrated material sat on an unmerged branch, so the repository did not reflect the true state of the world. The two master index files were also still placeholders despite substantive content existing elsewhere in the repo.

### Consequence
`main` is now the single source of truth reflecting all migrated Aruun material: World Bible v1.5, continental dossiers, canonical flora/fauna libraries, Hearth cultural material, and the full historical archive. `CANON_INDEX.md` and `WORLD_STATUS.md` now list real documents and real gaps (notably: no cultures yet for Shattered/Rift/Lost, `04_HISTORY` and `05_SYSTEMS` are entirely empty). Several duplicate migration/test branches remain on the remote from earlier attempts and should be cleaned up separately.

### Status
N/A — this is a repository/infrastructure decision, not a worldbuilding decision. No canon, working, or provisional world content was established or changed.

---

## 2026-08-23 — Document Migration Bundle Applied

### Decision
Migrated the existing Aruun/Mythroot source material (world profile, world bible history, climate, continental dossiers, flora/fauna libraries, Hearth cultural and demographic documents, and project changelogs) from the migration bundle into the domain directories, per `REPO_TABLE_OF_CONTENTS.md`'s proposed destinations.

### Reason
To make this repository the actual authoritative home for existing Aruun content, rather than a structure with only placeholder files.

### Consequence
- `00_MASTER/WORLD_BIBLE.md` and `00_MASTER/FOUNDATION_WORLD_PROFILE.md` are now populated from the latest available sources (World Bible v1.5; the Authoritative world profile).
- Superseded versions of versioned documents (World Bible v0.1–v1.4, HPGL v0.1–v0.2, tectonic model v0.1, ocean/marine climate v0.1, desert cultural base v0.1–v0.2, and the earlier world-concept seed) were preserved under `07_ARCHIVE/HISTORICAL/`, not deleted.
- Where two source documents were both mapped to the same destination and were not versions of the same document (e.g. Hearth geography overlays, Sunscour hydrology/oasis documents, Hearth family/partnership profiles, Hearth leadership/governance documents), they were combined into the destination file as clearly separated, source-attributed sections rather than editorially merged.
- `HEARTH_PEOPLES_MOUNTAIN_SPECIALIZATION_STRUCTURE_v0.1.md` was placed at `03_PEOPLES/CULTURES/HEARTH/MOUNTAINS/SPECIALIST_LINEAGES.md` and remains marked working/not canon, per the migration bundle's own note.
- Content ownership/canon status was **not** re-decided as part of this migration; each document's own status metadata (where present) was preserved as written.

### Status
N/A — this is a repository/infrastructure decision, not a worldbuilding decision. No canon, working, or provisional world content was created, reconciled, or overwritten by the migration itself.

---

## 2026-08-23 — Repository Structure Established

### Decision
Established the initial directory structure and configuration files for the Aruun source repository, per `ARUUN_REPOSITORY_STRUCTURE_INSTRUCTIONS.md`.

### Reason
To provide a stable, domain-organized home for Aruun source material so that "what is the current truth about Aruun?" can be answered by looking at this repository, rather than by searching prior conversations or uploads.

### Consequence
Future content migration and creation should be placed into the appropriate domain directory (`01_WORLD` through `08_RELEASES`) rather than collected into a single combined document.

### Status
N/A — this is a repository/infrastructure decision, not a worldbuilding decision. No canon, working, or provisional world content was established or changed.

---

## 2026-08-22 — Peoples Phase / Canon Consolidation

*Migrated from `MYTHROOT_PROJECT_CHANGELOG.md` during document migration.*

### 1. Planet Name Established
**Change:** The planet/world is now canonically named **Aruun**.

**Distinction:** **Mythroot** remains the LLC / parent IP umbrella and is not the planet name.

**Status:** LOCKED.

---

### 2. Lost Deep-Time Isolation Clarified
**Change:** Lost's geological/evolutionary isolation is established at approximately **700 million–1 billion years**.

**Important clarification:** This is the age of Lost's continental isolation, not automatically the amount of time that Aruunites themselves have been evolving independently there.

**Design intent:** Lost should be **deeply divergent but recognizable**, sharing deep ancestry with the rest of Aruun rather than becoming instantly alien.

**Status:** LOCKED SETTING CONSTRAINT.

---

### 3. Human Population Baseline Locked for Peoples Phase
**Global:** ~3.5–4 million.

- Hearth: ~1.5 million
- Shattered: ~800,000
- Rift: ~1.0 million
- Lost: ~300,000

**Status:** LOCKED WORKING DEMOGRAPHIC CANON.

---

### 4. Residential Community Model
**Change:** Typical residential communities remain approximately **80–150 people**, with smaller groups (~40–80) and larger seasonal aggregations (~200–500+) possible.

**Status:** LOCKED WORKING MODEL.

---

### 5. Continental Population Allocations Added
Current internal working allocations:

**Hearth**
- River valleys/floodplains: 25% / 375,000
- Grassland/woodland: 30% / 450,000
- Wetlands/lakes: 15% / 225,000
- Coasts: 12% / 180,000
- Highlands: 8% / 120,000
- Dry interior: 7% / 105,000
- Other/scattered seasonal: 3% / 45,000

**Shattered**
- Wet western/ocean fragments: 30% / 240,000
- Coastal productivity: 25% / 200,000
- Seasonal interior basins: 20% / 160,000
- Forest/woodland: 10% / 80,000
- Dry eastern fragments: 8% / 64,000
- Highlands: 5% / 40,000
- Peripheral islands: 2% / 16,000

**Rift**
- Rift-floor grasslands: 25% / 250,000
- Major lake margins: 20% / 200,000
- River corridors: 15% / 150,000
- Wetlands/floodplains: 15% / 150,000
- Highland valleys: 12% / 120,000
- Seasonal woodland/uplands: 7% / 70,000
- Dry basins/volcanic margins: 6% / 60,000

**Lost**
- Coastal networks: 38% / 114,000
- Grassland/plateau margins: 24% / 72,000
- Wetland/lake complexes: 10% / 30,000
- Highland valleys: 12% / 36,000
- Arid basins: 7% / 21,000
- Deep interior: 9% / 27,000

**Status:** LOCKED WORKING ALLOCATIONS for current Peoples development; fine settlement placement remains flexible.

---

### 6. Aruunite Continental Evolutionary Profiles Locked
Current working continental profiles:

**Hearth:** compact/robust, endurance-oriented, strong feet, high environmental awareness; regional climate effects generally modest because gene flow is strong and culture buffers many pressures.

**Rift:** terrain-adapted, powerful lower body/feet, strong climbing/scrambling capacity; highland populations can develop meaningful altitude/cold physiology.

**Shattered:** balance and aquatic competence, strong upper-body/shoulder emphasis in relevant populations; fragmentation creates higher regional divergence potential.

**Lost:** leaner/efficient gymnast-like movement, exceptional proprioception and environmental sensory integration; climate/isolation combinations can produce stronger regional specialization.

**Status:** LOCKED WORKING SPECIES FRAMEWORK.

---

### 7. Lost Climate Pass Completed
Major Lost climate/evolution zones evaluated:
- warm/moist coasts;
- cool/drier current-facing coasts;
- grassland/plateaus;
- mountain/highland valleys;
- wetlands/lakes;
- arid basins;
- deep interior.

Major candidate Lost population branches:
- coastal network;
- interior grassland/plateau;
- highland valleys;
- arid basins;
- isolated deep-interior branches.

**Status:** LOCKED WORKING EVOLUTIONARY/POPULATION FRAMEWORK.

---

### 8. Peoples Document Architecture Established
**World Bible:** broad knowledge / authoritative overview.

**Continental Cultural documents:** deep knowledge, structured similarly to the Continental Dossiers.

**Individual population/cultural profiles:** future deeper layer once a population is developed enough to justify its own document.

**Status:** LOCKED DOCUMENT ARCHITECTURE.

---

### 9. Standalone Reference Documents Retained
Flora, fauna, matrices, maps, HPGL, ecological cross-reference, and other specialized references remain standalone documents.

They are not secondary canon merely because the World Bible summarizes them.

**Status:** LOCKED PROJECT ARCHITECTURE.

---

### 10. Changelog Policy Established
A single changelog is maintained for project continuity.

Each substantive document revision must:
- advance its version;
- preserve the prior version as a historical snapshot;
- record the change here.

**Status:** LOCKED PROJECT PROCESS.

---

### 11. Edible Flora Expansion Handoff Created
A dedicated Markdown handoff was created for expansion of the flora library into plausible Aruunite edible plants.

It covers:
- grains/seeds;
- nuts/oils;
- roots/tubers;
- fruits;
- legumes;
- greens;
- fungi;
- fermentation;
- honey-like sweetener ecology;
- hydration plants;
- saline/mineral foods;
- domestication potential;
- toxicity/preparation;
- seasonality;
- regional coverage;
- flora-fauna relationships.

**Status:** HANDOFF COMPLETE / CLAUDE EXPANSION INPUT.

---

### 12. Domestication / Pack & Milking Animals
**Decision:** The setting should investigate **1–2 plausible domestication candidates**, preferably from the existing fauna library rather than inventing Earth-livestock analogues.

Criteria:
- behavioral compatibility;
- social structure;
- diet/carrying cost;
- 1.25g tolerance;
- reproductive/lactation biology;
- usefulness;
- ecological consequences;
- plausibility at the current technology stage.

**Status:** OPEN / NEXT RESEARCH PASS.

---

### Versioning Rule

The newest applicable version of a document is authoritative.

Older versions remain historical snapshots.

Do not silently overwrite substantive canon.
