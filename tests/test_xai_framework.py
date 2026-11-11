"""
Unit & Integration Test Suite for Explainable ML (XAI) Framework
Validates Modules 1 to 4 and the /api/v1/analyze target schema.
"""

import sys
import os
import unittest
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from services.barcode import validate_ean13, fetch_product_by_barcode
from services.parser import (
    load_taxonomy,
    normalize_ocr_errors,
    extract_additive_tokens,
    parse_additives_and_audit,
    construct_feature_vector
)
from services.scoring_engine import (
    compute_safety_score_and_attributions,
    calculate_grade,
    BASE_BASELINE_SCORE
)
from services.counterfactual import generate_counterfactual_explanation
from services.audit import evaluate_system_audit, get_audit_records
import app as flask_app_module


class TestXAIEndToEnd(unittest.TestCase):

    def setUp(self):
        self.app = flask_app_module.app.test_client()
        self.app.testing = True

    def test_01_ean13_validation(self):
        """Tests EAN-13 modulo-10 checksum validation."""
        # Valid EAN-13 barcodes
        self.assertTrue(validate_ean13("8901234567890"))
        self.assertTrue(validate_ean13("5449000000996"))
        self.assertTrue(validate_ean13("8901030000003"))

        # Invalid checksums
        self.assertFalse(validate_ean13("8901234567899"))
        self.assertFalse(validate_ean13("1234567890125"))

        # Invalid lengths / formats
        self.assertFalse(validate_ean13(""))
        self.assertFalse(validate_ean13("12345"))
        self.assertFalse(validate_ean13("890123456789X"))

    def test_02_product_fetch(self):
        """Tests product resolution with benchmark caching."""
        prod = fetch_product_by_barcode("8901234567890")
        self.assertEqual(prod["ean"], "8901234567890")
        self.assertEqual(prod["name"], "Sample Processed Food")
        self.assertEqual(prod["brand"], "Brand Name")
        self.assertIn("INS 250", prod["ingredients_text"])

    def test_03_ocr_normalization(self):
        """Tests normalization of OCR misreads (I->1, l->1, O->0)."""
        noisy_text = "Ingredients: INS lOl, INS 25O, E-2ll, water, salt."
        cleaned = normalize_ocr_errors(noisy_text)
        self.assertIn("INS 101", cleaned)
        self.assertIn("INS 250", cleaned)
        self.assertIn("E-211", cleaned)

    def test_04_taxonomy_parser_mapping(self):
        """Tests additive mapping against ins_taxonomy.json."""
        text = "Water, flour, INS 250 (Sodium Nitrite), E211, salt."
        parsed, unmapped, conf = parse_additives_and_audit(text)
        
        codes = [p["code"] for p in parsed]
        self.assertIn("INS 250", codes)
        self.assertIn("INS 211", codes)

        ins_250 = next(p for p in parsed if p["code"] == "INS 250")
        self.assertEqual(ins_250["name"], "Sodium Nitrite")
        self.assertEqual(ins_250["class"], "Preservative")
        self.assertEqual(ins_250["hazard_level"], "High")

    def test_05_shap_scoring_and_deductions_exact_target(self):
        """
        Validates target example from specification:
        INS 250 (-18.5 pts), High Sodium (-9.0 pts) -> Final: 62.5, Grade: C.
        """
        additives = [
            {
                "code": "INS 250",
                "name": "Sodium Nitrite",
                "class": "Preservative",
                "hazard_level": "High",
                "hazard_weight": 0.85
            }
        ]
        nutriments = {
            "sodium_100g": 1.25,  # High sodium -> -9.0 pts
            "sugars_100g": 5.0,
            "saturated_fat_100g": 3.0
        }

        res = compute_safety_score_and_attributions(additives, nutriments)

        self.assertEqual(res["base_baseline_score"], 90.0)
        self.assertEqual(res["final_score"], 62.5)
        self.assertEqual(res["grade"], "C")

        deductions = {d["feature"]: d["points_deducted"] for d in res["score_deductions"]}
        self.assertEqual(deductions.get("INS 250 (Sodium Nitrite)"), -18.5)
        self.assertEqual(deductions.get("High Sodium Content"), -9.0)

        # Mathematical efficiency check: Base + sum(deductions) == Final Score
        calculated = res["base_baseline_score"] + sum(d["points_deducted"] for d in res["score_deductions"])
        self.assertAlmostEqual(calculated, res["final_score"], places=1)

    def test_06_counterfactual_engine(self):
        """
        Validates actionable counterfactual optimization (Research Gap G2):
        Removing INS 250 increases safety score from 62.5 to 81.0 (+18.5 points).
        """
        additives = [
            {
                "code": "INS 250",
                "name": "Sodium Nitrite",
                "class": "Preservative",
                "hazard_level": "High",
                "hazard_weight": 0.85,
                "common_substitute": "INS 300 (Ascorbic acid)"
            }
        ]
        nutriments = {
            "sodium_100g": 1.25,
            "sugars_100g": 5.0,
            "saturated_fat_100g": 3.0
        }

        scoring = compute_safety_score_and_attributions(additives, nutriments)
        current_score = scoring["final_score"]
        deductions = scoring["score_deductions"]

        cf = generate_counterfactual_explanation(additives, nutriments, current_score, deductions)

        self.assertEqual(cf["target_score"], 81.0)
        self.assertIn("Remove INS 250 (Sodium Nitrite)", cf["recommended_action"])
        self.assertEqual(cf["potential_score_gain"], "+18.5 points")

    def test_07_human_in_the_loop_audit(self):
        """
        Validates HITL audit flagging (Research Gap G3) for unmapped additives.
        """
        # Clean scenario
        clean_res = evaluate_system_audit(0.95, [])
        self.assertFalse(clean_res["flagged_for_human_review"])
        self.assertEqual(clean_res["parser_confidence"], 0.95)

        # Unmapped additive scenario
        flagged_res = evaluate_system_audit(0.70, ["INS 9999_UNKNOWN"], context_identifier="AuditTest")
        self.assertTrue(flagged_res["flagged_for_human_review"])

        # Check records
        records = get_audit_records()
        self.assertTrue(any("INS 9999_UNKNOWN" in r.get("unmapped_tokens", []) for r in records))

    def test_08_api_v1_analyze_schema_validation(self):
        """
        Validates that POST /api/v1/analyze returns the exact JSON schema required by specification.
        """
        payload = {
            "ean": "8901234567890",
            "product": {
                "name": "Sample Processed Food",
                "brand": "Brand Name",
                "category": "Snacks"
            }
        }
        response = self.app.post(
            "/api/v1/analyze",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        # Check top-level keys
        self.assertIn("product", data)
        self.assertIn("parsed_additives", data)
        self.assertIn("safety_scoring", data)
        self.assertIn("counterfactual_explanation", data)
        self.assertIn("system_audit", data)

        # Check product schema
        self.assertEqual(data["product"]["ean"], "8901234567890")
        self.assertEqual(data["product"]["name"], "Sample Processed Food")
        self.assertEqual(data["product"]["brand"], "Brand Name")
        self.assertEqual(data["product"]["category"], "Snacks")

        # Check parsed_additives schema
        additives = data["parsed_additives"]
        self.assertGreater(len(additives), 0)
        ins_250 = next(a for a in additives if "250" in a["code"])
        self.assertEqual(ins_250["code"], "INS 250")
        self.assertEqual(ins_250["name"], "Sodium Nitrite")
        self.assertEqual(ins_250["class"], "Preservative")
        self.assertEqual(ins_250["hazard_level"], "High")

        # Check safety_scoring schema
        scoring = data["safety_scoring"]
        self.assertEqual(scoring["final_score"], 62.5)
        self.assertEqual(scoring["grade"], "C")
        self.assertEqual(scoring["base_baseline_score"], 90.0)

        # Check score_deductions list
        deductions = scoring["score_deductions"]
        features = [d["feature"] for d in deductions]
        self.assertIn("INS 250 (Sodium Nitrite)", features)
        self.assertIn("High Sodium Content", features)

        # Check counterfactual schema
        cf = data["counterfactual_explanation"]
        self.assertEqual(cf["target_score"], 81.0)
        self.assertIn("Remove INS 250 (Sodium Nitrite)", cf["recommended_action"])
        self.assertEqual(cf["potential_score_gain"], "+18.5 points")

        # Check system audit schema
        audit = data["system_audit"]
        self.assertIn("parser_confidence", audit)
        self.assertIn("flagged_for_human_review", audit)


if __name__ == "__main__":
    unittest.main()
