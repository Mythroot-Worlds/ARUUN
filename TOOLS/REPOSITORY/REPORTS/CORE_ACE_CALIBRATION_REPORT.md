# CORE A.C.E. Calibration Report

**Adaptive Calibration Engine** — read-only training/calibration layer.

Human decisions are evidence for calibration, not automatic permission to change canon or rules.

Labeled decisions: **40**
Heuristic candidates: **14**

## Safety invariants
- Automatic rule promotion: **OFF**
- Automatic canon changes: **OFF**
- Provenance loss: **HARD FAILURE**

## Candidate heuristics
- `ECOLOGY/TOOL` proposed `DUPLICATE` → observed `SUPPORTING` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `DUPLICATE` → observed `VARIANT` (15 examples): **ELIGIBLE_FOR_HUMAN_REVIEW**
- `PEOPLES/CANON` proposed `KEEP` → observed `MISPLACED` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `MERGE` → observed `COINCIDENTAL` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `MERGE` → observed `CONFLICT` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `MERGE` → observed `HISTORICAL` (2 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `MERGE` → observed `RELATED` (7 examples): **ELIGIBLE_FOR_HUMAN_REVIEW**
- `PEOPLES/CANON` proposed `MERGE` → observed `REVIEW` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `MERGE` → observed `VARIANT` (1 examples): **CANDIDATE**
- `PEOPLES/COMPARATIVE` proposed `DUPLICATE` → observed `SUPPORTING` (1 examples): **CANDIDATE**
- `PEOPLES/TOOL` proposed `MERGE` → observed `SUPPORTING` (3 examples): **CANDIDATE**
- `PEOPLES/WORKING` proposed `MERGE` → observed `RELATED` (4 examples): **CANDIDATE**
- `PEOPLES/WORKING_CANON` proposed `MERGE` → observed `RELATED` (1 examples): **CANDIDATE**
- `TOOLS/TOOL` proposed `MERGE` → observed `COINCIDENTAL` (1 examples): **CANDIDATE**

## Contrastive groups
A contrastive group contains the same proposed signal/context with multiple human-observed outcomes. These are evidence for discrimination, not automatic rules.
- `PEOPLES/CANON` proposed `MERGE` → COINCIDENTAL, CONFLICT, HISTORICAL, RELATED, REVIEW, VARIANT
