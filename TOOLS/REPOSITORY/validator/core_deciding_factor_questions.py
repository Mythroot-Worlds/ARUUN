#!/usr/bin/env python3
"""CORE deciding-factor question bank.

Turns the complete ontology into investigation prompts. This is a question bank,
not a scoring model: evidence must still answer the question before any human
adjudication can use it.
"""
from __future__ import annotations

QUESTIONS = {
    "subject": "What exact underlying subject is each artifact describing, and are they materially the same subject?",
    "scope": "At what geographic, social, organizational, or conceptual scope does each claim apply?",
    "scale": "At what scale does the described subject operate, and does that scale materially differ?",
    "function": "What function does each artifact or described element perform?",
    "depth": "Does one artifact provide a different level of development or depth rather than the same informational job?",
    "canon_status": "What status does each claim have, and could an apparent disagreement be explained by differing canon states?",
    "importance": "Does either artifact establish core material while the other is supporting or optional material?",
    "development_state": "Is the difference explained by one area being developed while the other remains partial, open, or intentionally unfinished?",
    "relationship": "What relationship type is actually supported by the evidence: related, variant, supporting, historical, conflict, misplaced, duplicate, coincidental, or review?",
    "dependency": "Does either artifact depend on, derive from, reference, build on, or inform the other?",
    "consequence": "What downstream world systems does each artifact affect, and are those consequences compatible or distinct?",
    "provenance": "Where did each claim originate, and does provenance establish precedence or authority?",
    "intentionality": "Is an apparent absence or omission intentionally open, unexplored, creator-expandable, or otherwise deliberate?",
    "coherence": "How does each artifact connect to geography, settlement, economy, politics, law, history, culture, daily life, or ecology?",
    "usability": "Is the difference caused by creator-facing usability, licensing, presentation, or world-meaning?",
    "story_relevance": "What story, conflict, mystery, narrative consequence, or story-generation opportunity does each artifact create?",
}


def questions_for_dimensions(dimensions=None):
    selected=list(dimensions) if dimensions else list(QUESTIONS)
    return [{"dimension":d,"question":QUESTIONS[d]} for d in selected if d in QUESTIONS]
