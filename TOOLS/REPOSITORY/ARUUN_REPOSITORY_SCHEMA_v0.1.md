# ARUUN REPOSITORY SCHEMA v0.1

**Status:** WORKING TOOL SPECIFICATION
**Purpose:** Define the metadata, naming, classification, path, and dependency rules that the ARUUN repository validator will use.

> This schema describes the world repository. It does not dictate world canon. Tools report structural or consistency problems; the Creative Director decides whether a reported issue becomes a correction, an intentional exception, a deferred item, or a canon change.

---

## 1. Core principle

Every active ARUUN document should be identifiable without opening it:

**what it is → where it belongs → what it describes → what authority it has → what it depends on → what depends on it.**

The validator must inspect both **metadata and filename/path**. A correctly tagged document in the wrong directory is still an error. A correctly located document with a misleading filename is still an error.

The validator must flag document names even when the content itself is valid.

---

## 2. Required metadata model

New or migrated active Markdown documents should use YAML frontmatter following this conceptual schema:

```yaml
---
id: hearth.plains.family.birth_childhood
title: Plains — Birth, Childhood & Coming-of-Age
domain: peoples
layer: world
scope: regional
status: canon
authority: regional
world: Aruun
continent: Hearth
people: Plains
subject: family.birth_childhood
parent: hearth.plains
source_of_truth: true
references: []
depends_on: []
used_by: []
---
```

### Required fields

| Field | Purpose |
|---|---|
| `id` | Stable machine-readable identity. Must be unique. |
| `title` | Human-readable document title. |
| `domain` | Major repository domain. |
| `layer` | World, tool, reference, audit, archive, or release. |
| `scope` | World, continent, region, people, subject, or system scope. |
| `status` | Current content status. |
| `authority` | Whether this file is authoritative, supporting, comparative, or historical. |
| `world` | World identity; currently `Aruun` for world material. |

### Conditional fields

These become required when the scope makes them applicable:

- `continent` for continent/region/people material;
- `people` for People-specific material;
- `subject` for subject-level entries;
- `parent` for nested world entries;
- `tool_scope` for creator/tool documents;
- `source_of_truth` for files that can serve as authoritative sources.

### Dependency fields

- `references`: documents consulted or cited but not required for the file's existence;
- `depends_on`: documents whose substantive decisions constrain this file;
- `used_by`: known downstream documents or generated/reference layers.

These should use stable document IDs when the referenced documents have IDs.

---

## 3. Status vocabulary

The validator recognizes the existing ARUUN status model and the project operating distinctions.

### World/content status

- `canon` — established current world state;
- `working_model` — current development model not yet locked;
- `inference` — derived but not explicitly established;
- `proposal` — suggested material awaiting acceptance;
- `open` — intentionally undeveloped;
- `unknown` — known to matter but deliberately unresolved;
- `retired` — deliberately rejected/superseded historical content.

### Layer is separate from status

A tool can be `canon` as a **tool specification** without dictating world canon.

A reference sheet can be `canon_reference` while remaining non-authoritative for the underlying subject.

The validator must never infer world authority solely from the word `canon`.

---

## 4. Layer vocabulary

The repository distinguishes the following functional layers:

| Layer | Meaning |
|---|---|
| `world` | Built world content: what exists in Aruun. |
| `tool` | World-building machinery: matrices, algorithms, formulas, simulations, generation methods. |
| `reference` | Compiled/comparative/navigation material derived from authoritative sources. |
| `audit` | QA, discrepancy, coverage, or validation material. |
| `archive` | Historical/superseded development material. |
| `release` | Controlled packaged distribution. |

**Tools are part of the ARUUN world package.** They are separated because they explain/build the world rather than serving as ordinary lore presentation.

Tools help creators build; they do not dictate creative outcomes.

---

## 5. Authority vocabulary

Recommended values:

- `world` — authoritative built-world source;
- `regional` — authoritative People/region source;
- `continental` — authoritative continent source;
- `tool` — authoritative generation methodology;
- `reference` — derived reference; not competing canon;
- `supporting` — supporting material that is not the source of truth;
- `historical` — preserved development history;
- `audit` — diagnostic source; never canon merely because it reports a finding.

### Source-of-truth rule

Only one active document should normally claim `source_of_truth: true` for a specific subject/scope combination.

Comparative sheets must normally use:

```yaml
source_of_truth: false
authority: reference
```

and identify their regional source files.

---

## 6. Path and filename validation

The validator must audit **every document filename**, including documents with no metadata.

It must report:

1. misleading names;
2. inconsistent naming conventions;
3. duplicate subject names at different levels;
4. old/batch-generated naming patterns;
5. names that do not match their directory scope;
6. names that imply authority the file does not have;
7. names that hide the document's actual subject;
8. obsolete filenames retained after architecture changes;
9. filenames that should be renamed to match the canonical regional structure;
10. collisions where two files appear to represent the same subject.

### Active world-entry filename convention

Use concise uppercase snake case for active Markdown subject files:

```text
FAMILY_BIRTH_CHILDHOOD.md
FAMILY_PARTNERSHIP.md
GOVERNANCE_AUTHORITY.md
FOOD_SUBSISTENCE.md
SETTLEMENT_HOUSING.md
```

The filename should describe the **subject**, not the production event that created it.

Avoid:

```text
BATCH_6_PEOPLES_FAMILY.md
NEW_FAMILY_DOC_FINAL.md
UPDATED_FINAL2.md
MOUNTAIN_REVISION_NEW.md
TEMP_CULTURE_WORK.md
```

Historical files may retain their original names when they are deliberately preserved as history.

### Comparative filename convention

Comparative/reference documents should be explicitly identifiable:

```text
COMPARATIVE/FAMILY_BIRTH_CHILDHOOD_COMPARATIVE.md
```

They must not use the same filename as an authoritative regional source when both could reasonably be confused.

### Tool filename convention

Tool names should describe the method/function:

```text
FAUNA_FUNCTION_MATRIX.md
PREDICTIVE_EVOLUTION_MATRIX.md
FLORA_CREATION_MATRIX.md
```

The validator should not require every tool to use one rigid suffix, but should flag names that obscure the function or suggest that a tool is narrative canon.

---

## 7. Path ↔ metadata consistency

The validator must derive expected metadata from the path and compare it with declared metadata.

Example:

```text
03_PEOPLES/CULTURES/HEARTH/PLAINS/FAMILY_BIRTH_CHILDHOOD.md
```

implies at minimum:

```yaml
layer: world
scope: people
continent: Hearth
people: Plains
subject: family.birth_childhood
```

A mismatch should be reported.

Examples:

- file says `people: Mountains` but lives under `PLAINS/` → **ERROR**;
- file says `layer: tool` but lives in an authoritative regional lore directory → **WARNING/ERROR depending on context**;
- comparative file claims `source_of_truth: true` → **ERROR**;
- archive file claims current regional authority → **ERROR**.

---

## 8. Subject identity

`subject` should be normalized enough to allow the validator to detect duplicates.

Recommended form:

```text
family.birth_childhood
family.partnership
family.kinship
food.subsistence
settlement.housing
governance.authority
technology.materials
belief.worldview
```

The validator should map common legacy filenames to normalized subjects during the audit without automatically renaming them.

Example:

```text
FAMILY_BIRTH_CHILDHOOD.md
BIRTH_CHILDHOOD.md
CHILDHOOD_AND_BIRTH.md
```

may all be flagged as possible aliases for:

```text
family.birth_childhood
```

A human decision or approved rename map determines the final canonical filename.

---

## 9. World Bible / deep-entry relationship

The World Bible is an overview/compiled orientation layer.

Deep regional documents are the detailed sources.

The validator should check that:

```text
DEEP WORLD CONTENT
        ↓
CONTINENT / PEOPLE OVERVIEW
        ↓
WORLD BIBLE
```

does not reverse into multiple competing sources of truth.

A World Bible statement that materially contradicts an authoritative deep source should be flagged.

A concise World Bible summary that omits deep detail is not an error.

---

## 10. Comparative/reference relationship

Comparative sheets are derived reference products.

They should:

- identify their scope;
- identify the subjects being compared;
- point to authoritative source files;
- avoid becoming the only location where a regional canon decision exists.

The validator should flag:

- comparative entries with no identifiable source;
- missing regional source files;
- comparative sheets containing unique canon not present in source files;
- source files that have been renamed without updating comparative references.

---

## 11. Tool relationship

Tools may have dependencies on world material and may be used to generate future world material.

Example:

```yaml
layer: tool
tool_scope: fauna
status: canon
authority: tool
depends_on:
  - hearth.ecology
  - world.climate
  - world.evolutionary_principles
used_by:
  - hearth.plains.fauna
```

A tool should describe **how to create plausible compatible material**, not silently impose that a particular creative result must exist.

The validator should flag a tool that references missing world inputs or references an obsolete path.

---

## 12. Archive rules

Anything under `07_ARCHIVE/` is historical unless explicitly reactivated.

The validator should:

- scan archive content for historical references;
- record them for traceability;
- **not** flag historical facts merely because they differ from current canon;
- flag an archive document if it is incorrectly tagged as a current source of truth;
- distinguish historical conflicts from active conflicts.

Archive material should never be mass-rewritten simply to make it agree with current canon.

---

## 13. Discrepancy record

Every validator finding that can affect world coherence should be representable as a discrepancy record.

Minimum fields:

```yaml
id: DEMO-001
category: population
severity: error
statement: Hearth population is listed as 1.5M
current_value: 1500000
expected_value: 1910000
expected_status: working_model
source_of_expected_value: hearth.demographic.ecological.mortality.model
affected_files:
  - 00_MASTER/WORLD_BIBLE.md
  - 03_PEOPLES/DEMOGRAPHICS/HUMAN_POPULATION_GEOGRAPHY.md
historical_files: []
action: review_and_patch
status: open
```

The validator may discover and group discrepancies, but must not silently resolve them.

---

## 14. Document rename record

Filename findings need their own record so renaming does not become guesswork.

Example:

```yaml
id: NAME-014
current_path: 03_PEOPLES/CULTURES/HEARTH/PLAINS/OLD_FAMILY_DOC.md
recommended_path: 03_PEOPLES/CULTURES/HEARTH/PLAINS/FAMILY_PARTNERSHIP.md
reason: filename does not identify established subject
confidence: high
collision_check: required
references_to_update: []
action: rename
status: open
```

The validator should identify all references to the old path before recommending a rename.

Renaming must be a controlled repository operation, not an automatic text substitution.

---

## 15. Validator output

The eventual validator should produce at least four reports:

### A. Repository Index
Every document with:
- path;
- filename;
- ID;
- title;
- layer;
- scope;
- status;
- authority;
- source-of-truth flag.

### B. Naming Report
Every suspicious, inconsistent, ambiguous, duplicate, legacy, or misleading filename.

### C. Discrepancy Ledger
Every active conflict and its affected documents.

### D. Dependency / Impact Report
For a changed source, show:

```text
SOURCE CHANGED
      ↓
DIRECT DEPENDENCIES
      ↓
SECONDARY REFERENCES
      ↓
COMPARATIVE / OVERVIEW OUTPUTS
```

The validator should distinguish **direct dependency** from merely mentioning the same term.

---

## 16. Severity model

- `ERROR` — structural or authority problem that should be reviewed before packaging.
- `WARNING` — likely issue, naming inconsistency, incomplete metadata, or possible conflict.
- `INFO` — useful observation with no known problem.
- `HISTORICAL` — detected difference confined to archive/history; informational only.

---

## 17. Migration strategy

The repository does not need to be rewritten in one pass.

Recommended migration order:

1. Audit every existing file name.
2. Build the rename/discrepancy ledger.
3. Establish canonical subject IDs.
4. Add metadata to new/actively edited files first.
5. Migrate authoritative active files in controlled batches.
6. Update cross-references after renames.
7. Validate again.
8. Only then consider automatic overview/reference compilation.

Existing documents without metadata are **legacy documents**, not automatically invalid documents. The validator should report missing metadata and infer probable values from path/content for review.

---

## 18. Non-negotiable validator behavior

The validator must:

- search the entire active repository, not only filenames;
- inspect archive separately;
- flag filenames independently of content validity;
- never assume a filename is correct because the content is good;
- never assume a path is correct because the filename is good;
- detect duplicate subject identities;
- detect competing source-of-truth claims;
- preserve historical material;
- report discrepancies with affected-document lists;
- distinguish direct dependencies from textual mentions where possible;
- never silently rewrite canon;
- never silently rename files;
- never treat a tool recommendation as a world requirement.

---

## 19. Current compatibility note

ARUUN already uses lightweight frontmatter in some master/reference documents, while many current regional entries use inline metadata such as `**Status:** CANON`. For example, the Canon Index uses YAML fields including `world`, `domain`, `subject`, `status`, and `canonical`, while regional entries currently use an inline Status line. The validator must support both during migration rather than treating existing files as invalid merely because they predate this schema.

This schema is therefore a **target standard**, not an instruction to rewrite the repository immediately.
