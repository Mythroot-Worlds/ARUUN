"""Small, auditable policy helpers for ontology-v2 relationship routing.

These helpers are intentionally conservative: VARIANT requires same-subject/layer evidence;
regional/context difference by itself is never enough.
"""


def classify_structural_relationship(*, category, subject, context, information, purpose,
                                      revision_lineage, same_subject_layer=False,
                                      explicit_scoped_expression=False,
                                      explicit_version_or_variant=False):
    """Return a structural relationship decision.

    Policy:
    - REVIEW is for genuine ambiguity/insufficient evidence.
    - RELATED is the default for shared domain/category relationships.
    - VARIANT requires affirmative same-subject/scoped/version evidence.
    """
    if same_subject_layer or explicit_scoped_expression or explicit_version_or_variant:
        return "VARIANT"

    if category == "SAME":
        if subject == "SAME" and purpose == "SAME":
            return "RELATED"
        if subject == "DIFFERENT":
            return "RELATED"
        if subject == "SAME" and purpose == "DIFFERENT":
            return "RELATED"

    if category == "DIFFERENT" and information == "LOW":
        return "REVIEW"

    return "RELATED"
