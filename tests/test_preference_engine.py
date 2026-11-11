"""
Phase 6 Tests: Personalised Additive Preference Matching Engine
================================================================
Comprehensive test suite for:
  - backend/services/preference_engine.py
  - Allergen detection across raw text and additive names
  - Explicit INS number avoid/caution matching
  - Functional category avoidance (colors, preservatives, sweeteners, MSG, animal derivatives)
  - Deterministic rule-based scoring (0-100), caps, and transparent deduction breakdowns
  - Safety verdicts and disclaimers
  - POST /api/v1/preferences/evaluate and POST /api/v1/analyze endpoints
"""

import os
import sys
import json
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

from models.database import init_db, get_db_connection
from services.preference_engine import (
    check_allergens,
    evaluate_dietary_preferences,
    ALLERGEN_KEYWORD_MAP,
    ANIMAL_DERIVED_INS,
    SCORING_DISCLAIMER
)
from services.auth_service import register_user, authenticate_user, DIETARY_PRESETS
from app import app


class TestAllergenDetection(unittest.TestCase):
    """Tests for ingredient text and additive allergen detection."""

    def test_allergen_detection_raw_text_plurals(self):
        """Detects allergens with plural variations and word boundary safety."""
        raw_text = "Ingredients: Wheat flour, roasted peanuts, sugar, salt, milk solid."
        allergens = ["peanuts", "gluten", "dairy", "soy"]
        alerts = check_allergens(raw_text, allergens)

        alert_keys = [a["allergen"] for a in alerts]
        self.assertIn("peanuts", alert_keys)
        self.assertIn("gluten", alert_keys)  # matched 'wheat flour'
        self.assertIn("dairy", alert_keys)   # matched 'milk solid'
        self.assertNotIn("soy", alert_keys)

        for a in alerts:
            self.assertEqual(a["severity"], "CRITICAL")
            self.assertEqual(a["source"], "raw_ingredient_text")

    def test_allergen_detection_in_additive_names(self):
        """Detects allergens when present in parsed additive official or alternative names."""
        raw_text = "Ingredients: Refined oil, sugar, INS 322, INS 1105."
        parsed_additives = [
            {
                "code": "INS 322",
                "clean_code": "322",
                "name": "Soy Lecithin",
                "alternative_names": ["Lecithin", "Soya lecithin"],
                "functional_categories": ["Emulsifier"]
            },
            {
                "code": "INS 1105",
                "clean_code": "1105",
                "name": "Lysozyme",
                "alternative_names": ["Muramidase"],
                "functional_categories": ["Preservative"]
            }
        ]
        alerts = check_allergens(raw_text, ["soy", "egg"], parsed_additives=parsed_additives)
        alert_allergens = [a["allergen"] for a in alerts]
        self.assertIn("soy", alert_allergens)
        self.assertIn("egg", alert_allergens)

    def test_allergen_score_cap_and_verdict(self):
        """Presence of critical allergens caps personal score to max 20 and sets ALLERGEN WARNING."""
        parsed_additives = [
            {"code": "INS 100", "clean_code": "100", "name": "Curcumin", "is_color": True, "color_origin": "natural"}
        ]
        profile = {
            "preset_name": "custom",
            "custom_allergens": ["peanuts"],
            "avoid_synthetic_colors": False
        }
        raw_text = "Ingredients: Corn starch, peanuts, water."
        result = evaluate_dietary_preferences(parsed_additives, raw_text, profile)

        self.assertTrue(len(result["allergen_alerts"]) > 0)
        self.assertLessEqual(result["personal_score"], 20)
        self.assertIn("ALLERGEN WARNING", result["personal_verdict"])
        self.assertTrue(any(v["type"] == "allergen" for v in result["critical_violations"]))


class TestAdditiveMatchingEngine(unittest.TestCase):
    """Tests for additive classification, category avoidance, and origin rules."""

    def test_explicit_avoid_ins_matching(self):
        """Strictly avoided INS codes yield 20 pt deduction and are placed in critical violations."""
        parsed_additives = [
            {"code": "INS 102", "clean_code": "102", "name": "Tartrazine", "is_color": True, "color_origin": "synthetic"},
            {"code": "INS 330", "clean_code": "330", "name": "Citric Acid", "functional_categories": ["Acidity regulator"]}
        ]
        profile = {
            "preset_name": "custom",
            "custom_avoid_ins": ["INS 102"],
            "custom_caution_ins": []
        }
        res = evaluate_dietary_preferences(parsed_additives, "Sugar, INS 102, INS 330", profile)

        self.assertEqual(res["personal_score"], 80)  # 100 - 20
        self.assertEqual(len(res["critical_violations"]), 1)
        self.assertEqual(res["critical_violations"][0]["code"], "INS 102")
        self.assertEqual(len(res["acceptable_additives"]), 1)
        self.assertEqual(res["acceptable_additives"][0]["code"], "INS 330")

    def test_synthetic_color_avoidance_distinguishes_natural_colors(self):
        """Synthetic color triggers deduction; natural color is marked acceptable."""
        parsed_additives = [
            {"code": "INS 110", "clean_code": "110", "name": "Sunset Yellow", "is_color": True, "color_origin": "synthetic"},
            {"code": "INS 162", "clean_code": "162", "name": "Beetroot Red", "is_color": True, "color_origin": "natural"}
        ]
        profile = {
            "preset_name": "custom",
            "avoid_synthetic_colors": True
        }
        res = evaluate_dietary_preferences(parsed_additives, "Food item", profile)

        self.assertEqual(res["personal_score"], 85)  # 100 - 15
        self.assertTrue(any(w["type"] == "synthetic_color" and w["code"] == "INS 110" for w in res["warnings"]))
        self.assertTrue(any(a["code"] == "INS 162" for a in res["acceptable_additives"]))

    def test_preservative_and_sweetener_avoidance(self):
        """Preservative and sweetener avoidance apply separate transparent deductions."""
        parsed_additives = [
            {"code": "INS 211", "clean_code": "211", "name": "Sodium Benzoate", "functional_categories": ["Preservative"]},
            {"code": "INS 951", "clean_code": "951", "name": "Aspartame", "functional_categories": ["Sweetener"]}
        ]
        profile = {
            "preset_name": "custom",
            "avoid_preservatives": True,
            "avoid_artificial_sweeteners": True
        }
        res = evaluate_dietary_preferences(parsed_additives, "Diet beverage", profile)

        self.assertEqual(res["personal_score"], 70)  # 100 - 15 - 15
        self.assertEqual(len(res["warnings"]), 2)
        warn_types = [w["type"] for w in res["warnings"]]
        self.assertIn("preservative", warn_types)
        self.assertIn("artificial_sweetener", warn_types)

    def test_animal_derivatives_avoidance(self):
        """Animal-derived additives (Carmine INS 120, Gelatin INS 428) trigger critical violation for vegans."""
        parsed_additives = [
            {"code": "INS 120", "clean_code": "120", "name": "Carmine", "color_origin": "animal"},
            {"code": "INS 428", "clean_code": "428", "name": "Gelatin", "class": "Gelling agent"}
        ]
        profile = {
            "preset_name": "vegan",
            "avoid_animal_derivatives": True
        }
        res = evaluate_dietary_preferences(parsed_additives, "Gummy candy", profile)

        self.assertEqual(res["personal_score"], 60)  # 100 - 20 - 20
        self.assertEqual(len(res["critical_violations"]), 2)
        for v in res["critical_violations"]:
            self.assertEqual(v["type"], "animal_derived")
            self.assertEqual(v["severity"], "CRITICAL")

    def test_caution_ins_matching(self):
        """Caution INS code triggers mild 5 pt deduction without marking critical violation."""
        parsed_additives = [
            {"code": "INS 150d", "clean_code": "150d", "name": "Caramel IV", "class": "Color"}
        ]
        profile = {
            "preset_name": "custom",
            "custom_caution_ins": ["INS 150d"]
        }
        res = evaluate_dietary_preferences(parsed_additives, "Dark cola", profile)

        self.assertEqual(res["personal_score"], 95)  # 100 - 5
        self.assertEqual(len(res["critical_violations"]), 0)
        self.assertEqual(len(res["warnings"]), 1)
        self.assertEqual(res["warnings"][0]["type"], "custom_caution_code")

    def test_flavor_enhancer_msg_avoidance(self):
        """MSG (INS 621) triggers flavor enhancer deduction when avoid_msg_flavor_enhancers is active."""
        parsed_additives = [
            {"code": "INS 621", "clean_code": "621", "name": "Monosodium Glutamate", "functional_categories": ["Flavor enhancer"]}
        ]
        profile = {
            "preset_name": "custom",
            "avoid_msg_flavor_enhancers": True
        }
        res = evaluate_dietary_preferences(parsed_additives, "Savory seasoning", profile)

        self.assertEqual(res["personal_score"], 85)
        self.assertEqual(len(res["warnings"]), 1)
        self.assertEqual(res["warnings"][0]["type"], "flavor_enhancer")


class TestPresetMatchingAndScoring(unittest.TestCase):
    """Tests evaluating predefined dietary presets and transparent explanations."""

    def test_clean_label_preset_deductions(self):
        """Clean label preset avoids synthetic colors, preservatives, sweeteners, and flavor enhancers."""
        preset = DIETARY_PRESETS["clean_label"]
        parsed_additives = [
            {"code": "INS 102", "clean_code": "102", "name": "Tartrazine", "is_color": True, "color_origin": "synthetic"},
            {"code": "INS 211", "clean_code": "211", "name": "Sodium Benzoate", "functional_categories": ["Preservative"]},
            {"code": "INS 951", "clean_code": "951", "name": "Aspartame", "functional_categories": ["Sweetener"]}
        ]
        res = evaluate_dietary_preferences(parsed_additives, "Snack mix", preset)

        # INS 102 is in clean_label custom_avoid_ins (-20)
        # INS 211 is in clean_label custom_avoid_ins (-20)
        # INS 951 is an artificial sweetener (-15)
        self.assertLessEqual(res["personal_score"], 45)
        self.assertIn("Caution", res["personal_verdict"])
        self.assertTrue(len(res["score_deductions"]) >= 3)
        self.assertTrue(len(res["disclaimer"]) > 20)

    def test_guest_mode_no_profile(self):
        """Guest mode (empty or null profile) returns default baseline score 100."""
        parsed_additives = [
            {"code": "INS 102", "clean_code": "102", "name": "Tartrazine"}
        ]
        res = evaluate_dietary_preferences(parsed_additives, "Snack", {})
        self.assertEqual(res["personal_score"], 100)
        self.assertFalse(res["is_personalized"])
        self.assertEqual(len(res["score_deductions"]), 0)


class TestEndpointsPreferenceEvaluation(unittest.TestCase):
    """Integration tests for /api/v1/preferences/evaluate and /api/v1/analyze."""

    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.temp_db_fd)
        init_db(self.temp_db_path)
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_preferences_evaluate_endpoint_guest(self):
        """POST /api/v1/preferences/evaluate works with inline dietary_profile."""
        payload = {
            "raw_text": "Contains milk and peanuts. Acidity regulator INS 330, synthetic color INS 110.",
            "dietary_profile": {
                "preset_name": "custom",
                "custom_allergens": ["peanuts"],
                "avoid_synthetic_colors": True
            }
        }
        res = self.client.post("/api/v1/preferences/evaluate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("personal_evaluation", data)
        eval_res = data["personal_evaluation"]
        self.assertLessEqual(eval_res["personal_score"], 20)
        self.assertTrue(len(eval_res["allergen_alerts"]) > 0)
        self.assertTrue(any(w["type"] == "synthetic_color" for w in eval_res["warnings"]))

    def test_preferences_evaluate_endpoint_authenticated(self):
        """POST /api/v1/preferences/evaluate auto-resolves logged-in user profile."""
        ok, user_data, _ = register_user("eval_user", "eval@example.com", "Password123!", db_path=self.temp_db_path)
        ok_l, token_data, _ = authenticate_user("eval_user", "Password123!", db_path=self.temp_db_path)
        token = token_data["token"]

        # Call with auth token
        payload = {
            "raw_text": "Sugar, water, INS 102",
            "dietary_profile": {
                "avoid_synthetic_colors": True
            }
        }
        res = self.client.post(
            "/api/v1/preferences/evaluate",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["personal_evaluation"]["is_personalized"])


if __name__ == "__main__":
    unittest.main()
