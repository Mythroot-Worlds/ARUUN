# CORE A.C.E. Calibration Report

**Adaptive Calibration Engine** — read-only training/calibration layer.

Human decisions are evidence for calibration, not automatic permission to change canon or rules.

Labeled decisions: **10**
Heuristic candidates: **10**

## Safety invariants
- Automatic rule promotion: **OFF**
- Automatic canon changes: **OFF**
- Provenance loss: **HARD FAILURE**

## Candidate heuristics
- `ECOLOGY/TOOL` proposed `DUPLICATE` → observed `SUPPORTING` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `DUPLICATE` → observed `VARIANT` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `KEEP` → observed `MISPLACED` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `MERGE` → observed `COINCIDENTAL` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `MERGE` → observed `CONFLICT` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `MERGE` → observed `HISTORICAL` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `MERGE` → observed `RELATED` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `MERGE` → observed `REVIEW` (1 examples): **CANDIDATE**
- `PEOPLES/CANON` proposed `MERGE` → observed `VARIANT` (1 examples): **CANDIDATE**
- `TOOLS/TOOL` proposed `MERGE` → observed `COINCIDENTAL` (1 examples): **CANDIDATE**
