# CORE A.C.E. — Corpus Observer Integration Plan

## Purpose

Move CORE A.C.E. from validator-only development into guarded observation of the real ARUUN corpus.

The observer may analyze and report. It must not silently modify canon.

## Phase 1 — Corpus Inventory

- Enumerate all corpus documents in scope.
- Record path, front matter/status, domain, cultural scope, subject, and authority layer.
- Exclude generated releases and validator reports from source-of-truth analysis unless explicitly requested.
- Produce a stable inventory report.

## Phase 2 — Relationship Observation

For each eligible document pair, produce:

- relationship classification;
- placement recommendation;
- structural evidence;
- confidence;
- canonical/context hints;
- review requirement;
- provenance.

The observer must distinguish:

- RELATED — same information system but not a scoped representation of one another;
- VARIANT — substantially the same subject represented at different layers/scopes;
- SUPPORTING — one document directly supports another without being its variant;
- REVIEW — insufficient evidence or conflicting signals;
- CONFLICT — substantive incompatible claims;
- MISPLACED — document appears to belong elsewhere;
- DUPLICATE — materially redundant document.

## Phase 3 — Safety Boundary

The observer may write reports only to the designated report area.

It must not:

- rewrite canon documents;
- promote working material to canon;
- delete or relocate source documents;
- resolve unresolved lore automatically;
- alter human adjudication labels;
- modify the trusted holdout;
- treat generated release files as sources of truth.

## Phase 4 — Human Review Queue

Escalate cases when:

- structural evidence conflicts;
- authority/lineage is unclear;
- a proposed relationship would materially affect placement;
- a conflict cannot be resolved from existing authoritative documents;
- the system's confidence is insufficient.

Human decisions may later become trusted calibration material only through explicit adjudication.

## Phase 5 — Corpus Pilot

Run against the current ARUUN corpus in observation mode.

Success criteria:

1. Corpus inventory completes without source mutation.
2. Every proposed placement has evidence.
3. No automatic canon changes occur.
4. Known calibration cases remain correct.
5. True-blind protections remain intact.
6. REVIEW cases are preserved rather than forced into a stronger relationship.
7. Reports are deterministic enough to compare across runs.

## Phase 6 — Promotion Gate

Do not promote CORE A.C.E. to active corpus organization until the pilot has been reviewed and the following are demonstrated:

- stable placement behavior;
- acceptable false-positive/false-negative relationship rates;
- safe handling of ambiguity;
- no answer leakage;
- no automatic canon mutation;
- auditable provenance for every recommendation.

## Operating Principle

CORE A.C.E. exists to identify enough structure to keep the corpus organized. It does not need perfect semantic understanding before it can be useful. It must, however, be conservative about claims it cannot support.

**Documents record decisions. They do not make decisions.**
