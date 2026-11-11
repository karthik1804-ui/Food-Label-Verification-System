"""
Phase 4 Tests: User Authentication, Database Models & Dietary Profiles
======================================================================
Tests for:
  - backend/models/database.py (SQLite initialization and connection)
  - backend/models/user.py (User entity and validators)
  - backend/models/profile.py (DietaryProfile entity)
  - backend/models/analysis.py (AnalysisRecord entity)
  - backend/services/auth_service.py (Registration, PBKDF2:SHA256, Tokens, Presets)
  - backend/app.py (Auth and Profile endpoints)
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
from models.user import User
from models.profile import DietaryProfile
from models.analysis import AnalysisRecord
from services.auth_service import (
    register_user,
    authenticate_user,
    verify_token,
    revoke_token,
    get_user_profile,
    update_user_profile,
    get_user_preferences,
    update_category_preferences,
    manage_additive_preference,
    manage_allergy_preferences,
    DIETARY_PRESETS
)


class TestEntityModels(unittest.TestCase):
    """Unit tests for entity models and validation logic."""

    def test_user_validation_rules(self):
        """User model correctly validates username, email, and password."""
        # Valid cases
        self.assertTrue(User.validate_username("valid_user_123")[0])
        self.assertTrue(User.validate_email("researcher@university.edu")[0])
        self.assertTrue(User.validate_password("secure123")[0])

        # Invalid username
        self.assertFalse(User.validate_username("ab")[0])  # too short
        self.assertFalse(User.validate_username("user with spaces")[0])
        self.assertFalse(User.validate_username("user@invalid!")[0])

        # Invalid email
        self.assertFalse(User.validate_email("notanemail")[0])
        self.assertFalse(User.validate_email("user@nodomain")[0])

        # Invalid password
        self.assertFalse(User.validate_password("12345")[0])  # < 6 chars

    def test_user_serialization(self):
        """User.to_dict() omits password_hash unless explicitly requested."""
        user = User(
            id=1,
            username="john_doe",
            email="john@example.com",
            password_hash="pbkdf2:sha256:dummyhash"
        )
        safe_dict = user.to_dict()
        self.assertNotIn("password_hash", safe_dict)
        self.assertEqual(safe_dict["username"], "john_doe")

        sensitive_dict = user.to_dict(include_sensitive=True)
        self.assertIn("password_hash", sensitive_dict)

    def test_profile_serialization(self):
        """DietaryProfile serializes correctly."""
        profile = DietaryProfile(
            id=1,
            user_id=10,
            preset_name="vegan",
            avoid_animal_derivatives=True,
            custom_allergens=["dairy", "egg"]
        )
        d = profile.to_dict()
        self.assertEqual(d["preset_name"], "vegan")
        self.assertTrue(d["avoid_animal_derivatives"])
        self.assertIn("dairy", d["custom_allergens"])

    def test_analysis_record_serialization(self):
        """AnalysisRecord serializes and computes additives_count."""
        rec = AnalysisRecord(
            id=1,
            user_id=5,
            session_id="scan_1",
            ean="8901234567890",
            product_name="Test Product",
            raw_text="Contains INS 250",
            additives_summary=["INS 250"]
        )
        d = rec.to_dict()
        self.assertEqual(d["additives_count"], 1)
        self.assertEqual(d["ean"], "8901234567890")


class TestAuthServiceIsolated(unittest.TestCase):
    """Isolated tests for auth_service functions on temporary SQLite database."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_file.name
        self.temp_file.close()
        init_db(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass

    def test_register_success_and_default_profile(self):
        """Registering a user creates user row and linked dietary_profile row."""
        ok, user_data, err = register_user(
            username="analyst_1",
            email="analyst@foodlab.org",
            password="strongpassword2026",
            db_path=self.db_path
        )
        self.assertTrue(ok)
        self.assertIsNone(err)
        uid = user_data["id"]

        # Verify linked dietary profile exists
        profile = get_user_profile(uid, db_path=self.db_path)
        self.assertEqual(profile["user_id"], uid)
        self.assertEqual(profile["preset_name"], "custom")

    def test_register_duplicate_username_and_email(self):
        """Duplicate username or email must be rejected with informative error."""
        register_user("unique_name", "first@foodlab.org", "pass12345", db_path=self.db_path)

        # Duplicate username
        ok1, _, err1 = register_user("unique_name", "second@foodlab.org", "pass12345", db_path=self.db_path)
        self.assertFalse(ok1)
        self.assertIn("Username is already registered", err1)

        # Duplicate email
        ok2, _, err2 = register_user("another_name", "first@foodlab.org", "pass12345", db_path=self.db_path)
        self.assertFalse(ok2)
        self.assertIn("Email is already registered", err2)

    def test_authenticate_user_password_verification(self):
        """authenticate_user verifies password hash using PBKDF2:SHA256."""
        register_user("verifier", "verifier@foodlab.org", "correct_secret", db_path=self.db_path)

        # Correct password
        ok, auth_payload, _ = authenticate_user("verifier", "correct_secret", db_path=self.db_path)
        self.assertTrue(ok)
        self.assertIn("token", auth_payload)
        self.assertEqual(len(auth_payload["token"]), 64)  # 32 bytes hex = 64 chars

        # Incorrect password
        ok_bad, _, err_bad = authenticate_user("verifier", "wrong_secret", db_path=self.db_path)
        self.assertFalse(ok_bad)
        self.assertIn("Invalid username or password", err_bad)

        # Login with email instead of username
        ok_email, _, _ = authenticate_user("verifier@foodlab.org", "correct_secret", db_path=self.db_path)
        self.assertTrue(ok_email)

    def test_token_verification_and_revocation(self):
        """Tokens can be verified, checked for user identity, and revoked on logout."""
        register_user("session_user", "session@foodlab.org", "mypassword1", db_path=self.db_path)
        _, auth_payload, _ = authenticate_user("session_user", "mypassword1", db_path=self.db_path)
        token = auth_payload["token"]

        # Verify active token
        user_info = verify_token(token, db_path=self.db_path)
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info["username"], "session_user")

        # Verify with Bearer prefix
        user_info_bearer = verify_token(f"Bearer {token}", db_path=self.db_path)
        self.assertIsNotNone(user_info_bearer)

        # Revoke token (logout)
        revoked = revoke_token(token, db_path=self.db_path)
        self.assertTrue(revoked)

        # Subsequent verification must fail
        self.assertIsNone(verify_token(token, db_path=self.db_path))

    def test_update_profile_preset(self):
        """User profile can adopt standard dietary presets."""
        _, user, _ = register_user("clean_eater", "clean@foodlab.org", "cleanpass", db_path=self.db_path)
        uid = user["id"]

        ok, updated, _ = update_user_profile(
            uid,
            {"preset_name": "clean_label"},
            db_path=self.db_path
        )
        self.assertTrue(ok)
        self.assertEqual(updated["preset_name"], "clean_label")
        self.assertTrue(updated["avoid_synthetic_colors"])
        self.assertTrue(updated["avoid_preservatives"])
        self.assertIn("INS 102", updated["custom_avoid_ins"])

    def test_granular_preference_functions_isolated(self):
        """Granular category, additive, and allergy preference management."""
        _, user, _ = register_user("gran_user", "gran@foodlab.org", "password123", db_path=self.db_path)
        uid = user["id"]

        # 1. Update categories
        ok_cat, prof_cat, _ = update_category_preferences(
            uid,
            {"avoid_synthetic_colors": True, "avoid_preservatives": True},
            db_path=self.db_path
        )
        self.assertTrue(ok_cat)
        self.assertTrue(prof_cat["avoid_synthetic_colors"])
        self.assertTrue(prof_cat["avoid_preservatives"])

        # 2. Add and remove additives
        ok_add, prof_add, _ = manage_additive_preference(
            uid, action="add", code="102", pref_type="avoid", db_path=self.db_path
        )
        self.assertTrue(ok_add)
        self.assertIn("INS 102", prof_add["custom_avoid_ins"])

        ok_rem, prof_rem, _ = manage_additive_preference(
            uid, action="remove", code="INS 102", pref_type="avoid", db_path=self.db_path
        )
        self.assertTrue(ok_rem)
        self.assertNotIn("INS 102", prof_rem["custom_avoid_ins"])

        # 3. Add and remove allergies
        ok_alg1, prof_alg1, _ = manage_allergy_preferences(
            uid, action="add", allergens_input=["peanuts", "gluten"], db_path=self.db_path
        )
        self.assertTrue(ok_alg1)
        self.assertIn("peanuts", prof_alg1["custom_allergens"])
        self.assertIn("gluten", prof_alg1["custom_allergens"])

        ok_alg2, prof_alg2, _ = manage_allergy_preferences(
            uid, action="remove", allergens_input="peanuts", db_path=self.db_path
        )
        self.assertTrue(ok_alg2)
        self.assertNotIn("peanuts", prof_alg2["custom_allergens"])
        self.assertIn("gluten", prof_alg2["custom_allergens"])

        # 4. Get preferences
        prefs = get_user_preferences(uid, db_path=self.db_path)
        self.assertTrue(prefs["categories"]["avoid_synthetic_colors"])
        self.assertIn("gluten", prefs["custom_allergens"])


class TestAuthAPIEndpoints(unittest.TestCase):
    """Integration tests for Flask authentication API routes."""

    def setUp(self):
        from app import app
        self.client = app.test_client()

    def test_auth_endpoints_full_lifecycle(self):
        """Full registration, login, me, and logout HTTP request lifecycle."""
        # 1. Register new user
        reg_resp = self.client.post(
            "/api/v1/auth/register",
            data=json.dumps({
                "username": "phase4_user",
                "email": "phase4@verification.org",
                "password": "valid_phase4_password"
            }),
            content_type="application/json"
        )
        # 201 Created (or 400 if already created in earlier test run)
        self.assertIn(reg_resp.status_code, [201, 400])

        # 2. Login
        login_resp = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({
                "identifier": "phase4_user",
                "password": "valid_phase4_password"
            }),
            content_type="application/json"
        )
        self.assertEqual(login_resp.status_code, 200)
        body = login_resp.get_json()
        self.assertIn("token", body)
        self.assertIn("user", body)
        token = body["token"]

        # 3. GET /api/v1/auth/me with valid Bearer token
        me_resp = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(me_resp.status_code, 200)
        me_body = me_resp.get_json()
        self.assertEqual(me_body["user"]["username"], "phase4_user")
        self.assertIn("dietary_profile", me_body)

        # 4. GET /api/v1/auth/me without token -> 401 Unauthorized
        unauth_resp = self.client.get("/api/v1/auth/me")
        self.assertEqual(unauth_resp.status_code, 401)

        # 5. POST /api/v1/auth/logout
        logout_resp = self.client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(logout_resp.status_code, 200)

        # 6. Verify token is now invalid
        post_logout_me = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(post_logout_me.status_code, 401)

    def test_phase5_profile_and_preference_endpoints(self):
        """Phase 5 endpoints: GET/POST profile, preferences, categories, additives, and allergies."""
        # Setup user and get token
        self.client.post(
            "/api/v1/auth/register",
            data=json.dumps({"username": "phase5_user", "email": "p5@lab.org", "password": "password555"}),
            content_type="application/json"
        )
        login_res = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"identifier": "phase5_user", "password": "password555"}),
            content_type="application/json"
        )
        token = login_res.get_json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. GET /api/v1/profile
        p_get = self.client.get("/api/v1/profile", headers=headers)
        self.assertEqual(p_get.status_code, 200)
        self.assertIn("preset_name", p_get.get_json())

        # 2. POST /api/v1/profile (full update)
        p_post = self.client.post(
            "/api/v1/profile",
            headers=headers,
            data=json.dumps({"preset_name": "vegan"}),
            content_type="application/json"
        )
        self.assertEqual(p_post.status_code, 200)
        self.assertEqual(p_post.get_json()["dietary_profile"]["preset_name"], "vegan")

        # 3. GET /api/v1/profile/preferences
        prefs_get = self.client.get("/api/v1/profile/preferences", headers=headers)
        self.assertEqual(prefs_get.status_code, 200)
        p_body = prefs_get.get_json()
        self.assertIn("categories", p_body)
        self.assertIn("custom_allergens", p_body)

        # 4. POST /api/v1/profile/preferences/categories
        cat_res = self.client.post(
            "/api/v1/profile/preferences/categories",
            headers=headers,
            data=json.dumps({"avoid_synthetic_colors": True, "avoid_preservatives": True}),
            content_type="application/json"
        )
        self.assertEqual(cat_res.status_code, 200)
        self.assertTrue(cat_res.get_json()["dietary_profile"]["avoid_synthetic_colors"])

        # 5. POST /api/v1/profile/preferences/additives
        add_res = self.client.post(
            "/api/v1/profile/preferences/additives",
            headers=headers,
            data=json.dumps({"action": "add", "code": "INS 250", "type": "avoid"}),
            content_type="application/json"
        )
        self.assertEqual(add_res.status_code, 200)
        self.assertIn("INS 250", add_res.get_json()["dietary_profile"]["custom_avoid_ins"])

        # 6. POST /api/v1/profile/allergies
        alg_res = self.client.post(
            "/api/v1/profile/allergies",
            headers=headers,
            data=json.dumps({"action": "set", "allergens": ["peanuts", "dairy"]}),
            content_type="application/json"
        )
        self.assertEqual(alg_res.status_code, 200)
        self.assertIn("peanuts", alg_res.get_json()["dietary_profile"]["custom_allergens"])
        self.assertIn("dairy", alg_res.get_json()["dietary_profile"]["custom_allergens"])

        # 7. Unauthenticated access must be rejected
        unauth = self.client.get("/api/v1/profile/preferences")
        self.assertEqual(unauth.status_code, 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
