# ARUUN Repository Tooling

Repository-maintenance and validation tooling for ARUUN. Tools are part of the world package but remain separate from ordinary lore: they explain and validate how the world is built without dictating what creators must create.

## Current tooling

### `ARUUN_REPOSITORY_SCHEMA_v0.1.md`
Target metadata, naming, path, authority, dependency, World Bible, comparative-sheet, and tool-layer schema.

### `validate_repo.py`
Read-only repository auditor. It scans Markdown documents across the repository, including files whose names do not advertise their subject, and checks:

- metadata presence and normalization;
- path ↔ metadata consistency;
- layer/scope mismatches;
- filename conventions;
- temporary/batch/legacy naming patterns;
- comparative naming;
- duplicate subject identities;
- archive separation.

It does **not** rename files, rewrite canon, or silently resolve discrepancies.

## Running the audit

From the repository root:

```bash
python TOOLS/REPOSITORY/validate_repo.py
```

Optional output location:

```bash
python TOOLS/REPOSITORY/validate_repo.py --out TOOLS/REPOSITORY/REPORTS
```

## Generated reports

- `AUDIT_SUMMARY.md` — high-level counts.
- `REPOSITORY_INDEX.md` — every scanned Markdown document and inferred identity.
- `NAMING_REPORT.md` — filename/path findings and rename recommendations.
- `DISCREPANCY_LEDGER.md` — metadata, path, status, authority, and duplicate findings.

## Operating principle

The validator reports problems; the Creative Director decides what happens next. A finding can be corrected, accepted as intentional, deferred, or recorded as a canon decision.

The validator is therefore a **QA instrument and world-building tool**, not a canon engine.
