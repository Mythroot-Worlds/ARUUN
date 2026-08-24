#!/usr/bin/env python3
"""Deterministic tests for CORE Semantic Arbitration."""
import unittest

from core_semantic_arbitration import arbitrate, normalize_legacy_resolution, validate_final_resolution


class SemanticArbitrationTests(unittest.TestCase):
    def test_variant_is_not_a_final_resolution(self):
        self.assertFalse(validate_final_resolution("VARIANT"))
        self.assertEqual(normalize_legacy_resolution("VARIANT"), "REVIEW")

    def test_authority_and_scope_can_coexist_without_variant(self):
        left = {
            "role": "AUTHORITATIVE", "authority": "REGIONAL", "scope": "REGION",
            "subject": "Coast", "evidence": [{"kind": "REFERENCE", "statement": "regional culture"}],
        }
        right = {
            "role": "REFERENCE", "authority": "CROSS_CULTURAL", "scope": "HEARTH_WIDE",
            "subject": "Coast", "evidence": [{"kind": "CONTEXT", "statement": "comparison"}],
        }
        result = arbitrate(left, right, "VARIANT")
        self.assertEqual(result.resolution, "SUPPORTING")
        self.assertIn("SCOPE_DIFFERENTIATED", result.descriptors)
        self.assertIn("ROLE_DIFFERENTIATED", result.descriptors)

    def test_missing_context_stays_unresolved(self):
        result = arbitrate({"subject": "A"}, {"subject": "A"}, "VARIANT")
        self.assertEqual(result.resolution, "UNRESOLVED")
        self.assertIn("UNKNOWN_DOCUMENT_ROLE", result.blockers)
        self.assertIn("UNKNOWN_AUTHORITY", result.blockers)
        self.assertIn("NO_EXPLICIT_EVIDENCE", result.blockers)

    def test_explicit_conflict_is_resolved_only_with_evidence(self):
        base = {"role": "AUTHORITATIVE", "authority": "CANON", "scope": "REGIONAL", "subject": "X"}
        left = {**base, "evidence": [{"kind": "CONFLICT", "statement": "X says north"}]}
        right = {**base, "evidence": [{"kind": "CONFLICT", "statement": "X says south"}]}
        self.assertEqual(arbitrate(left, right).resolution, "CONFLICT")


if __name__ == "__main__":
    unittest.main()
