# ARUUN Content Lineage & Consolidation Audit

**Mode:** READ-ONLY
**Scope:** `ALL_ACTIVE_NON_GENERATED_CONTENT`
**Lineage clusters:** 4

First-class document identity (subject + content type + scope) is resolved before lineage grouping. Regional siblings are compared as variants/contributors, not assumed to replace one another.

Human decisions only: `KEEP`, `MERGE`, `MOVE`, `LINK`, `ARCHIVE`, `UNRESOLVED

## readme (TOOLING)

### Sources
- `TOOLS/REPOSITORY/README.md` — `STRUCTURAL_IDENTITY`; scope `{'region': None, 'continent': None, 'regional_scope': False}`; role `AUTHORITATIVE`
- `TOOLS/REPOSITORY/RECONCILIATION/README.md` — `STRUCTURAL_IDENTITY`; scope `{'region': None, 'continent': None, 'regional_scope': False}`; role `AUTHORITATIVE`

### Compare: `TOOLS/REPOSITORY/README.md` ↔ `TOOLS/REPOSITORY/RECONCILIATION/README.md`
- Scope relation: **SAME_SCOPE**
- Overall similarity: **0.208**

**Human decision:** `UNRESOLVED`

## birth_childhood (CULTURE)

### Sources
- `03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md` — `STRUCTURAL_IDENTITY`; scope `{'region': None, 'continent': None, 'regional_scope': False}`; role `AUTHORITATIVE`
- `03_PEOPLES/CULTURES/HEARTH/COAST/FAMILY_BIRTH_CHILDHOOD.md` — `STRUCTURAL_IDENTITY`; scope `{'region': 'COAST', 'continent': None, 'regional_scope': True}`; role `AUTHORITATIVE`
- `03_PEOPLES/CULTURES/HEARTH/WETLANDS/FAMILY_BIRTH_CHILDHOOD.md` — `STRUCTURAL_IDENTITY`; scope `{'region': 'WETLANDS', 'continent': None, 'regional_scope': True}`; role `AUTHORITATIVE`
- `03_PEOPLES/CULTURES/HEARTH/PLAINS/FAMILY_BIRTH_CHILDHOOD.md` — `STRUCTURAL_IDENTITY`; scope `{'region': 'PLAINS', 'continent': None, 'regional_scope': True}`; role `AUTHORITATIVE`
- `03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md` — `STRUCTURAL_IDENTITY`; scope `{'region': 'RIVER', 'continent': None, 'regional_scope': True}`; role `AUTHORITATIVE`
- `03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md` — `STRUCTURAL_IDENTITY`; scope `{'region': 'DESERT', 'continent': None, 'regional_scope': True}`; role `AUTHORITATIVE`
- `03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md` — `STRUCTURAL_IDENTITY`; scope `{'region': None, 'continent': None, 'regional_scope': False}`; role `SUPPORTING`
- `03_PEOPLES/CULTURES/HEARTH/MOUNTAINS/FAMILY_BIRTH_CHILDHOOD.md` — `STRUCTURAL_IDENTITY`; scope `{'region': 'MOUNTAINS', 'continent': None, 'regional_scope': True}`; role `AUTHORITATIVE`

### Compare: `03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/COAST/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.404**

### Compare: `03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/WETLANDS/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.353**

### Compare: `03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/PLAINS/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.316**

### Compare: `03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.305**

### Compare: `03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.55**

### Compare: `03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md`
- Scope relation: **SAME_SCOPE**
- Overall similarity: **0.334**

### Compare: `03_PEOPLES/CULTURES/HEARTH/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/MOUNTAINS/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.305**

### Compare: `03_PEOPLES/CULTURES/HEARTH/COAST/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/WETLANDS/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.41**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 1
  - Unique to first: 6
  - Unique to second: 5
  - Possible conflicts: 1

### Compare: `03_PEOPLES/CULTURES/HEARTH/COAST/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/PLAINS/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.278**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 0
  - Unique to first: 7
  - Unique to second: 5
  - Possible conflicts: 0

### Compare: `03_PEOPLES/CULTURES/HEARTH/COAST/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.336**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 0
  - Unique to first: 7
  - Unique to second: 6
  - Possible conflicts: 0

### Compare: `03_PEOPLES/CULTURES/HEARTH/COAST/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.291**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 0
  - Unique to first: 7
  - Unique to second: 10
  - Possible conflicts: 0

### Compare: `03_PEOPLES/CULTURES/HEARTH/COAST/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.214**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 1
  - Unique to first: 6
  - Unique to second: 3
  - Possible conflicts: 1

### Compare: `03_PEOPLES/CULTURES/HEARTH/COAST/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/MOUNTAINS/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.301**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 0
  - Unique to first: 7
  - Unique to second: 6
  - Possible conflicts: 0

### Compare: `03_PEOPLES/CULTURES/HEARTH/WETLANDS/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/PLAINS/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.381**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 1
  - Unique to first: 5
  - Unique to second: 4
  - Possible conflicts: 1

### Compare: `03_PEOPLES/CULTURES/HEARTH/WETLANDS/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.408**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 0
  - Unique to first: 6
  - Unique to second: 6
  - Possible conflicts: 0

### Compare: `03_PEOPLES/CULTURES/HEARTH/WETLANDS/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.284**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 0
  - Unique to first: 6
  - Unique to second: 10
  - Possible conflicts: 0

### Compare: `03_PEOPLES/CULTURES/HEARTH/WETLANDS/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.277**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 1
  - Unique to first: 5
  - Unique to second: 3
  - Possible conflicts: 1

### Compare: `03_PEOPLES/CULTURES/HEARTH/WETLANDS/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/MOUNTAINS/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.311**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 0
  - Unique to first: 6
  - Unique to second: 6
  - Possible conflicts: 0

### Compare: `03_PEOPLES/CULTURES/HEARTH/PLAINS/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.375**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 0
  - Unique to first: 5
  - Unique to second: 6
  - Possible conflicts: 0

### Compare: `03_PEOPLES/CULTURES/HEARTH/PLAINS/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.243**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 0
  - Unique to first: 5
  - Unique to second: 10
  - Possible conflicts: 0

### Compare: `03_PEOPLES/CULTURES/HEARTH/PLAINS/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.26**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 1
  - Unique to first: 4
  - Unique to second: 3
  - Possible conflicts: 1

### Compare: `03_PEOPLES/CULTURES/HEARTH/PLAINS/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/MOUNTAINS/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.312**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 1
  - Unique to first: 4
  - Unique to second: 5
  - Possible conflicts: 1

### Compare: `03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.329**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 0
  - Unique to first: 6
  - Unique to second: 10
  - Possible conflicts: 0

### Compare: `03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.248**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 1
  - Unique to first: 5
  - Unique to second: 3
  - Possible conflicts: 1

### Compare: `03_PEOPLES/CULTURES/HEARTH/RIVER/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/MOUNTAINS/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.255**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 0
  - Unique to first: 6
  - Unique to second: 6
  - Possible conflicts: 0

### Compare: `03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.197**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 0
  - Unique to first: 10
  - Unique to second: 4
  - Possible conflicts: 0

### Compare: `03_PEOPLES/CULTURES/HEARTH/DESERT/FAMILY_BIRTH_CHILDHOOD.md` ↔ `03_PEOPLES/CULTURES/HEARTH/MOUNTAINS/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.26**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 1
  - Unique to first: 9
  - Unique to second: 5
  - Possible conflicts: 1

### Compare: `03_PEOPLES/CULTURES/HEARTH/COMPARATIVE/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md` ↔ `03_PEOPLES/CULTURES/HEARTH/MOUNTAINS/FAMILY_BIRTH_CHILDHOOD.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.215**
- **Section:** `birth_childhood_coming_of_age`
  - Shared/possible units: 1
  - Unique to first: 3
  - Unique to second: 5
  - Possible conflicts: 1

**Human decision:** `UNRESOLVED`

## 00_readme (ECOLOGY)

### Sources
- `02_ECOLOGY/FLORA/FLORA_CREATION_PACKAGE/00_README.md` — `STRUCTURAL_IDENTITY`; scope `{'region': None, 'continent': None, 'regional_scope': False}`; role `AUTHORITATIVE`
- `02_ECOLOGY/FAUNA/CREATURE_LIBRARY_CREATION_PACKAGE/00_README.md` — `STRUCTURAL_IDENTITY`; scope `{'region': None, 'continent': None, 'regional_scope': False}`; role `AUTHORITATIVE`

### Compare: `02_ECOLOGY/FLORA/FLORA_CREATION_PACKAGE/00_README.md` ↔ `02_ECOLOGY/FAUNA/CREATURE_LIBRARY_CREATION_PACKAGE/00_README.md`
- Scope relation: **SAME_SCOPE**
- Overall similarity: **0.193**

**Human decision:** `UNRESOLVED`

## dossier (GEOGRAPHY)

### Sources
- `01_WORLD/CONTINENTS/SHATTERED/DOSSIER.md` — `STRUCTURAL_IDENTITY`; scope `{'region': None, 'continent': 'SHATTERED', 'regional_scope': False}`; role `AUTHORITATIVE`
- `01_WORLD/CONTINENTS/RIFT/DOSSIER.md` — `STRUCTURAL_IDENTITY`; scope `{'region': None, 'continent': 'RIFT', 'regional_scope': False}`; role `AUTHORITATIVE`
- `01_WORLD/CONTINENTS/LOST/DOSSIER.md` — `STRUCTURAL_IDENTITY`; scope `{'region': None, 'continent': 'LOST', 'regional_scope': False}`; role `AUTHORITATIVE`

### Compare: `01_WORLD/CONTINENTS/SHATTERED/DOSSIER.md` ↔ `01_WORLD/CONTINENTS/RIFT/DOSSIER.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.407**
- **Section:** `artist_s_map_brief`
  - Shared/possible units: 0
  - Unique to first: 1
  - Unique to second: 1
  - Possible conflicts: 0
- **Section:** `ecological_identity`
  - Shared/possible units: 0
  - Unique to first: 0
  - Unique to second: 1
  - Possible conflicts: 0
- **Section:** `geographic_identity`
  - Shared/possible units: 0
  - Unique to first: 1
  - Unique to second: 1
  - Possible conflicts: 0
- **Section:** `geography_climate_reference_v0_1`
  - Shared/possible units: 1
  - Unique to first: 0
  - Unique to second: 0
  - Possible conflicts: 0
- **Section:** `major_geographic_structures`
  - Shared/possible units: 0
  - Unique to first: 2
  - Unique to second: 1
  - Possible conflicts: 0
- **Section:** `open_cartographic_details`
  - Shared/possible units: 1
  - Unique to first: 0
  - Unique to second: 0
  - Possible conflicts: 1
- **Section:** `water_system`
  - Shared/possible units: 0
  - Unique to first: 1
  - Unique to second: 1
  - Possible conflicts: 0

### Compare: `01_WORLD/CONTINENTS/SHATTERED/DOSSIER.md` ↔ `01_WORLD/CONTINENTS/LOST/DOSSIER.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.436**
- **Section:** `artist_s_map_brief`
  - Shared/possible units: 0
  - Unique to first: 1
  - Unique to second: 1
  - Possible conflicts: 0
- **Section:** `climate`
  - Shared/possible units: 0
  - Unique to first: 1
  - Unique to second: 1
  - Possible conflicts: 0
- **Section:** `ecological_identity`
  - Shared/possible units: 0
  - Unique to first: 0
  - Unique to second: 1
  - Possible conflicts: 0
- **Section:** `geographic_identity`
  - Shared/possible units: 0
  - Unique to first: 1
  - Unique to second: 2
  - Possible conflicts: 0
- **Section:** `geography_climate_reference_v0_1`
  - Shared/possible units: 1
  - Unique to first: 0
  - Unique to second: 0
  - Possible conflicts: 0
- **Section:** `major_geographic_structures`
  - Shared/possible units: 0
  - Unique to first: 2
  - Unique to second: 2
  - Possible conflicts: 0
- **Section:** `open_cartographic_details`
  - Shared/possible units: 1
  - Unique to first: 0
  - Unique to second: 0
  - Possible conflicts: 0

### Compare: `01_WORLD/CONTINENTS/RIFT/DOSSIER.md` ↔ `01_WORLD/CONTINENTS/LOST/DOSSIER.md`
- Scope relation: **REGIONAL_SIBLINGS**
- Overall similarity: **0.407**
- **Section:** `artist_s_map_brief`
  - Shared/possible units: 0
  - Unique to first: 1
  - Unique to second: 1
  - Possible conflicts: 0
- **Section:** `ecological_identity`
  - Shared/possible units: 0
  - Unique to first: 1
  - Unique to second: 1
  - Possible conflicts: 0
- **Section:** `geographic_identity`
  - Shared/possible units: 0
  - Unique to first: 1
  - Unique to second: 2
  - Possible conflicts: 0
- **Section:** `geography_climate_reference_v0_1`
  - Shared/possible units: 1
  - Unique to first: 0
  - Unique to second: 0
  - Possible conflicts: 0
- **Section:** `major_geographic_structures`
  - Shared/possible units: 0
  - Unique to first: 1
  - Unique to second: 2
  - Possible conflicts: 0
- **Section:** `open_cartographic_details`
  - Shared/possible units: 1
  - Unique to first: 0
  - Unique to second: 0
  - Possible conflicts: 0

**Human decision:** `UNRESOLVED`
