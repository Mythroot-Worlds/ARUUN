# ARUUN Version Overlay Specification

## Goal

Make rewrites safe by showing what survived, what changed, what was added, and what disappeared between versions of the same document.

## Overlay model

```text
PREVIOUS VERSION
      │
      ├── preserved ───────────────┐
      ├── modified ────────────────┤
      ├── potentially lost ────────┤──> HUMAN REVIEW
      └── prior-only numeric facts ┘
                                   │
CURRENT VERSION                    │
      ├── preserved ───────────────┤
      ├── modified ────────────────┤
      └── added ───────────────────┘
```

## Lineage

Primary lineage is the same repository path across Git history. A renamed or relocated document requires a review candidate rather than an automatic merge of identities.

## Display requirements

A generated overlay should include:

- path and comparison commits;
- similarity score;
- preserved statements;
- added statements;
- modified statements;
- previous/current numeric values;
- potential dropped statements;
- a stable review ID;
- creator resolution state.

## Safety

The overlay is advisory. It must never silently edit canon, delete history, or merge competing facts.
