"""
Stage 2 Service Tests — Food Label Verification System
=====================================================
Tests for all new and modified services introduced in Stage 2:
  - scoring_engine.py  (rule-based label, disclaimer, rationale fields)
  - parser.py          (E-number range validation, Vitamin E false-positive,
                        expanded name dict, ocr_confidence parameter)
  - audit.py           (barcode_decode_status as string, 4-way confidence,
                        deduplication, persistent reviewer updates)
  - regulatory_checker.py (lookup by code/number, authority field, India check)
  - app.py endpoints   (POST /api/v1/analyze, POST audit review, GET queue)

Run from project root:
    python -m unittest tests.test_stage2_services -v
"""

import json
import os
import sys
import tempfile
import unittest

# ---- path setup ----
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)


# ===========================================================================
# TestScoringEngine
# ===========================================================================

class TestScoringEngine(unittest.TestCase):
    """Tests for the rewritten scoring_engine.py."""

    def setUp(self):
        from services.scoring_engine import (
            compute_rule_based_score,
            compute_safety_score_and_attributions,
        )
        self.compute = compute_rule_based_score
        self.compat_alias = compute_safety_score_and_attributions

        self.sample_additives = [
            {"code": "INS 250", "hazard_level": "Severe", "hazard_weight": 1.0,
             "class": "Preservative", "name": "Sodium Nitrite"},
            {"code": "INS 211", "hazard_level": "High", "hazard_weight": 0.8,
             "class": "Preservative", "name": "Sodium Benzoate"},
        ]
        self.sample_nutrients = {
            "sugars_100g": 10.0,
            "sodium_100g": 0.8,
            "saturated_fat_100g": 3.0,
        }

    def test_rule_based_label_in_output(self):
        """scoring_method must be 'rule_based_indicator', not 'SHAP' or ML."""
        result = self.compute(self.sample_additives, self.sample_nutrients)
        self.assertEqual(
            result.get("scoring_method"), "rule_based_indicator",
            "scoring_method must be 'rule_based_indicator'"
        )

    def test_scoring_disclaimer_present(self):
        """scoring_disclaimer must be a non-empty string."""
        result = self.compute(self.sample_additives, self.sample_nutrients)
        disclaimer = result.get("scoring_disclaimer", "")
        self.assertIsInstance(disclaimer, str)
        self.assertGreater(len(disclaimer), 20, "scoring_disclaimer is too short or missing")

    def test_scoring_version_present(self):
        """scoring_version field must be present."""
        result = self.compute(self.sample_additives, self.sample_nutrients)
        self.assertIn("scoring_version", result)

    def test_deduction_rationale_present(self):
        """Each score deduction must include a non-empty 'rationale' field."""
        result = self.compute(self.sample_additives, self.sample_nutrients)
        deductions = result.get("score_deductions", [])
        # At least one deduction expected for INS 250 (Severe hazard)
        self.assertGreater(len(deductions), 0, "Expected at least one deduction for Severe additive")
        for d in deductions:
            self.assertIn("rationale", d, f"Missing 'rationale' key in deduction: {d}")
            self.assertIsInstance(d["rationale"], str)
            self.assertGreater(len(d["rationale"]), 5, f"'rationale' is too short in deduction: {d}")

    def test_deduction_rule_source_present(self):
        """Each score deduction must include a non-empty 'rule_source' field."""
        result = self.compute(self.sample_additives, self.sample_nutrients)
        deductions = result.get("score_deductions", [])
        for d in deductions:
            self.assertIn("rule_source", d, f"Missing 'rule_source' key in deduction: {d}")

    def test_backward_compat_alias(self):
        """compute_safety_score_and_attributions() must still work (backward compat)."""
        result = self.compat_alias(self.sample_additives, self.sample_nutrients)
        self.assertIn("final_score", result)
        self.assertIn("grade", result)
        # The alias should also carry the scoring_method label
        self.assertEqual(result.get("scoring_method"), "rule_based_indicator")

    def test_final_score_range(self):
        """final_score must be 0–100."""
        result = self.compute(self.sample_additives, self.sample_nutrients)
        score = result.get("final_score", -1)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_no_shap_terminology(self):
        """Result keys and values must not contain the word 'shap'."""
        result = self.compute(self.sample_additives, self.sample_nutrients)
        result_str = json.dumps(result).lower()
        self.assertNotIn("shap", result_str, "SHAP terminology must be removed from scoring output")


# ===========================================================================
# TestParser
# ===========================================================================

class TestParser(unittest.TestCase):
    """Tests for the improved parser.py."""

    def setUp(self):
        from services.parser import extract_additive_tokens, parse_additives_and_audit
        self.extract = extract_additive_tokens
        self.parse = parse_additives_and_audit

    def test_e_number_range_valid(self):
        """E211 and E250 must be detected (within 100-1599 range)."""
        tokens = self.extract("Contains E211 and E250 as preservatives.")
        codes = [t.replace("INS ", "") for t in tokens]
        self.assertIn("211", codes, "E211 should be detected")
        self.assertIn("250", codes, "E250 should be detected")

    def test_e_number_range_too_high(self):
        """E2026 (year/date) must NOT be detected (above 1599)."""
        tokens = self.extract("Best before E2026.")
        codes = [t.replace("INS ", "").replace(" ", "") for t in tokens]
        self.assertNotIn("2026", codes, "E2026 (expiry year) must not be detected as additive")

    def test_e_number_range_too_low(self):
        """E10 (2-digit but below 100) must NOT be detected."""
        tokens = self.extract("Batch code E10-A product reference E50.")
        for t in tokens:
            num_part = t.replace("INS", "").strip()
            try:
                n = int(num_part)
                self.assertGreaterEqual(n, 100, f"E-number {n} is below valid range 100-1599")
            except ValueError:
                pass  # Non-numeric suffix — OK

    def test_vitamin_e_false_positive_prevented(self):
        """'Vitamin E 100mg' must NOT produce INS 100 (false positive)."""
        text = "Vitamin E 100mg per serving. Contains E211 as preservative."
        tokens = self.extract(text)
        # E211 should be found
        self.assertTrue(
            any("211" in t for t in tokens),
            "E211 should still be detected in same text"
        )
        # INS 100 (from 'Vitamin E 100') should NOT be found via E-number pattern
        # (it may still appear if 'Curcumin' chemical name matches, but not from E-pattern)
        # We check that the token set doesn't include INS 100 from the E-pattern
        # by verifying the text 'Vitamin E' context was correctly skipped.
        e_100_from_pattern = any(
            t.replace("INS ", "").strip().startswith("100") for t in tokens
        )
        # If INS 100 appears, it should only be if the taxonomy maps 'CURCUMIN'
        # which isn't in this text. So INS 100 should not appear at all.
        self.assertFalse(
            e_100_from_pattern,
            f"'Vitamin E 100mg' produced a false INS 100 detection. Tokens: {tokens}"
        )

    def test_vitamin_e_no_space_not_suppressed(self):
        """'E211' standalone (not preceded by vitamin) must still be detected."""
        tokens = self.extract("Preservative: E211.")
        self.assertTrue(any("211" in t for t in tokens), "Standalone E211 should be detected")

    def test_expanded_name_dict_potassium_sorbate(self):
        """'Potassium Sorbate' should map to INS 202 via chemical name dict."""
        tokens = self.extract("Contains Potassium Sorbate as preservative.")
        self.assertIn("INS 202", tokens, "Potassium Sorbate must map to INS 202")

    def test_expanded_name_dict_sucralose(self):
        """'Sucralose' should map to INS 955."""
        tokens = self.extract("Sweetened with Sucralose.")
        self.assertIn("INS 955", tokens, "Sucralose must map to INS 955")

    def test_expanded_name_dict_msg(self):
        """'Monosodium Glutamate' should map to INS 621."""
        tokens = self.extract("Flavor enhanced with Monosodium Glutamate.")
        self.assertIn("INS 621", tokens, "Monosodium Glutamate must map to INS 621")

    def test_expanded_name_dict_sodium_nitrite(self):
        """'Sodium Nitrite' should map to INS 250."""
        tokens = self.extract("Cured with Sodium Nitrite.")
        self.assertIn("INS 250", tokens, "Sodium Nitrite must map to INS 250")

    def test_ocr_confidence_parameter_accepted(self):
        """parse_additives_and_audit must accept ocr_confidence parameter."""
        result = self.parse("E211 preservative", ocr_confidence=0.75)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3,
                         "parse_additives_and_audit must return (additives, unmapped, conf) tuple")
        parsed_additives, unmapped, additive_conf = result
        self.assertIsInstance(parsed_additives, list)
        self.assertIsInstance(unmapped, list)
        self.assertIsInstance(additive_conf, float)

    def test_ocr_confidence_default_works(self):
        """parse_additives_and_audit must work without ocr_confidence argument."""
        parsed, unmapped, conf = self.parse("Contains E211.")
        self.assertIsInstance(conf, float)

    def test_ins_number_format_detected(self):
        """INS 250, INS:211, INS-330 should all be detected."""
        tokens = self.extract("INS 250, INS:211 and INS-330 listed.")
        codes = [t.replace("INS ", "").strip() for t in tokens]
        self.assertIn("250", codes)
        self.assertIn("211", codes)
        self.assertIn("330", codes)

    def test_no_duplicate_tokens(self):
        """Same additive mentioned twice should appear once in output."""
        tokens = self.extract("E211 sodium benzoate E211 preservative.")
        count_211 = sum(1 for t in tokens if "211" in t)
        self.assertEqual(count_211, 1, "Duplicate E211 must be deduplicated")

    def test_quantity_unit_suffix_not_matched(self):
        """Numbers immediately followed by mg/g/ml should not match as E-numbers."""
        # E100mg — 'E' followed by '100' followed by 'mg' — should be skipped
        tokens = self.extract("Energy 100mg, protein E100mg per serving, E211 permitted.")
        # E211 should be found
        self.assertTrue(any("211" in t for t in tokens), "E211 should be detected")
        # INS 100 from 'E100mg' should NOT be found via E-pattern
        e100_tokens = [t for t in tokens if t.replace("INS ", "").strip().startswith("100")]
        self.assertEqual(
            len(e100_tokens), 0,
            f"'E100mg' produced a false INS 100 match. Tokens: {tokens}"
        )

    def test_taxonomy_enhanced_fields_present(self):
        """Parsed additives must contain functional_categories, is_color, color_origin, alternative_names, verified_source."""
        parsed, _, _ = self.parse("Contains E102 and E330.")
        self.assertGreater(len(parsed), 0)
        for item in parsed:
            self.assertIn("functional_categories", item)
            self.assertIsInstance(item["functional_categories"], list)
            self.assertIn("is_color", item)
            self.assertIsInstance(item["is_color"], bool)
            self.assertIn("color_origin", item)
            self.assertIn("alternative_names", item)
            self.assertIsInstance(item["alternative_names"], list)
            self.assertIn("verified_source", item)

    def test_taxonomy_color_origin_classification(self):
        """Curcumin (E100) must be natural & is_color=True, Tartrazine (E102) must be synthetic & is_color=True, Citric Acid (E330) not_applicable & is_color=False."""
        parsed, _, _ = self.parse("Contains E100, E102, and E330.")
        by_code = {p["code"]: p for p in parsed}
        self.assertTrue(by_code.get("INS 100", {}).get("is_color"))
        self.assertEqual(by_code.get("INS 100", {}).get("color_origin"), "natural")
        self.assertTrue(by_code.get("INS 102", {}).get("is_color"))
        self.assertEqual(by_code.get("INS 102", {}).get("color_origin"), "synthetic")
        self.assertFalse(by_code.get("INS 330", {}).get("is_color"))
        self.assertEqual(by_code.get("INS 330", {}).get("color_origin"), "not_applicable")

    def test_taxonomy_multi_functional_categories(self):
        """Citric Acid (INS 330) must have multiple functional categories."""
        parsed, _, _ = self.parse("Contains E330.")
        self.assertEqual(len(parsed), 1)
        cats = parsed[0].get("functional_categories", [])
        self.assertIn("Acidity regulator", cats)
        self.assertIn("Antioxidant", cats)


# ===========================================================================
# TestAudit
# ===========================================================================

class TestAudit(unittest.TestCase):
    """Tests for the refined audit.py module."""

    def setUp(self):
        from services.audit import (
            evaluate_system_audit,
            update_audit_record,
            get_audit_records,
            BARCODE_STATUS_VALID,
            BARCODE_STATUS_INVALID,
            BARCODE_STATUS_NOT_PROVIDED,
            BARCODE_STATUS_LOOKUP_FAILED,
            AUDIT_LOG_PATH,
        )
        self.evaluate = evaluate_system_audit
        self.update = update_audit_record
        self.get_records = get_audit_records
        self.STATUS_VALID = BARCODE_STATUS_VALID
        self.STATUS_INVALID = BARCODE_STATUS_INVALID
        self.STATUS_NOT_PROVIDED = BARCODE_STATUS_NOT_PROVIDED
        self.STATUS_LOOKUP_FAILED = BARCODE_STATUS_LOOKUP_FAILED
        self.log_path = AUDIT_LOG_PATH

        # Use a temp file so tests don't pollute the real audit log
        self._original_path = AUDIT_LOG_PATH
        import services.audit as audit_module
        self._temp_log = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        self._temp_log.write("[]")
        self._temp_log.close()
        audit_module.AUDIT_LOG_PATH = self._temp_log.name

    def tearDown(self):
        import services.audit as audit_module
        audit_module.AUDIT_LOG_PATH = self._original_path
        try:
            os.unlink(self._temp_log.name)
        except OSError:
            pass

    def test_barcode_status_is_string_not_float(self):
        """confidence['barcode_decode_status'] must be a string, never a float."""
        result = self.evaluate(
            additive_match_confidence=0.9,
            unmapped_tokens=[],
            barcode_decode_status=self.STATUS_VALID
        )
        status = result["confidence"]["barcode_decode_status"]
        self.assertIsInstance(status, str, "barcode_decode_status must be a string enum, not float")

    def test_four_confidence_keys_present(self):
        """All four required confidence dimensions must be present."""
        result = self.evaluate(
            additive_match_confidence=0.9,
            unmapped_tokens=[],
        )
        conf = result["confidence"]
        self.assertIn("ocr_confidence", conf)
        self.assertIn("additive_match_confidence", conf)
        self.assertIn("barcode_decode_status", conf)
        self.assertIn("product_identity_confidence", conf)

    def test_barcode_status_valid_enum_value(self):
        """Status 'valid_ean13' must be accepted and reflected in output."""
        result = self.evaluate(
            additive_match_confidence=0.9,
            unmapped_tokens=[],
            barcode_decode_status=self.STATUS_VALID
        )
        self.assertEqual(result["confidence"]["barcode_decode_status"], "valid_ean13")

    def test_barcode_status_not_provided_enum_value(self):
        """Status 'not_provided' must be accepted."""
        result = self.evaluate(
            additive_match_confidence=0.9,
            unmapped_tokens=[],
            barcode_decode_status=self.STATUS_NOT_PROVIDED
        )
        self.assertEqual(result["confidence"]["barcode_decode_status"], "not_provided")

    def test_barcode_status_invalid_triggers_flag(self):
        """Invalid barcode status must trigger flagging."""
        result = self.evaluate(
            additive_match_confidence=0.9,
            unmapped_tokens=[],
            barcode_decode_status=self.STATUS_INVALID
        )
        self.assertTrue(result["flagged_for_human_review"])
        self.assertTrue(any("Barcode" in r for r in result["flag_reasons"]))

    def test_deduplication_same_entry_not_logged_twice(self):
        """Same (context_identifier, unmapped_tokens) should produce only 1 record."""
        import services.audit as audit_module
        # Call twice with identical context and unmapped tokens
        for _ in range(2):
            self.evaluate(
                additive_match_confidence=0.2,  # low to trigger flag
                unmapped_tokens=["unknown_x"],
                context_identifier="TEST_DEDUP",
                raw_text="some text"
            )
        records = self.get_records()
        matching = [r for r in records if r.get("context_identifier") == "TEST_DEDUP"]
        self.assertEqual(len(matching), 1, "Duplicate audit entries must be deduplicated")

    def test_reviewer_confirm_persists_to_disk(self):
        """update_audit_record('confirm') must persist the status change to disk."""
        # First create a flagged record
        self.evaluate(
            additive_match_confidence=0.1,
            unmapped_tokens=["mystery_token"],
            context_identifier="TEST_CONFIRM",
            raw_text="test ingredient text"
        )
        records_before = self.get_records()
        self.assertGreater(len(records_before), 0, "Expected at least one audit record")

        record_id = records_before[0]["id"]
        result = self.update(record_id, "confirm", reviewer_note="Verified not an additive")
        self.assertTrue(result["success"], f"update_audit_record failed: {result}")

        # Reload from disk and verify persistence
        records_after = self.get_records()
        updated = next((r for r in records_after if r["id"] == record_id), None)
        self.assertIsNotNone(updated, "Record not found after update")
        self.assertEqual(updated["audit_status"], "CONFIRMED_BY_REVIEWER")
        self.assertEqual(len(updated.get("review_history", [])), 1)

    def test_reviewer_correct_stores_corrected_tokens(self):
        """update_audit_record('correct', [...]) must store corrected_tokens in record."""
        self.evaluate(
            additive_match_confidence=0.1,
            unmapped_tokens=["mis_spelled_additive"],
            context_identifier="TEST_CORRECT",
            raw_text="ingredient text"
        )
        records = self.get_records()
        record_id = records[0]["id"]

        result = self.update(record_id, "correct", corrected_tokens=["INS 250"])
        self.assertTrue(result["success"])

        records_after = self.get_records()
        updated = next(r for r in records_after if r["id"] == record_id)
        self.assertEqual(updated["audit_status"], "CORRECTED_BY_REVIEWER")
        self.assertEqual(updated.get("corrected_tokens"), ["INS 250"])

    def test_reviewer_invalid_action_returns_failure(self):
        """update_audit_record with invalid action must return success=False."""
        result = self.update("some_id", "invalidaction")
        self.assertFalse(result["success"])
        self.assertIn("message", result)

    def test_reviewer_correct_without_tokens_returns_failure(self):
        """'correct' action without corrected_tokens must return success=False."""
        result = self.update("some_id", "correct", corrected_tokens=None)
        self.assertFalse(result["success"])

    def test_flag_reasons_populated_for_unmapped_tokens(self):
        """Unmapped tokens must produce non-empty flag_reasons list."""
        result = self.evaluate(
            additive_match_confidence=0.9,
            unmapped_tokens=["UnknownChem X", "SuspiciousE9999"]
        )
        self.assertTrue(result["flagged_for_human_review"])
        self.assertGreater(len(result["flag_reasons"]), 0)

    def test_no_flag_when_all_confident(self):
        """High confidence + no unmapped tokens must NOT trigger flagging."""
        result = self.evaluate(
            additive_match_confidence=0.95,
            unmapped_tokens=[],
            ocr_confidence=0.90,
            barcode_decode_status=self.STATUS_VALID,
            product_identity_confidence=1.0
        )
        self.assertFalse(result["flagged_for_human_review"])
        self.assertEqual(len(result["flag_reasons"]), 0)

    def test_backward_compat_parser_confidence_key(self):
        """parser_confidence (backward compat key) must still be in response."""
        result = self.evaluate(
            additive_match_confidence=0.8,
            unmapped_tokens=[]
        )
        self.assertIn("parser_confidence", result)
        self.assertIsInstance(result["parser_confidence"], float)


# ===========================================================================
# TestRegulatoryChecker
# ===========================================================================

class TestRegulatoryChecker(unittest.TestCase):
    """Tests for regulatory_checker.py and regulatory_references.json."""

    def setUp(self):
        from services.regulatory_checker import (
            get_regulatory_info,
            get_regulatory_info_batch,
            is_permitted_in_india,
        )
        self.get_info = get_regulatory_info
        self.get_batch = get_regulatory_info_batch
        self.is_permitted = is_permitted_in_india

    def test_ins250_lookup_by_ins_prefix(self):
        """get_regulatory_info('INS 250') must return Sodium Nitrite entry."""
        info = self.get_info("INS 250")
        self.assertNotEqual(info, {}, "INS 250 entry must exist")
        self.assertEqual(info.get("name"), "Sodium Nitrite")

    def test_lookup_by_bare_number(self):
        """get_regulatory_info('250') must return same as 'INS 250'."""
        info_full = self.get_info("INS 250")
        info_bare = self.get_info("250")
        self.assertEqual(info_full, info_bare, "Bare number lookup must match 'INS NNN' lookup")

    def test_lookup_by_e_number(self):
        """get_regulatory_info('E250') must return Sodium Nitrite entry."""
        info = self.get_info("E250")
        self.assertNotEqual(info, {})
        self.assertEqual(info.get("name"), "Sodium Nitrite")

    def test_unknown_code_returns_empty(self):
        """INS 9999 (non-existent) must return empty dict."""
        info = self.get_info("INS 9999")
        self.assertEqual(info, {})

    def test_permitted_in_india_ins330(self):
        """Citric Acid (INS 330) is permitted by FSSAI."""
        result = self.is_permitted("INS 330")
        self.assertTrue(result, "INS 330 (Citric Acid) must be reported as permitted in India")

    def test_permitted_in_india_unknown_returns_none(self):
        """Unknown code must return None (not True or False)."""
        result = self.is_permitted("INS 9999")
        self.assertIsNone(result)

    def test_authority_field_present_in_v2_1(self):
        """v2.1 regulatory_references.json must include 'authority' field."""
        info = self.get_info("INS 250")
        self.assertIn("authority", info, "'authority' field missing — regulatory_references.json not updated to v2.1")
        self.assertIsInstance(info["authority"], str)
        self.assertGreater(len(info["authority"]), 0)

    def test_source_url_field_present_in_v2_1(self):
        """v2.1 entries must include 'source_url' field."""
        info = self.get_info("INS 211")
        self.assertIn("source_url", info, "'source_url' field missing — regulatory_references.json not updated to v2.1")
        url = info["source_url"]
        self.assertTrue(url.startswith("http"), f"source_url should be a real URL, got: {url}")

    def test_applicable_conditions_field_present_in_v2_1(self):
        """v2.1 entries must include 'applicable_conditions' field."""
        info = self.get_info("INS 250")
        self.assertIn("applicable_conditions", info)
        self.assertGreater(len(info.get("applicable_conditions", "")), 0)

    def test_batch_lookup_returns_all_codes(self):
        """get_regulatory_info_batch must return a key for every input code."""
        codes = ["INS 100", "INS 211", "INS 330", "INS 9999"]
        batch = self.get_batch(codes)
        for code in codes:
            self.assertIn(code, batch)

    def test_batch_lookup_known_entries_not_empty(self):
        """Known codes in batch must return non-empty dicts."""
        batch = self.get_batch(["INS 100", "INS 330"])
        self.assertNotEqual(batch["INS 100"], {})
        self.assertNotEqual(batch["INS 330"], {})

    def test_verified_field_present(self):
        """All entries must have a 'verified' boolean field."""
        info = self.get_info("INS 102")
        self.assertIn("verified", info)
        self.assertIsInstance(info["verified"], bool)

    def test_last_verified_field_present(self):
        """All entries should have a 'last_verified' date string."""
        info = self.get_info("INS 102")
        self.assertIn("last_verified", info)


# ===========================================================================
# TestAppEndpoints
# ===========================================================================

class TestAppEndpoints(unittest.TestCase):
    """Integration tests for Flask API endpoints."""

    def setUp(self):
        import app as flask_app
        flask_app.app.config["TESTING"] = True
        self.client = flask_app.app.test_client()

    # --- /api/v1/analyze ---

    def test_analyze_missing_both_fields_returns_400(self):
        """POST with empty body must return 400."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)
        body = resp.get_json()
        self.assertIn("error", body)

    def test_analyze_ean_too_long_returns_400(self):
        """EAN longer than 20 chars must return 400."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({"ean": "X" * 21}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_analyze_valid_barcode_returns_200(self):
        """POST with valid benchmark EAN must return 200."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({"ean": "8901234567890"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)

    def test_analyze_response_has_safety_indicator(self):
        """Response must contain safety_indicator with scoring_method label."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({"ean": "8901234567890"}),
            content_type="application/json"
        )
        body = resp.get_json()
        self.assertIn("safety_indicator", body)
        self.assertEqual(
            body["safety_indicator"].get("scoring_method"),
            "rule_based_indicator"
        )

    def test_analyze_response_has_safety_scoring_backward_compat(self):
        """Response must also contain legacy 'safety_scoring' field for backward compat."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({"ean": "8901234567890"}),
            content_type="application/json"
        )
        body = resp.get_json()
        self.assertIn("safety_scoring", body, "'safety_scoring' backward-compat field missing")

    def test_analyze_barcode_decode_status_is_string(self):
        """system_audit.confidence.barcode_decode_status must be a string."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({"ean": "8901234567890"}),
            content_type="application/json"
        )
        body = resp.get_json()
        status = body.get("system_audit", {}).get("confidence", {}).get("barcode_decode_status")
        self.assertIsNotNone(status, "barcode_decode_status missing from response")
        self.assertIsInstance(status, str, "barcode_decode_status must be a string, not a float")
        # Must be one of the defined enum values
        valid_statuses = {"valid_ean13", "invalid_checksum", "not_provided", "lookup_failed"}
        self.assertIn(status, valid_statuses, f"Unexpected barcode_decode_status value: {status}")

    def test_analyze_four_confidence_keys_in_response(self):
        """Response system_audit.confidence must contain all 4 confidence keys."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({"ean": "8901234567890"}),
            content_type="application/json"
        )
        body = resp.get_json()
        conf = body.get("system_audit", {}).get("confidence", {})
        self.assertIn("ocr_confidence", conf)
        self.assertIn("additive_match_confidence", conf)
        self.assertIn("barcode_decode_status", conf)
        self.assertIn("product_identity_confidence", conf)

    def test_analyze_text_only_request(self):
        """POST with text (no EAN) must succeed and use not_provided barcode status."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({
                "text": "Contains E211, E330 and E950 as additives.",
                "ocr_confidence": 0.85
            }),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        status = body["system_audit"]["confidence"]["barcode_decode_status"]
        self.assertEqual(status, "not_provided")

    def test_analyze_regulatory_fields_present(self):
        """Parsed additives should contain regulatory info with authority and source_url."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({"text": "Contains E211 sodium benzoate."}),
            content_type="application/json"
        )
        body = resp.get_json()
        additives = body.get("parsed_additives", [])
        # Find INS 211 in response
        ins211 = next((a for a in additives if "211" in a.get("code", "")), None)
        if ins211 and ins211.get("regulatory"):
            reg = ins211["regulatory"]
            self.assertIn("authority", reg)
            self.assertIn("source_url", reg)

    def test_analyze_ocr_confidence_out_of_range_returns_400(self):
        """ocr_confidence outside 0.0-1.0 must return 400."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({"text": "E211", "ocr_confidence": 1.5}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_analyze_ocr_confidence_zero_preserved(self):
        """ocr_confidence = 0.0 must be preserved as 0.0, not defaulted to 1.0."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({"text": "Contains INS 211", "ocr_confidence": 0.0}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        conf = body.get("system_audit", {}).get("confidence", {})
        self.assertEqual(conf.get("ocr_confidence"), 0.0, "ocr_confidence 0.0 was overwritten")

    def test_analyze_product_identity_confidence_found(self):
        """Valid EAN found in catalog must give product_identity_confidence = 1.0."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({"ean": "8901234567890"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        conf = body.get("system_audit", {}).get("confidence", {})
        self.assertEqual(conf.get("product_identity_confidence"), 1.0)
        self.assertTrue(body.get("product", {}).get("found_in_db"))

    def test_analyze_product_identity_confidence_not_found(self):
        """Valid EAN-13 not found in catalog must give product_identity_confidence = 0.0."""
        # 1234567890128 is valid EAN-13 checksum, not in benchmark
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({"ean": "1234567890128"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        conf = body.get("system_audit", {}).get("confidence", {})
        self.assertEqual(conf.get("product_identity_confidence"), 0.0)
        self.assertFalse(body.get("product", {}).get("found_in_db"))
        flags = body.get("system_audit", {}).get("flag_reasons", [])
        self.assertTrue(any("Product identity not found" in f for f in flags))

    def test_analyze_product_identity_confidence_no_barcode(self):
        """No barcode provided must yield product_identity_confidence = 0.5."""
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps({"text": "Contains INS 211"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        conf = body.get("system_audit", {}).get("confidence", {})
        self.assertEqual(conf.get("product_identity_confidence"), 0.5)

    def test_product_endpoint_lookup_status(self):
        """GET /api/v1/product/<barcode> returns product_found and lookup_status."""
        resp = self.client.get("/api/v1/product/8901234567890")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertTrue(body.get("product_found"))
        self.assertEqual(body.get("lookup_status"), "success")

    # --- /api/v1/audit/<id>/review ---

    def test_audit_review_missing_action_returns_400(self):
        """POST review with no action field must return 400."""
        resp = self.client.post(
            "/api/v1/audit/some_id/review",
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_audit_review_invalid_action_returns_400(self):
        """POST review with unrecognised action must return 400."""
        resp = self.client.post(
            "/api/v1/audit/some_id/review",
            data=json.dumps({"action": "nonsense"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_audit_review_nonexistent_id_returns_400(self):
        """POST review for a record that does not exist must return 400."""
        resp = self.client.post(
            "/api/v1/audit/does_not_exist_id/review",
            data=json.dumps({"action": "confirm"}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)

    # --- GET /api/v1/audit/unmapped ---

    def test_audit_queue_returns_200(self):
        """GET /api/v1/audit/unmapped must return 200 with records list."""
        resp = self.client.get("/api/v1/audit/unmapped")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("records", body)
        self.assertIsInstance(body["records"], list)

    def test_audit_queue_status_filter(self):
        """GET with status= param must accept and apply the filter without error."""
        resp = self.client.get("/api/v1/audit/unmapped?status=PENDING_EXPERT_REVIEW")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        # All returned records must match the filter
        for rec in body.get("records", []):
            self.assertEqual(rec.get("audit_status"), "PENDING_EXPERT_REVIEW")

    # --- GET /api/health ---

    def test_health_endpoint(self):
        """GET /api/health must return healthy status."""
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body.get("status"), "healthy")
        self.assertEqual(body.get("scoring_method"), "rule_based_indicator")


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
