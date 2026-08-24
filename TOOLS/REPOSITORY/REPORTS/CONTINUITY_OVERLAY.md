## 00_MASTER/CANON_INDEX.md — `b2e82c363aaf`

**Similarity:** 0.0835

### Preserved
- | 01 world/ | planet, continents, geography, climate, geology |
- | 02 ecology/ | flora, fauna, biomes, food webs, ecological models |
- | 03 peoples/ | species, cultures, societies, languages, demographics |
- | 04 history/ | timeline, eras, historical events |
- | 05 systems/ | magic, technology, economics, social systems |
- | 06 working/ | simulations, proposals, unresolved questions, experiments |
- | 07 archive/ | superseded material |
- | 08 releases/ | controlled distributions (internal, full, creator, player, licensed) |

### Added
- 02 ecology — libraries established, expansion open
- 03 peoples — hearth deep, others thin
- full historical version chain for the world bible (v0.1–v1.4), hpgl (v0.1–v0.2), tectonic model v0.1, ocean reference v0.1, changelog additions, and unclassified source material (pack/milking/honey insectoid design drafts). preserved per the "nothing deleted unless retired/superseded" rule.
- no content yet. magic, technology, economics, and social systems (beyond the hearth governance/family material filed under 03 peoples ) are unwritten. note: agriculture and domestication are explicitly not unlocked yet per the world bible (§15–16) — this is a deliberate open question, not an oversight.
- no content yet. timeline, eras, and historical events are entirely unwritten.
- no controlled distributions have been generated yet.
- no experiments, proposals, simulations, or unresolved questions docs have been filed here yet, though the world bible references several open questions (domestication candidates, lost's undeveloped population branches, etc.) that arguably belong here.
- this document indexes what is currently locked ( canon ) versus in progress ( working , provisional , open , or unknown ) across the repository, and points to where each subject lives. status labels here follow the world bible's canon status rule (locked canon / flexible provisional / open / unknown / working inference / retired).
- | climate/climate overlay.md , climate/ocean and marine climate reference.md | broad scaffold, exact values open. |
- | continents/hearth/ (dossier, hydrology, settlement overlay) | hearth continent structure — most detailed continent so far. |
- | continents/hearth/regions/sunscour oasis network.md | regional detail, working. |
- | continents/rift/dossier.md , continents/shattered/dossier.md , continents/lost/dossier.md | dossier level only — thinner than hearth, open for expansion. |
- | cultures/hearth/coast.md , desert.md , plains.md , wetlands.md | working cultural sub profiles. |
- | cultures/hearth/governance and authority.md , family partnership.md , family birth childhood.md | working social structure material. |
- | cultures/hearth/mountains/specialist lineages.md , demographic mountain revision.md | explicitly working, not canon — flagged in the source migration as not locked merely by inclusion. |
- | demographics/human population geography.md (hpgl v0.3) | current working population geography reference. |
- | fauna/canonical creature library.md | 34 canonical exemplars — locked as exemplars, not exhaustive. |
- | fauna/creature library creation package/ | process docs for adding new fauna. |
- | fauna/fauna function matrix.md , predictive evolution matrix.md , creature necessity sheet.md | supporting reference/qa tools. |
- | flora/canonical flora library.md | 30 canonical entries (13 signature). |

### Modified

### Potentially Dropped
- as content is migrated into each domain, list the substantive documents and their status here.
- this document indexes what is currently locked ( canon ) versus in progress ( working , provisional , open , or unknown ) across the repository, and points to where each subject lives.

### Unified Overlay
```diff
--- previous:b2e82c363aaf
+++ current
@@ -8,9 +8,7 @@
 
 # Aruun — Canon Index
 
-**Status:** placeholder, not yet populated.
-
-This document indexes what is currently locked (`canon`) versus in-progress (`working`, `provisional`, `open`, or `unknown`) across the repository, and points to where each subject lives.
+This document indexes what is currently locked (`canon`) versus in-progress (`working`, `provisional`, `open`, or `unknown`) across the repository, and points to where each subject lives. Status labels here follow the World Bible's canon-status rule (LOCKED CANON / FLEXIBLE-PROVISIONAL / OPEN / UNKNOWN / WORKING INFERENCE / RETIRED).
 
 ## Domain map
 
@@ -25,4 +23,61 @@
 | `07_ARCHIVE/` | Superseded material |
 | `08_RELEASES/` | Controlled distributions (internal, full, creator, player, licensed) |
 
-As content is migrated into each domain, list the substantive documents and their status here.
+## 00_MASTER — synthesis
+
+| Document | Status |
+|---|---|
+| `WORLD_BIBLE.md` (v1.5) | Current authoritative synthesis. Supersedes v0.1–v1.4 (archived). |
+| `FOUNDATION_WORLD_PROFILE.md` | LOCKED CANON — original world concept, foundation reference. |
+
+## 01_WORLD — locked/stable
+
+| Document | Status |
+|---|---|
+| `PLANET/TECTONICS.md` | Working model — 7-plate architecture, continental history. |
+| `CONTINENTS/HEARTH/*` (dossier, hydrology, settlement overlay) | Hearth continent structure — most detailed continent so far. |
+| `CONTINENTS/HEARTH/REGIONS/SUNSCOUR_OASIS_NETWORK.md` | Regional detail, working. |
+| `CONTINENTS/RIFT/DOSSIER.md`, `CONTINENTS/SHATTERED/DOSSIER.md`, `CONTINENTS/LOST/DOSSIER.md` | Dossier-level only — thinner than Hearth, open for expansion. |
+| `CLIMATE/CLIMATE_OVERLAY.md`, `CLIMATE/OCEAN_AND_MARINE_CLIMATE_REFERENCE.md` | Broad scaffold, exact values open. |
+
+## 02_ECOLOGY — libraries established, expansion open
+
+| Document | Status |
+|---|---|
+| `FAUNA/CANONICAL_CREATURE_LIBRARY.md` | 34 canonical exemplars — LOCKED as exemplars, not exhaustive. |
+| `FAUNA/FAUNA_FUNCTION_MATRIX.md`, `PREDICTIVE_EVOLUTION_MATRIX.md`, `CREATURE_NECESSITY_SHEET.md` | Supporting reference/QA tools. |
+| `FAUNA/CREATURE_LIBRARY_CREATION_PACKAGE/*` | Process docs for adding new fauna. |
+| `FLORA/CANONICAL_FLORA_LIBRARY.md` | 30 canonical entries (13 signature). |
+| `FLORA/EDIBLE_FLORA_LIBRARY.md`, `EDIBLE_FLORA_EXPANSION_HANDOFF.md` | Food-plant expansion track — open/active. |
+| `FLORA/FLORA_FUNCTION_MATRIX.md`, `FLORA_CREATION_MATRIX.md`, `FLORA_CREATION_PACKAGE/*` | Supporting reference/process docs. |
+
+## 03_PEOPLES — Hearth deep, others thin
+
+| Document | Status |
+|---|---|
+| `DEMOGRAPHICS/HUMAN_POPULATION_GEOGRAPHY.md` (HPGL v0.3) | Current working population-geography reference. |
+| `SPECIES/HUMAN_EVOLUTION_RESEARCH_TRACK.md` | Working research track. |
+| `CULTURES/HEARTH/COAST.md`, `DESERT.md`, `PLAINS.md`, `WETLANDS.md` | Working cultural sub-profiles. |
+| `CULTURES/HEARTH/GOVERNANCE_AND_AUTHORITY.md`, `FAMILY_PARTNERSHIP.md`, `FAMILY_BIRTH_CHILDHOOD.md` | Working social-structure material. |
+| `CULTURES/HEARTH/MOUNTAINS/SPECIALIST_LINEAGES.md`, `DEMOGRAPHIC_MOUNTAIN_REVISION.md` | **Explicitly WORKING, not canon** — flagged in the source migration as not locked merely by inclusion. |
+| Shattered, Rift, Lost — no `CULTURES/` content yet | OPEN. Only continent-level dossiers exist (see `01_WORLD`); no peoples/cultures have been developed for these three continents. |
+
+## 04_HISTORY — OPEN
+
+No content yet. Timeline, eras, and historical events are entirely unwritten.
+
+## 05_SYSTEMS — OPEN
+
+No content yet. Magic, technology, economics, and social-systems (beyond the Hearth governance/family material filed under `03_PEOPLES`) are unwritten. Note: agriculture and domestication are explicitly *not* unlocked yet per the World Bible (§15–16) — this is a deliberate open question, not an oversight.
+
+## 06_WORKING — empty
+
+No experiments, proposals, simulations, or unresolved-questions docs have been filed here yet, though the World Bible references several open questions (domestication candidates, Lost's undeveloped population branches, etc.) that arguably belong here.
+
+## 07_ARCHIVE — populated
+
+Full historical version chain for the World Bible (v0.1–v1.4), HPGL (v0.1–v0.2), tectonic model v0.1, ocean reference v0.1, changelog additions, and unclassified source material (pack/milking/honey-insectoid design drafts). Preserved per the "nothing deleted unless RETIRED/SUPERSEDED" rule.
+
+## 08_RELEASES — empty
+
+No controlled distributions have been generated yet.
```

## 00_MASTER/WORLD_BIBLE.md — `b2e82c363aaf`

**Similarity:** 0.0024

### Preserved

### Added
- 1. hearth — mostly intact great continent.
- 13. demographic / evolutionary divergence rule
- 17. canonical fauna & ecological integration
- 18. standalone document architecture
- 2. shattered — enormous continental fragments separated by major seas.
- 20. anachronism & internal coherence
- 3. rift — one great continental system actively splitting into two major halves.
- 4. lost — enormous continuous continent isolated by an immense ocean.
- 5. ocean circulation & marine climate
- 9. continental aruunite evolutionary profiles
- a community is not automatically a complete people.
- a dedicated edible flora expansion handoff has been created for expanding the flora library into plausible aruunite food plants, including staples, fruits, roots/tubers, legumes, oils/fats, fermentation substrates, sweetener systems, hydration plants, seasonality, toxicity, and domestication potential.
- a reasoned extrapolation used to make the current system function; not automatically canon.
- advanced ships and oceanic navigation are not assumed without a later technological pass.
- agriculture is not automatically unlocked merely because domestication compatible plants exist.
- an active working decision that may still change.
- an explored idea deliberately rejected.
- anachronism may be impossible; it must not be arbitrary.
- aruunite populations should be distinguishable without becoming fantasy races.
- aruunites remain predominantly upright/bipedal.

### Modified

### Potentially Dropped
- do not treat this file as complete or authoritative until it has been populated from migrated source material.
- this document is the human facing synthesis of aruun's established worldbuilding. it summarizes and cross references material that lives in the domain directories ( 01 world through 05 systems ); it is not itself the sole source of truth for any given subject.

### Unified Overlay
```diff
--- previous:b2e82c363aaf
+++ current
@@ -1,15 +1,755 @@
----
-world: Aruun
-domain: Master
-subject: World Bible
-status: open
-canonical: false
----
-
-# Aruun — World Bible
-
-**Status:** placeholder, not yet populated.
-
-This document is the human-facing synthesis of Aruun's established worldbuilding. It summarizes and cross-references material that lives in the domain directories (`01_WORLD` through `05_SYSTEMS`); it is not itself the sole source of truth for any given subject.
-
-Do not treat this file as complete or authoritative until it has been populated from migrated source material.
+# MYTHROOT — PREHISTORIC MASTER WORLD BIBLE
+## Preservation & Canon Update — v1.5
+
+**Status:** Current authoritative World Bible for development.
+
+**Source-preservation note:** v1.4 remains preserved as a historical snapshot. This v1.5 keeps all content present in the available v1.4 consolidation and restores/adds material identified in the v1.3 audit that should not have been lost.
+
+> **Versioning rule:** New versions preserve prior material. Nothing is intentionally deleted unless explicitly marked RETIRED/SUPERSEDED.
+
+---
+
+# CANON STATUS RULE
+
+### LOCKED CANON
+Explicitly established truth.
+
+### FLEXIBLE / PROVISIONAL
+An active working decision that may still change.
+
+### OPEN
+Not established and available for future development.
+
+### UNKNOWN
+Known to matter, but deliberately unexplained.
+
+### WORKING INFERENCE
+A reasoned extrapolation used to make the current system function; not automatically canon.
+
+### RETIRED
+An explored idea deliberately rejected.
+
+Later explicitly locked decisions supersede earlier conflicting seed material.
+
+---
+
+# 1. WORLD IDENTITY
+
+## Planet Name
+
+**ARUUN**
+
+The world/planet is now named Aruun.
+
+**Mythroot** is the LLC / parent IP umbrella and is not the planet's name.
+
+---
+
+# 2. PLANETARY FOUNDATION
+
+The established planetary framework remains:
+
+- ~1.25g gravity
+- 32-hour rotation/day
+- ~26° axial tilt
+- ~214 Earth-day orbital year
+- ~0.08 orbital eccentricity
+- warm K-type star
+- ~0.65 AU working orbital distance
+- ~70/30 land-water target
+- two substantial moons
+- four major continental systems
+
+The causal chain remains:
+
+**planetary parameters → atmosphere/circulation → geography → ocean circulation → climate → water systems → ecology → evolution → culture**
+
+Exact cartographic coordinates, precise climate boundaries, and other deliberately open parameters remain open where not explicitly locked.
+
+---
+
+# 3. TECTONIC WORLD MODEL
+
+The four major continental systems remain:
+
+1. **Hearth** — mostly intact great continent.
+2. **Shattered** — enormous continental fragments separated by major seas.
+3. **Rift** — one great continental system actively splitting into two major halves.
+4. **Lost** — enormous continuous continent isolated by an immense ocean.
+
+The established working seven-plate architecture remains:
+- Hearth Plate
+- Shatter-West Plate
+- Shatter-East Plate
+- Rift Crown Plate
+- Rift South Plate
+- Oceanic Ring Plate
+- Lost Plate
+
+### Geological history
+
+**Ancient continental assembly**
+→ volcanic arcs, accretion, collisions, stabilization
+
+**Supercontinental interval**
+→ broad ancestral continental complex
+
+**Lost separation**
+→ major rift succeeds, new oceanic crust forms, Lost begins long isolation
+
+**Main-cluster breakup**
+→ Hearth, Shattered, and Rift systems emerge
+
+**Shattering**
+→ overlapping rifts + transform/oblique motion + rotation + accretion create enormous fragments
+
+**Rift formation**
+→ continental crust thins, faults and basins form, volcanism increases, but full ocean formation has not yet occurred
+
+**Long reorganization**
+→ spreading, subduction, transform motion, accretion, uplift, erosion
+
+**Present**
+→ four continental systems remain active geological participants.
+
+### Lost isolation
+
+Lost has remained geographically/evolutionarily isolated for roughly:
+
+**700 million–1 billion years**
+
+This is a geological/evolutionary-history constraint.
+
+It does **not** mean that Aruunites themselves have necessarily been isolated for a billion years.
+
+The intended result is:
+
+> **Deep divergence without immediate alienness.**
+
+---
+
+# 4. GLOBAL CLIMATE MODEL
+
+Climate remains derived from planetary parameters plus geography.
+
+Major climate/environment categories include:
+- warm wet;
+- seasonal wet;
+- dry forest;
+- grassland;
+- semi-arid;
+- arid;
+- highland;
+- cool forest;
+- wetland;
+- riverine;
+- lake;
+- inland sea;
+- coastal;
+- marine;
+- volcanic/disturbed;
+- transitional.
+
+The existing climate overlay remains the authoritative broad climate scaffold.
+
+---
+
+# 5. OCEAN CIRCULATION & MARINE CLIMATE
+
+The ocean system follows the same causal philosophy as the terrestrial climate model:
+
+> **latitude → winds → currents → heat/moisture → upwelling → marine productivity → coastal climate → terrestrial ecology**
+
+Surface currents are driven primarily by global wind systems, modified by planetary rotation (Coriolis) and continental geometry.
+
+Established broad effects include:
+- moderated coasts;
+- warm and cool current regions;
+- wet and dry coastal climates;
+- storm corridors;
+- different climates around enclosed and semi-enclosed seas;
+- major fisheries near upwelling;
+- settlements near estuaries and river mouths;
+- seasonal coastal migrations;
+- navigation corridors;
+- dangerous current crossings;
+- fog hazards;
+- storm-exposed coasts;
+- coastal resource booms/crashes.
+
+Exact current speeds, temperatures, salinities, seasonal strength, and precise coastline intersections remain open until detailed mapping requires them.
+
+---
+
+# 6. ECOLOGY
+
+The canonical ecological framework remains:
+
+- 34 canonical fauna exemplars;
+- 30 canonical flora entries;
+- standalone flora/fauna matrices;
+- ecological cross-reference layer;
+- creature necessity / duplication safeguards.
+
+The ecosystem is intentionally larger than the canonical libraries.
+
+The libraries represent **well-understood exemplars**, not total biodiversity.
+
+### Ecological identity by continent
+
+**Hearth:** connected abundance and broad terrestrial food webs.
+
+**Shattered:** fragmentation and specialization.
+
+**Rift:** transition and instability.
+
+**Lost:** deep-time independence.
+
+---
+
+# 7. HUMANITY — ARUUNITES
+
+## Species identity
+
+The human-descended species currently being developed is the **Aruunites**.
+
+They remain a recognizable humanoid lineage shaped by:
+- ~1.25g gravity;
+- prehistoric megafaunal pressure;
+- climate;
+- food and water availability;
+- disease/pathogens;
+- mobility;
+- geographic isolation;
+- culture;
+- technology;
+- long-term gene flow patterns.
+
+### Species-level evolutionary principle
+
+> **Evolution solves the problems that remain after behavior and technology have done their work.**
+
+Culture and biology interact:
+
+**environment → behavior → culture/technology → modified selection pressure → residual biological adaptation**
+
+---
+
+# 8. ARUUNITE BASELINE
+
+The current species baseline is intentionally compact, robust, and athletic rather than bodybuilder-heavy.
+
+Working baseline:
+- approximate height: ~160–165 cm
+- approximate mass: ~67–72 kg
+- compact, structurally robust frame
+- powerful lower body
+- strong, broad, highly capable feet
+- high endurance
+- strong proprioception
+- strong environmental awareness
+- athletic musculature closer to a thick gymnast than a bodybuilder
+
+The distinctive feet are intentionally retained as a visible species characteristic.
+
+Aruunites remain predominantly upright/bipedal.
+
+Four-limb locomotion is not the normal adult gait.
+
+---
+
+# 9. CONTINENTAL ARUUNITE EVOLUTIONARY PROFILES
+
+## Hearth
+
+Core expression:
+
+> **Built to cross the world.**
+
+Typical traits:
+- compact/robust body;
+- powerful lower body;
+- high endurance;
+- strong feet;
+- environmental awareness;
+- high gene flow limiting extreme regional divergence.
+
+## Rift
+
+Core expression:
+
+> **Built to cross whatever is in front of them.**
+
+Typical traits:
+- strong lower body and feet;
+- exceptional balance;
+- climbing/scrambling competence;
+- high terrain awareness;
+- stronger regional divergence where altitude, rugged terrain, disease, and isolation persist.
+
+Highland populations are candidates for genuine oxygen/cold physiological specialization.
+
+## Shattered
+
+Core expression:
+
+> **Built to use and negotiate fragmented environments.**
+
+Typical traits:
+- strong balance;
+- capable upper body/shoulders in aquatic-resource populations;
+- excellent water competence;
+- strong proprioception;
+- regional variation driven by island/fragment isolation.
+
+Simple watercraft are plausible at the appropriate technological stage, but ships/open-ocean navigation are not assumed at the current pre-agricultural baseline.
+
+## Lost
+
+Core expression:
+
+> **Built for precision, efficiency, and adaptation.**
+
+Typical traits:
+- somewhat leaner/efficient body;
+- highly controlled movement;
+- exceptional proprioception;
+- strong environmental sensory integration;
+- slightly more prominent/sensitive eyes;
+- strong directional hearing;
+- enhanced smell;
+- regional specialization driven by isolation.
+
+The Lost baseline should remain recognizably Aruunite rather than becoming an alien humanoid.
+
+---
+
+# 10. HUMAN POPULATION GEOGRAPHY
+
+The standalone **HPGL v0.3** is now the detailed reference.
+
+## Global working population
+
+~3.5–4 million.
+
+- Hearth: ~1.5 million
+- Shattered: ~800,000
+- Rift: ~1.0 million
+- Lost: ~300,000
+
+## Community scale
+
+Typical residential community:
+
+**~80–150 people**
+
+Smaller groups:
+**~40–80**
+
+Larger seasonal aggregations:
+**~200–500+**
+
+A community is not automatically a complete people.
+
+## Population distribution
+
+### Hearth — 1.5 million
+- River valleys/floodplains: 25% / 375,000
+- Grassland/woodland: 30% / 450,000
+- Wetlands/lakes: 15% / 225,000
+- Coasts: 12% / 180,000
+- Highlands: 8% / 120,000
+- Dry interior/rain shadows: 7% / 105,000
+- Other/scattered seasonal: 3% / 45,000
+
+### Shattered — 800,000
+- Wet western/ocean fragments: 30% / 240,000
+- Coastal productivity: 25% / 200,000
+- Seasonal interior basins: 20% / 160,000
+- Forest/woodland: 10% / 80,000
+- Dry eastern fragments: 8% / 64,000
+- Highlands: 5% / 40,000
+- Peripheral islands: 2% / 16,000
+
+### Rift — 1 million
+- Rift-floor grasslands: 25% / 250,000
+- Major lake margins: 20% / 200,000
+- River corridors: 15% / 150,000
+- Wetlands/floodplains: 15% / 150,000
+- Highland valleys: 12% / 120,000
+- Seasonal woodland/uplands: 7% / 70,000
+- Dry basins/volcanic margins: 6% / 60,000
+
+### Lost — 300,000
+- Coastal networks: 38% / 114,000
+- Grassland/plateau margins: 24% / 72,000
+- Wetland/lake complexes: 10% / 30,000
+- Highland valleys: 12% / 36,000
+- Arid basins: 7% / 21,000
+- Deep interior: 9% / 27,000
+
+---
+
+# 11. HUMAN MOBILITY
+
+Aruunite movement may be:
+- sedentary;
+- seasonally mobile;
+- semi-nomadic;
+- fully nomadic;
+- herd-following;
+- plant-season following;
+- river/lake oriented;
+- coastal/water oriented;
+- mixed by season.
+
+### Watercraft boundary
+
+Pre-agricultural aquatic technology may progress through:
+- natural flotation;
+- floating logs;
+- simple rafts;
+- simple dugouts or equivalent craft when woodworking permits.
+
+Advanced ships and oceanic navigation are **not** assumed without a later technological pass.
+
+---
+
+# 12. PEOPLES & CULTURES
+
+## World Bible role
+
+The World Bible provides **broad knowledge** about peoples:
+- where they live;
+- broad population identity;
+- broad physical/ecological distinction;
+- major mobility pattern;
+- broad cultural role;
+- relationship to neighboring peoples.
+
+## Continental Cultural documents
+
+Each continent will receive a standalone deep-reference document structurally similar to the Continental Dossiers.
+
+These documents are equally important parts of the setting package.
+
+They will contain:
+- population overview;
+- demographic distribution;
+- environmental zones;
+- evolutionary profile;
+- physical characteristics;
+- regional variation;
+- food/subsistence;
+- water;
+- shelter;
+- mobility;
+- technology/materials;
+- social organization;
+- family/kinship;
+- child rearing;
+- group size/cooperation;
+- territory/resource rights;
+- trade/exchange;
+- conflict;
+- communication/language;
+- belief/spiritual framework;
+- material culture;
+- flora/fauna relationships;
+- relationships with other Aruunite populations;
+- historical development;
+- regional peoples/cultural branches;
+- open questions.
+
+---
+
+# 13. DEMOGRAPHIC / EVOLUTIONARY DIVERGENCE RULE
+
+Aruunite populations should be distinguishable without becoming fantasy races.
+
+Desired recognition gradient:
+
+**Continent:** reasonably guessable.
+
+**Major environmental ancestry:** often noticeable.
+
+**Exact population:** uncertain without contextual/cultural clues.
+
+Differences can appear through:
+- body proportions;
+- musculature;
+- gait;
+- feet/hands;
+- facial structure;
+- pigmentation;
+- eyes;
+- respiratory physiology;
+- thermoregulation;
+- metabolism;
+- sensory emphasis.
+
+Genetic, physiological, and morphological divergence are tracked separately.
+
+---
+
+# 14. LOST PEOPLE DEVELOPMENT RULE
+
+Lost climate zones have been evaluated.
+
+Major evolutionary population candidates:
+1. Coastal network
+2. Grassland/plateau interior
+3. Highland valleys
+4. Arid basins
+5. Isolated deep-interior branches
+
+Not every climate zone automatically becomes a separate people.
+
+The deciding variables are:
+
+**climate + resource base + mobility + barriers + population size + time + gene flow**
+
+Lost is where the greatest regional divergence is expected, but the shared Aruunite body plan remains recognizable.
+
+---
+
+# 15. FOOD & PLANT DEVELOPMENT
+
+The canonical flora library currently contains **30 entries**, including **13 signature entries**. The flora system is organized around ecological function rather than botanical completeness.
+
+The current library includes, among others:
+- Broadgrass
+- Marshreed
+- Riverweed
+- Duskroot
+- Stonemat
+- Bloomthorn
+- Hollowfruit
+- Deepshoal weed
+- Tideshrub
+- Crustbloom
+- Shoregrass
+- Thornbrush
+- Fragmentreed
+- Ashbloom
+- Driftweed
+- Valleymix
+- Faultscrub
+- Ashcolonizer
+- Rift reed-stand
+- Basinweed
+- Floodroot
+- Galleryhang
+- Plateautuft
+- Deeplichen
+- Mudmat
+- Driftplankton mat
+- Canopyveil
+- Basinsucculent
+- Marginbloom
+- Rootveil
+
+Background plant diversity exists beyond the 30 named entries.
+
+A dedicated edible-flora expansion handoff has been created for expanding the flora library into plausible Aruunite food plants, including staples, fruits, roots/tubers, legumes, oils/fats, fermentation substrates, sweetener systems, hydration plants, seasonality, toxicity, and domestication potential.
+
+### Agriculture status
+
+Agriculture is **not automatically unlocked** merely because domestication-compatible plants exist.
+
+Wild gathering, plant management, proto-domestication, and agriculture are distinct stages.
+
+---
+
+# 16. DOMESTICATION — OPEN NEXT PASS
+
+The setting should investigate **one or two plausible pack/milking domestication candidates**, preferably from existing fauna.
+
+Candidates must be evaluated for:
+- behavior;
+- social structure;
+- diet;
+- reproductive biology;
+- human handling;
+- load capacity;
+- milk production where relevant;
+- secondary products;
+- 1.25g tolerance;
+- ecological consequences;
+- technological plausibility;
+- whether domestication is actually useful before agriculture.
+
+Do not create an Earth cow/horse analogue unless the ecological pass independently justifies it.
+
+---
+
+# 17. CANONICAL FAUNA & ECOLOGICAL INTEGRATION
+
+The canonical fauna library contains **34 exemplars**.
+
+The fauna framework emphasizes:
+- ecological function before body plan;
+- meaningful convergent solutions;
+- large-animal ecological consequences;
+- dangerous but non-malevolent animals;
+- regional variants where justified;
+- Lost's independent evolutionary solutions;
+- cross-environment organisms that connect systems.
+
+The ecological cross-reference confirms strong established plant-fauna relationships, including:
+- Broadgrass → Broadback
+- Marshreed → Marshtread + Marshwing
+- Riverweed → Rivergrazer
+- Duskroot → Rootsnout
+- Stonemat → Ridgehorn
+- Bloomthorn → small burrowers → Duststriker
+- Hollowfruit → Rootsnout + Longjaw habitat
+- Deepshoal weed → fish analogues → Deepjaw
+
+Intentional convergence/divergence pairs include:
+- Broadback vs Basingrazer vs Plateauhorn
+- Ridgehorn vs Highvault vs Shellback
+- Shattered burrower vs Mudweaver
+- Bloomthorn vs Basinsucculent
+- Hearth Broadgrass vs Lost Plateautuft
+
+The canonical libraries are not the total biodiversity of Aruun.
+
+---
+
+# 18. STANDALONE DOCUMENT ARCHITECTURE
+
+The following remain standalone and equally important:
+- Master World Bible
+- Continental Dossiers
+- Continental Cultural documents
+- HPGL
+- Flora Function Matrix
+- Flora Creation Matrix
+- Canonical Flora Library
+- Fauna Function Matrix
+- Predictive Evolution Matrix
+- Creature Necessity Sheet
+- Canonical Creature Library
+- Ecological Cross-Reference
+- Maps
+- Project Changelog
+- specialized research/reference documents
+
+The World Bible summarizes what a creator needs to know while the standalone documents preserve depth.
+
+---
+
+# 19. MATRIX REFERENCE NOTE
+
+The standalone matrices are methodology documents.
+
+**Predictive Evolution Matrix:** uses continent + climate + function to identify plausible evolutionary solutions.
+
+**Flora Function / Creation Matrices:** identify ecological plant functions and turn environment + function + continent into plausible plant designs.
+
+**Fauna Function Matrix:** identifies ecological roles and constraints for creature creation.
+
+**Creature Necessity Sheet:** prevents redundant creature development and determines when the canonical library is “enough.”
+
+The matrices do not replace creative judgment.
+
+---
+
+# 20. ANACHRONISM & INTERNAL COHERENCE
+
+## Principle
+
+> **Anachronism may be impossible; it must not be arbitrary.**
+
+The setting may contain organisms or conditions that did not coexist in Earth's history.
+
+The exact mechanism remains **UNKNOWN / OPEN**.
+
+Do not assume:
+- time travel;
+- portals;
+- alternate Earth;
+- divine creation;
+- magical convergence;
+- evolutionary divergence;
+- another planet;
+
+unless later explicitly chosen.
+
+The working scientific/ecological design instead focuses on making coexistence internally coherent.
+
+---
+
+# 21. STORY-BUILDING PHILOSOPHY
+
+## Story density, not information density.
+
+A developed region may contain:
+- geography;
+- ecology;
+- peoples;
+- resources;
+- settlements;
+- history;
+- conflicts;
+- beliefs;
+- story opportunities.
+
+A distant region may remain:
+- a name;
+- rumor;
+- ecological description;
+- or blank space.
+
+Uneven depth is intentional.
+
+---
+
+# 22. CURRENT DEVELOPMENT STATUS
+
+## Established / Locked for current phase
+
+- Planet name: **Aruun**
+- Mythroot = parent LLC/IP umbrella
+- Four continents
+- Planetary/climate framework
+- Ocean/current framework
+- Flora and fauna libraries
+- Ecological cross-reference
+- Human population baseline
+- Continental population allocations
+- Aruunite baseline
+- Continental Aruunite evolutionary profiles
+- Lost deep-time isolation constraint
+- World Bible vs standalone-document architecture
+- Single changelog policy
+- Peoples-phase documentation architecture
+
+## Open / next major phase
+
+**PEOPLES → CULTURES → SUBSISTENCE → TECHNOLOGY → SOCIAL ORGANIZATION**
+
+The next documents to build are the **Continental Cultural documents**, beginning with Hearth.
+
+---
+
+# 23. CHANGE MANAGEMENT
+
+Substantive revisions must advance document versions.
+
+Older versions remain historical snapshots.
+
+The project maintains **one changelog** as the continuity record.
+
+Nothing canonical is intentionally deleted without a SUPERSEDED/RETIRED note.
+
+---
+
+# VERSION
+
+**v1.5 — Preservation Audit / Peoples Phase**
+
+This revision preserves the available v1.4 consolidation, restores v1.3-era material identified during audit, and adds current locked Peoples-phase canon.
+
+v1.4 remains preserved as a historical snapshot.
```

## 00_MASTER/WORLD_STATUS.md — `b2e82c363aaf`

**Similarity:** 0.0901

### Preserved

### Added
- 1. cultures for shattered, rift, and lost — right now only hearth has been built out; the other three continents are geography without people.
- 2. 04 history — no timeline exists at all yet. even a rough eras skeleton would give future content something to hang off of.
- 3. domestication pass — world bible flags 1–2 pack/milking candidates as an open next step (draft material exists in 07 archive/unclassified/ but hasn't been evaluated or promoted to canon).
- 4. resolve mountain (hearth) working material — specialist lineages and the mountain demographic revision are explicitly marked not yet canon and need a decision.
- 5. 06 working — start actually filing open questions there (lost's undeveloped population branches, agriculture timing, etc.) instead of leaving them buried in world bible prose.
- main previously contained only placeholder/scaffolding content — the actual migrated source material had been pushed to a branch ( claude/git push kyp7tp ) but never merged. that branch has now been merged into main . a number of duplicate migration/test branches from earlier attempts still exist on the remote and should be deleted once confirmed unnecessary.
- repository housekeeping note (2026 08 23)
- this document tracks the current development status of aruun at a glance. update it whenever a domain gets substantive new content, so "what's the current state?" can be answered without re reading the whole repo.
- | climate | broad scaffold in place; exact regional values open |
- | continents | hearth well developed (geography, hydrology, settlement, one region). shattered / rift / lost — dossier level only |
- | ecology (fauna) | 34 canonical exemplars + support matrices; not exhaustive by design |
- | ecology (flora) | 30 canonical entries + active edible flora expansion track |
- | history | empty — no timeline, eras, or events yet |
- | peoples — hearth culture | deepest cultural content: coast, desert, plains, wetlands, mountains (working), family/governance systems |
- | peoples — shattered/rift/lost culture | not started — biggest open gap |
- | peoples — species baseline | aruunite baseline established, plus per continent evolutionary profiles |
- | planet / physical world | established (gravity, day length, tilt, orbit, star, land/water ratio, moons, 7 plate tectonics) |
- | systems (magic/tech/economics) | empty — agriculture and domestication explicitly not yet unlocked |
- | working/unresolved | not yet tracked in 06 working/ despite several known open questions |

### Modified

### Potentially Dropped
- this document tracks the current development status of aruun at a glance — which domains have substantive content, which are still open, and what the near term priorities are. it should be updated as content is migrated and created.

### Unified Overlay
```diff
--- previous:b2e82c363aaf
+++ current
@@ -8,6 +8,32 @@
 
 # Aruun — World Status
 
-**Status:** placeholder, not yet populated.
+This document tracks the current development status of Aruun at a glance. Update it whenever a domain gets substantive new content, so "what's the current state?" can be answered without re-reading the whole repo.
 
-This document tracks the current development status of Aruun at a glance — which domains have substantive content, which are still open, and what the near-term priorities are. It should be updated as content is migrated and created.
+## At a glance
+
+| Domain | State |
+|---|---|
+| Planet / physical world | Established (gravity, day length, tilt, orbit, star, land/water ratio, moons, 7-plate tectonics) |
+| Continents | **Hearth** well-developed (geography, hydrology, settlement, one region). **Shattered / Rift / Lost** — dossier-level only |
+| Climate | Broad scaffold in place; exact regional values open |
+| Ecology (fauna) | 34 canonical exemplars + support matrices; not exhaustive by design |
+| Ecology (flora) | 30 canonical entries + active edible-flora expansion track |
+| Peoples — species baseline | Aruunite baseline established, plus per-continent evolutionary profiles |
+| Peoples — Hearth culture | Deepest cultural content: Coast, Desert, Plains, Wetlands, Mountains (working), family/governance systems |
+| Peoples — Shattered/Rift/Lost culture | **Not started** — biggest open gap |
+| History | **Empty** — no timeline, eras, or events yet |
+| Systems (magic/tech/economics) | **Empty** — agriculture and domestication explicitly not yet unlocked |
+| Working/unresolved | Not yet tracked in `06_WORKING/` despite several known open questions |
+
+## Near-term priorities (suggested)
+
+1. **Cultures for Shattered, Rift, and Lost** — right now only Hearth has been built out; the other three continents are geography without people.
+2. **04_HISTORY** — no timeline exists at all yet. Even a rough eras skeleton would give future content something to hang off of.
+3. **Domestication pass** — World Bible flags 1–2 pack/milking candidates as an open next step (draft material exists in `07_ARCHIVE/UNCLASSIFIED/` but hasn't been evaluated or promoted to canon).
+4. **Resolve Mountain (Hearth) working material** — specialist lineages and the mountain demographic revision are explicitly marked not-yet-canon and need a decision.
+5. **06_WORKING** — start actually filing open questions there (Lost's undeveloped population branches, agriculture timing, etc.) instead of leaving them buried in World Bible prose.
+
+## Repository housekeeping note (2026-08-23)
+
+`main` previously contained only placeholder/scaffolding content — the actual migrated source material had been pushed to a branch (`claude/git-push-kyp7tp`) but never merged. That branch has now been merged into `main`. A number of duplicate migration/test branches from earlier attempts still exist on the remote and should be deleted once confirmed unnecessary.
```

## CHANGELOG.md — `7a4e2c37ee5e`

**Similarity:** 0.931

### Preserved
- 00 master/world bible.md and 00 master/foundation world profile.md are now populated from the latest available sources (world bible v1.5; the authoritative world profile).
- 11. edible flora expansion handoff created
- 12. domestication / pack & milking animals
- 2. lost deep time isolation clarified
- 2026 08 22 — peoples phase / canon consolidation
- 2026 08 23 — document migration bundle applied
- 2026 08 23 — repository structure established
- 3. human population baseline locked for peoples phase
- 5. continental population allocations added
- 6. aruunite continental evolutionary profiles locked
- 8. peoples document architecture established
- 9. standalone reference documents retained
- a dedicated markdown handoff was created for expansion of the flora library into plausible aruunite edible plants.
- a single changelog is maintained for project continuity.
- change: lost's geological/evolutionary isolation is established at approximately 700 million–1 billion years .
- change: the planet/world is now canonically named aruun .
- change: typical residential communities remain approximately 80–150 people , with smaller groups (~40–80) and larger seasonal aggregations (~200–500+) possible.
- coastal productivity: 25% / 200,000
- content ownership/canon status was not re decided as part of this migration; each document's own status metadata (where present) was preserved as written.
- continental cultural documents: deep knowledge, structured similarly to the continental dossiers.

### Added
- 2026 08 23 — migration merged into main; canon index and world status populated
- main had been left on placeholder/scaffolding content while the real migrated material sat on an unmerged branch, so the repository did not reflect the true state of the world. the two master index files were also still placeholders despite substantive content existing elsewhere in the repo.
- main is now the single source of truth reflecting all migrated aruun material: world bible v1.5, continental dossiers, canonical flora/fauna libraries, hearth cultural material, and the full historical archive. canon index.md and world status.md now list real documents and real gaps (notably: no cultures yet for shattered/rift/lost, 04 history and 05 systems are entirely empty). several duplicate migration/test branches remain on the remote from earlier attempts and should be cleaned up separately.
- merged the previously unmerged claude/git push kyp7tp branch (which contained the full document migration) into main , and populated 00 master/canon index.md and 00 master/world status.md with the actual current state of the repository.

### Modified

### Potentially Dropped

### Unified Overlay
```diff
--- previous:7a4e2c37ee5e
+++ current
@@ -3,6 +3,22 @@
 This changelog records **worldbuilding decisions and their meaning** — what was established or revised, why, and what it affects. It is separate from the Git commit log, which records the technical history of file changes.
 
 Entries are listed newest first.
+
+---
+
+## 2026-08-23 — Migration Merged into Main; Canon Index and World Status Populated
+
+### Decision
+Merged the previously-unmerged `claude/git-push-kyp7tp` branch (which contained the full document migration) into `main`, and populated `00_MASTER/CANON_INDEX.md` and `00_MASTER/WORLD_STATUS.md` with the actual current state of the repository.
+
+### Reason
+`main` had been left on placeholder/scaffolding content while the real migrated material sat on an unmerged branch, so the repository did not reflect the true state of the world. The two master index files were also still placeholders despite substantive content existing elsewhere in the repo.
+
+### Consequence
+`main` is now the single source of truth reflecting all migrated Aruun material: World Bible v1.5, continental dossiers, canonical flora/fauna libraries, Hearth cultural material, and the full historical archive. `CANON_INDEX.md` and `WORLD_STATUS.md` now list real documents and real gaps (notably: no cultures yet for Shattered/Rift/Lost, `04_HISTORY` and `05_SYSTEMS` are entirely empty). Several duplicate migration/test branches remain on the remote from earlier attempts and should be cleaned up separately.
+
+### Status
+N/A — this is a repository/infrastructure decision, not a worldbuilding decision. No canon, working, or provisional world content was established or changed.
 
 ---
 
```

## CHANGELOG.md — `b2e82c363aaf`

**Similarity:** 0.1888

### Preserved
- 2026 08 23 — repository structure established
- established the initial directory structure and configuration files for the aruun source repository, per aruun repository structure instructions.md .
- future content migration and creation should be placed into the appropriate domain directory ( 01 world through 08 releases ) rather than collected into a single combined document.
- n/a — this is a repository/infrastructure decision, not a worldbuilding decision. no canon, working, or provisional world content was established or changed.
- this changelog records worldbuilding decisions and their meaning — what was established or revised, why, and what it affects. it is separate from the git commit log, which records the technical history of file changes.
- to provide a stable, domain organized home for aruun source material so that "what is the current truth about aruun?" can be answered by looking at this repository, rather than by searching prior conversations or uploads.

### Added
- 00 master/world bible.md and 00 master/foundation world profile.md are now populated from the latest available sources (world bible v1.5; the authoritative world profile).
- 11. edible flora expansion handoff created
- 12. domestication / pack & milking animals
- 2. lost deep time isolation clarified
- 2026 08 22 — peoples phase / canon consolidation
- 2026 08 23 — document migration bundle applied
- 2026 08 23 — migration merged into main; canon index and world status populated
- 3. human population baseline locked for peoples phase
- 5. continental population allocations added
- 6. aruunite continental evolutionary profiles locked
- 8. peoples document architecture established
- 9. standalone reference documents retained
- a dedicated markdown handoff was created for expansion of the flora library into plausible aruunite edible plants.
- a single changelog is maintained for project continuity.
- change: lost's geological/evolutionary isolation is established at approximately 700 million–1 billion years .
- change: the planet/world is now canonically named aruun .
- change: typical residential communities remain approximately 80–150 people , with smaller groups (~40–80) and larger seasonal aggregations (~200–500+) possible.
- coastal productivity: 25% / 200,000
- content ownership/canon status was not re decided as part of this migration; each document's own status metadata (where present) was preserved as written.
- continental cultural documents: deep knowledge, structured similarly to the continental dossiers.

### Modified

### Potentially Dropped

### Unified Overlay
```diff
--- previous:b2e82c363aaf
+++ current
@@ -3,6 +3,42 @@
 This changelog records **worldbuilding decisions and their meaning** — what was established or revised, why, and what it affects. It is separate from the Git commit log, which records the technical history of file changes.
 
 Entries are listed newest first.
+
+---
+
+## 2026-08-23 — Migration Merged into Main; Canon Index and World Status Populated
+
+### Decision
+Merged the previously-unmerged `claude/git-push-kyp7tp` branch (which contained the full document migration) into `main`, and populated `00_MASTER/CANON_INDEX.md` and `00_MASTER/WORLD_STATUS.md` with the actual current state of the repository.
+
+### Reason
+`main` had been left on placeholder/scaffolding content while the real migrated material sat on an unmerged branch, so the repository did not reflect the true state of the world. The two master index files were also still placeholders despite substantive content existing elsewhere in the repo.
+
+### Consequence
+`main` is now the single source of truth reflecting all migrated Aruun material: World Bible v1.5, continental dossiers, canonical flora/fauna libraries, Hearth cultural material, and the full historical archive. `CANON_INDEX.md` and `WORLD_STATUS.md` now list real documents and real gaps (notably: no cultures yet for Shattered/Rift/Lost, `04_HISTORY` and `05_SYSTEMS` are entirely empty). Several duplicate migration/test branches remain on the remote from earlier attempts and should be cleaned up separately.
+
+### Status
+N/A — this is a repository/infrastructure decision, not a worldbuilding decision. No canon, working, or provisional world content was established or changed.
+
+---
+
+## 2026-08-23 — Document Migration Bundle Applied
+
+### Decision
+Migrated the existing Aruun/Mythroot source material (world profile, world bible history, climate, continental dossiers, flora/fauna libraries, Hearth cultural and demographic documents, and project changelogs) from the migration bundle into the domain directories, per `REPO_TABLE_OF_CONTENTS.md`'s proposed destinations.
+
+### Reason
+To make this repository the actual authoritative home for existing Aruun content, rather than a structure with only placeholder files.
+
+### Consequence
+- `00_MASTER/WORLD_BIBLE.md` and `00_MASTER/FOUNDATION_WORLD_PROFILE.md` are now populated from the latest available sources (World Bible v1.5; the Authoritative world profile).
+- Superseded versions of versioned documents (World Bible v0.1–v1.4, HPGL v0.1–v0.2, tectonic model v0.1, ocean/marine climate v0.1, desert cultural base v0.1–v0.2, and the earlier world-concept seed) were preserved under `07_ARCHIVE/HISTORICAL/`, not deleted.
+- Where two source documents were both mapped to the same destination and were not versions of the same document (e.g. Hearth geography overlays, Sunscour hydrology/oasis documents, Hearth family/partnership profiles, Hearth leadership/governance documents), they were combined into the destination file as clearly separated, source-attributed sections rather than editorially merged.
+- `HEARTH_PEOPLES_MOUNTAIN_SPECIALIZATION_STRUCTURE_v0.1.md` was placed at `03_PEOPLES/CULTURES/HEARTH/MOUNTAINS/SPECIALIST_LINEAGES.md` and remains marked working/not canon, per the migration bundle's own note.
+- Content ownership/canon status was **not** re-decided as part of this migration; each document's own status metadata (where present) was preserved as written.
+
+### Status
+N/A — this is a repository/infrastructure decision, not a worldbuilding decision. No canon, working, or provisional world content was created, reconciled, or overwritten by the migration itself.
 
 ---
 
@@ -19,3 +55,208 @@
 
 ### Status
 N/A — this is a repository/infrastructure decision, not a worldbuilding decision. No canon, working, or provisional world content was established or changed.
+
+---
+
+## 2026-08-22 — Peoples Phase / Canon Consolidation
+
+*Migrated from `MYTHROOT_PROJECT_CHANGELOG.md` during document migration.*
+
+### 1. Planet Name Established
+**Change:** The planet/world is now canonically named **Aruun**.
+
+**Distinction:** **Mythroot** remains the LLC / parent IP umbrella and is not the planet name.
+
+**Status:** LOCKED.
+
+---
+
+### 2. Lost Deep-Time Isolation Clarified
+**Change:** Lost's geological/evolutionary isolation is established at approximately **700 million–1 billion years**.
+
+**Important clarification:** This is the age of Lost's continental isolation, not automatically the amount of time that Aruunites themselves have been evolving independently there.
+
+**Design intent:** Lost should be **deeply divergent but recognizable**, sharing deep ancestry with the rest of Aruun rather than becoming instantly alien.
+
+**Status:** LOCKED SETTING CONSTRAINT.
+
+---
+
+### 3. Human Population Baseline Locked for Peoples Phase
+**Global:** ~3.5–4 million.
+
+- Hearth: ~1.5 million
+- Shattered: ~800,000
+- Rift: ~1.0 million
+- Lost: ~300,000
+
+**Status:** LOCKED WORKING DEMOGRAPHIC CANON.
+
+---
+
+### 4. Residential Community Model
+**Change:** Typical residential communities remain approximately **80–150 people**, with smaller groups (~40–80) and larger seasonal aggregations (~200–500+) possible.
+
+**Status:** LOCKED WORKING MODEL.
+
+---
+
+### 5. Continental Population Allocations Added
+Current internal working allocations:
+
+**Hearth**
+- River valleys/floodplains: 25% / 375,000
+- Grassland/woodland: 30% / 450,000
+- Wetlands/lakes: 15% / 225,000
+- Coasts: 12% / 180,000
+- Highlands: 8% / 120,000
+- Dry interior: 7% / 105,000
+- Other/scattered seasonal: 3% / 45,000
+
+**Shattered**
+- Wet western/ocean fragments: 30% / 240,000
+- Coastal productivity: 25% / 200,000
+- Seasonal interior basins: 20% / 160,000
+- Forest/woodland: 10% / 80,000
+- Dry eastern fragments: 8% / 64,000
+- Highlands: 5% / 40,000
+- Peripheral islands: 2% / 16,000
+
+**Rift**
+- Rift-floor grasslands: 25% / 250,000
+- Major lake margins: 20% / 200,000
+- River corridors: 15% / 150,000
+- Wetlands/floodplains: 15% / 150,000
+- Highland valleys: 12% / 120,000
+- Seasonal woodland/uplands: 7% / 70,000
+- Dry basins/volcanic margins: 6% / 60,000
+
+**Lost**
+- Coastal networks: 38% / 114,000
+- Grassland/plateau margins: 24% / 72,000
+- Wetland/lake complexes: 10% / 30,000
+- Highland valleys: 12% / 36,000
+- Arid basins: 7% / 21,000
+- Deep interior: 9% / 27,000
+
+**Status:** LOCKED WORKING ALLOCATIONS for current Peoples development; fine settlement placement remains flexible.
+
+---
+
+### 6. Aruunite Continental Evolutionary Profiles Locked
+Current working continental profiles:
+
+**Hearth:** compact/robust, endurance-oriented, strong feet, high environmental awareness; regional climate effects generally modest because gene flow is strong and culture buffers many pressures.
+
+**Rift:** terrain-adapted, powerful lower body/feet, strong climbing/scrambling capacity; highland populations can develop meaningful altitude/cold physiology.
+
+**Shattered:** balance and aquatic competence, strong upper-body/shoulder emphasis in relevant populations; fragmentation creates higher regional divergence potential.
+
+**Lost:** leaner/efficient gymnast-like movement, exceptional proprioception and environmental sensory integration; climate/isolation combinations can produce stronger regional specialization.
+
+**Status:** LOCKED WORKING SPECIES FRAMEWORK.
+
+---
+
+### 7. Lost Climate Pass Completed
+Major Lost climate/evolution zones evaluated:
+- warm/moist coasts;
+- cool/drier current-facing coasts;
+- grassland/plateaus;
+- mountain/highland valleys;
+- wetlands/lakes;
+- arid basins;
+- deep interior.
+
+Major candidate Lost population branches:
+- coastal network;
+- interior grassland/plateau;
+- highland valleys;
+- arid basins;
+- isolated deep-interior branches.
+
+**Status:** LOCKED WORKING EVOLUTIONARY/POPULATION FRAMEWORK.
+
+---
+
+### 8. Peoples Document Architecture Established
+**World Bible:** broad knowledge / authoritative overview.
+
+**Continental Cultural documents:** deep knowledge, structured similarly to the Continental Dossiers.
+
+**Individual population/cultural profiles:** future deeper layer once a population is developed enough to justify its own document.
+
+**Status:** LOCKED DOCUMENT ARCHITECTURE.
+
+---
+
+### 9. Standalone Reference Documents Retained
+Flora, fauna, matrices, maps, HPGL, ecological cross-reference, and other specialized references remain standalone documents.
+
+They are not secondary canon merely because the World Bible summarizes them.
+
+**Status:** LOCKED PROJECT ARCHITECTURE.
+
+---
+
+### 10. Changelog Policy Established
+A single changelog is maintained for project continuity.
+
+Each substantive document revision must:
+- advance its version;
+- preserve the prior version as a historical snapshot;
+- record the change here.
+
+**Status:** LOCKED PROJECT PROCESS.
+
+---
+
+### 11. Edible Flora Expansion Handoff Created
+A dedicated Markdown handoff was created for expansion of the flora library into plausible Aruunite edible plants.
+
+It covers:
+- grains/seeds;
+- nuts/oils;
+- roots/tubers;
+- fruits;
+- legumes;
+- greens;
+- fungi;
+- fermentation;
+- honey-like sweetener ecology;
+- hydration plants;
+- saline/mineral foods;
+- domestication potential;
+- toxicity/preparation;
+- seasonality;
+- regional coverage;
+- flora-fauna relationships.
+
+**Status:** HANDOFF COMPLETE / CLAUDE EXPANSION INPUT.
+
+---
+
+### 12. Domestication / Pack & Milking Animals
+**Decision:** The setting should investigate **1–2 plausible domestication candidates**, preferably from the existing fauna library rather than inventing Earth-livestock analogues.
+
+Criteria:
+- behavioral compatibility;
+- social structure;
+- diet/carrying cost;
+- 1.25g tolerance;
+- reproductive/lactation biology;
+- usefulness;
+- ecological consequences;
+- plausibility at the current technology stage.
+
+**Status:** OPEN / NEXT RESEARCH PASS.
+
+---
+
+### Versioning Rule
+
+The newest applicable version of a document is authoritative.
+
+Older versions remain historical snapshots.
+
+Do not silently overwrite substantive canon.
```

## TOOLS/REPOSITORY/CONTINUITY_TEST/CONTINUITY_TEST.md — `e6350894e350`

**Similarity:** 0.9331

### Preserved
- they use pack animals for transport .
- this document is deliberately disposable. it exists only to test git history continuity detection.
- when this file is deliberately rewritten, the continuity engine should identify preserved information, additions, modifications, and potentially dropped information. this fixture is not canon.

### Added

### Modified
- the mountain people maintain three seasonal camps . → the mountain people maintain two seasonal camps .

### Potentially Dropped
- elders teach children through observation and practice.

### Unified Overlay
```diff
--- previous:e6350894e350
+++ current
@@ -4,11 +4,9 @@
 
 ## Baseline facts
 
-The mountain people maintain **three seasonal camps**.
+The mountain people maintain **two seasonal camps**.
 
 They use **pack animals for transport**.
-
-**Elders teach children through observation and practice.**
 
 ## Expected test behavior
 
```

## TOOLS/REPOSITORY/README.md — `af46af0b20cc`

**Similarity:** 0.1076

### Preserved

### Added
- audit summary.md — high level counts.
- discrepancy ledger.md — metadata, path, status, authority, and duplicate findings.
- it does not rename files, rewrite canon, or silently resolve discrepancies.
- metadata presence and normalization;
- naming report.md — filename/path findings and rename recommendations.
- python tools/repository/validate repo.py
- python tools/repository/validate repo.py out tools/repository/reports
- read only repository auditor. it scans markdown documents across the repository, including files whose names do not advertise their subject, and checks:
- repository index.md — every scanned markdown document and inferred identity.
- repository maintenance and validation tooling for aruun. tools are part of the world package but remain separate from ordinary lore: they explain and validate how the world is built without dictating what creators must create.
- target metadata, naming, path, authority, dependency, world bible, comparative sheet, and tool layer schema.
- temporary/batch/legacy naming patterns;
- the validator is therefore a qa instrument and world building tool , not a canon engine.
- the validator reports problems; the creative director decides what happens next. a finding can be corrected, accepted as intentional, deferred, or recorded as a canon decision.

### Modified

### Potentially Dropped
- document classification and authority validation
- duplicate/competing authority detection
- see the project operating rules at /project operating rules.md for the repository first and authority rules.
- the validator should report problems, not silently rewrite canon. a human/creator decides whether a reported discrepancy is corrected, accepted, deferred, or intentionally retained.
- this directory contains repository maintenance and validation tooling. tools are part of the aruun world package but do not dictate canon; they validate structure, metadata, dependencies, and consistency.
- world bible/deep entry relationship checks

### Unified Overlay
```diff
--- previous:af46af0b20cc
+++ current
@@ -1,22 +1,49 @@
 # ARUUN Repository Tooling
 
-This directory contains repository-maintenance and validation tooling. Tools are part of the ARUUN world package but do not dictate canon; they validate structure, metadata, dependencies, and consistency.
+Repository-maintenance and validation tooling for ARUUN. Tools are part of the world package but remain separate from ordinary lore: they explain and validate how the world is built without dictating what creators must create.
 
-## Planned validation layers
+## Current tooling
 
-- Frontmatter/tag validation
-- Document classification and authority validation
-- Scope/path validation
-- Required metadata validation
-- Duplicate/competing-authority detection
-- Cross-reference validation
-- Superseded-value detection
-- World-Bible/deep-entry relationship checks
-- Tool-to-world dependency checks
-- Comparative-sheet source checks
+### `ARUUN_REPOSITORY_SCHEMA_v0.1.md`
+Target metadata, naming, path, authority, dependency, World Bible, comparative-sheet, and tool-layer schema.
 
-## Principle
+### `validate_repo.py`
+Read-only repository auditor. It scans Markdown documents across the repository, including files whose names do not advertise their subject, and checks:
 
-The validator should report problems, not silently rewrite canon. A human/creator decides whether a reported discrepancy is corrected, accepted, deferred, or intentionally retained.
+- metadata presence and normalization;
+- path ↔ metadata consistency;
+- layer/scope mismatches;
+- filename conventions;
+- temporary/batch/legacy naming patterns;
+- comparative naming;
+- duplicate subject identities;
+- archive separation.
 
-See the project operating rules at `/PROJECT_OPERATING_RULES.md` for the repository-first and authority rules.
+It does **not** rename files, rewrite canon, or silently resolve discrepancies.
+
+## Running the audit
+
+From the repository root:
+
+```bash
+python TOOLS/REPOSITORY/validate_repo.py
+```
+
+Optional output location:
+
+```bash
+python TOOLS/REPOSITORY/validate_repo.py --out TOOLS/REPOSITORY/REPORTS
+```
+
+## Generated reports
+
+- `AUDIT_SUMMARY.md` — high-level counts.
+- `REPOSITORY_INDEX.md` — every scanned Markdown document and inferred identity.
+- `NAMING_REPORT.md` — filename/path findings and rename recommendations.
+- `DISCREPANCY_LEDGER.md` — metadata, path, status, authority, and duplicate findings.
+
+## Operating principle
+
+The validator reports problems; the Creative Director decides what happens next. A finding can be corrected, accepted as intentional, deferred, or recorded as a canon decision.
+
+The validator is therefore a **QA instrument and world-building tool**, not a canon engine.
```
