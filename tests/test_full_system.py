"""
Full System Unit and Integration Tests
======================================
Tests new services and API endpoints:
  - models/database.py (SQLite schema)
  - services/auth_service.py (Registration, PBKDF2 hashing, Tokens, Profiles)
  - services/preference_engine.py (Allergens, Category avoidance, Personal score)
  - services/barcode_decoder.py (OpenCV BarcodeDetector, no invented confidence)
  - services/personal_scoring.py (History logging, comprehensive orchestrator)
  - app.py endpoints (Auth, Profiles, Presets, History, Barcode Decode, Analyze)
"""

import os
import sys
import json
import base64
import tempfile
import unittest
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

from models.database import init_db, get_db_connection
from services.auth_service import (
    register_user,
    authenticate_user,
    verify_token,
    revoke_token,
    get_user_profile,
    update_user_profile,
    DIETARY_PRESETS
)
from services.preference_engine import evaluate_dietary_preferences, check_allergens
from services.barcode_decoder import decode_barcode_from_image
from services.personal_scoring import get_user_history


class TestDatabaseAndAuth(unittest.TestCase):
    """Tests for SQLite database and authentication service."""

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        init_db(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass

    def test_register_and_login_flow(self):
        """User can register with PBKDF2 password hashing and login to receive token."""
        ok, user_data, err = register_user(
            username="testuser",
            email="test@example.com",
            password="securepassword123",
            db_path=self.db_path
        )
        self.assertTrue(ok, f"Registration failed: {err}")
        self.assertEqual(user_data["username"], "testuser")

        # Duplicate registration must fail
        ok_dup, _, err_dup = register_user(
            username="testuser",
            email="test2@example.com",
            password="anotherpassword",
            db_path=self.db_path
        )
        self.assertFalse(ok_dup)

        # Login with correct password
        ok_login, auth_payload, err_login = authenticate_user(
            identifier="testuser",
            password="securepassword123",
            db_path=self.db_path
        )
        self.assertTrue(ok_login, f"Login failed: {err_login}")
        token = auth_payload.get("token")
        self.assertIsNotNone(token)
        self.assertGreater(len(token), 20)

        # Token verification
        user_verified = verify_token(token, db_path=self.db_path)
        self.assertIsNotNone(user_verified)
        self.assertEqual(user_verified["username"], "testuser")

        # Token revocation (logout)
        revoked = revoke_token(token, db_path=self.db_path)
        self.assertTrue(revoked)
        self.assertIsNone(verify_token(token, db_path=self.db_path))

    def test_login_incorrect_password(self):
        """Login with wrong password must be rejected."""
        register_user("user1", "user1@example.com", "pass123", db_path=self.db_path)
        ok, _, _ = authenticate_user("user1", "wrongpass", db_path=self.db_path)
        self.assertFalse(ok)

    def test_dietary_profile_presets_and_update(self):
        """User profile can be updated directly and via presets."""
        ok, user, _ = register_user("vegan_user", "vegan@example.com", "mypassword", db_path=self.db_path)
        uid = user["id"]

        # Default profile
        prof = get_user_profile(uid, db_path=self.db_path)
        self.assertEqual(prof["preset_name"], "custom")

        # Apply vegan preset
        ok_up, updated, _ = update_user_profile(
            uid,
            {"preset_name": "vegan"},
            db_path=self.db_path
        )
        self.assertTrue(ok_up)
        self.assertEqual(updated["preset_name"], "vegan")
        self.assertTrue(updated["avoid_animal_derivatives"])
        self.assertIn("INS 120", updated["custom_avoid_ins"])


class TestPreferenceEngine(unittest.TestCase):
    """Tests for preference engine and allergen detection."""

    def test_allergen_detection(self):
        """Direct text mention of allergens must produce high-priority alerts."""
        text = "Ingredients: Roasted peanuts, wheat flour, sugar, salt, palm oil."
        user_allergens = ["peanuts", "gluten"]
        alerts = check_allergens(text, user_allergens)
        self.assertEqual(len(alerts), 2)
        flagged = {a["allergen"] for a in alerts}
        self.assertIn("peanuts", flagged)
        self.assertIn("gluten", flagged)
        for a in alerts:
            self.assertEqual(a["severity"], "CRITICAL")

    def test_synthetic_color_conflict(self):
        """Synthetic color Tartrazine (E102) must trigger conflict when avoid_synthetic_colors is enabled."""
        additives = [{
            "code": "INS 102",
            "clean_code": "102",
            "name": "Tartrazine",
            "class": "Color",
            "color_origin": "synthetic",
            "functional_categories": ["Color"]
        }]
        profile = {"avoid_synthetic_colors": True}
        res = evaluate_dietary_preferences(additives, "Contains Tartrazine", profile)
        self.assertTrue(res["is_personalized"])
        self.assertLess(res["personal_score"], 100)
        self.assertEqual(len(res["preference_conflicts"]), 1)
        self.assertEqual(res["preference_conflicts"][0]["code"], "INS 102")

    def test_animal_derived_additive_conflict(self):
        """Carmine (INS 120) must be flagged for animal derivatives avoidance."""
        additives = [{
            "code": "INS 120",
            "clean_code": "120",
            "name": "Carmine",
            "class": "Color",
            "color_origin": "natural",
            "functional_categories": ["Color"]
        }]
        profile = {"avoid_animal_derivatives": True}
        res = evaluate_dietary_preferences(additives, "Contains Carmine", profile)
        self.assertLess(res["personal_score"], 100)
        self.assertTrue(any(c["conflict_type"] == "animal_derived" for c in res["preference_conflicts"]))


class TestBarcodeDecoder(unittest.TestCase):
    """Tests for OpenCV-based image barcode decoder."""

    def test_blank_image_returns_not_detected_status(self):
        """Blank image must return success=False and decode_status='not_detected' without arbitrary percentages."""
        blank = np.zeros((150, 150, 3), dtype=np.uint8)
        result = decode_barcode_from_image(blank)
        self.assertFalse(result["success"])
        self.assertEqual(result["decode_status"], "not_detected")
        self.assertNotIn("confidence", result, "No arbitrary float confidence should be invented")

    def test_corrupted_bytes_handled_safely(self):
        """Non-image bytes must return decoding_error status cleanly without crashing."""
        garbage_bytes = b"This is not a real image header"
        result = decode_barcode_from_image(garbage_bytes)
        self.assertFalse(result["success"])
        self.assertEqual(result["decode_status"], "decoding_error")


class TestSystemEndpoints(unittest.TestCase):
    """Integration tests for updated Flask app endpoints."""

    def setUp(self):
        from app import app
        self.client = app.test_client()

    def test_auth_and_profile_api(self):
        """Register, login, get profile, and get presets endpoints."""
        # 1. Register
        reg_resp = self.client.post(
            "/api/v1/auth/register",
            data=json.dumps({
                "username": "api_user_test",
                "email": "api_test@example.com",
                "password": "apipassword123"
            }),
            content_type="application/json"
        )
        self.assertIn(reg_resp.status_code, [201, 400])  # 400 if already exists

        # 2. Login
        login_resp = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({
                "identifier": "api_user_test",
                "password": "apipassword123"
            }),
            content_type="application/json"
        )
        self.assertEqual(login_resp.status_code, 200)
        body = login_resp.get_json()
        token = body.get("token")
        self.assertIsNotNone(token)

        # 3. GET /api/v1/auth/me
        me_resp = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(me_resp.status_code, 200)

        # 4. GET /api/v1/profile/presets
        presets_resp = self.client.get("/api/v1/profile/presets")
        self.assertEqual(presets_resp.status_code, 200)
        self.assertIn("presets", presets_resp.get_json())

        # 5. PUT /api/v1/profile
        update_resp = self.client.put(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
            data=json.dumps({"preset_name": "clean_label"}),
            content_type="application/json"
        )
        self.assertEqual(update_resp.status_code, 200)

    def test_analyze_with_dietary_profile_and_personal_score(self):
        """POST /api/v1/analyze returns both safety_indicator and personal_evaluation."""
        payload = {
            "text": "Ingredients: Refined wheat flour, water, salt, INS 102 (Tartrazine), INS 211 (Sodium Benzoate).",
            "ocr_confidence": 0.90,
            "dietary_profile": {
                "avoid_synthetic_colors": True,
                "avoid_preservatives": True,
                "custom_allergens": ["gluten"]
            }
        }
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()

        # Universal Safety Indicator present
        self.assertIn("safety_indicator", body)
        self.assertEqual(body["safety_indicator"].get("scoring_method"), "rule_based_indicator")

        # Personalised Dietary Evaluation present
        self.assertIn("personal_evaluation", body)
        p_eval = body["personal_evaluation"]
        self.assertTrue(p_eval["is_personalized"])
        self.assertLess(p_eval["personal_score"], 100)
        self.assertGreater(len(p_eval["allergen_alerts"]), 0, "Gluten allergen should be detected")
        self.assertGreater(len(p_eval["preference_conflicts"]), 0, "Tartrazine & Benzoate conflicts expected")

    def test_analyze_critical_ocr_uncertainty_warning(self):
        """ocr_confidence < 0.40 triggers ocr_uncertainty_warning = True in system_audit."""
        payload = {
            "text": "Contains INS 211",
            "ocr_confidence": 0.35
        }
        resp = self.client.post(
            "/api/v1/analyze",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        audit = body.get("system_audit", {})
        self.assertTrue(audit.get("ocr_uncertainty_warning"))
        self.assertTrue(audit.get("flagged_for_human_review"))
        self.assertTrue(any("Critical: Low OCR quality" in f for f in audit.get("flag_reasons", [])))

    def test_barcode_decode_endpoint_no_image_returns_400(self):
        """POST /api/v1/barcode/decode with empty body returns 400."""
        resp = self.client.post(
            "/api/v1/barcode/decode",
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
