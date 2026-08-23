# Aruun

**Aruun** is a fictional world developed by **Mythroot Worlds**, the creative-world division of **Mythroot**.

This repository is the **source repository for Aruun**. It is the authoritative place to look for the current state of the world's content, structure, and status.

## Status

This repository is currently in **foundation / development setup**. The directory structure exists to organize content as it is created and migrated; not all sections are populated yet.

## How truth is tracked

- **Git history** is the version history for this repository. Files are not duplicated as `FINAL`, `FINAL2`, or similar — Git commits record how content has changed over time.
- **Canon vs. working status** is tracked in the metadata of individual content files (see front matter conventions) and summarized in `00_MASTER/`.
- **`00_MASTER/WORLD_BIBLE.md`** is a human-facing synthesis of the world, not the sole source of truth. Underlying domain documents are the source of truth for their subject areas.
- **`CHANGELOG.md`** records worldbuilding decisions and their reasoning, separate from the Git commit log of file changes.

## Release directories

**`08_RELEASES/`** contains controlled distributions (internal, full, creator, player, and licensed subsets) generated from this source repository. Release directories are **not** independent sources of truth — they are curated exports of material that lives here.

## Structure

See `00_MASTER/CANON_INDEX.md` for an index of the domain directories and what belongs in each.
