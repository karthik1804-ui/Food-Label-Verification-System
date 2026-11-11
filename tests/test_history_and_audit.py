"""
Tests for Phase 10: Analysis History and Audit Records Management
=================================================================
Verifies:
  1. User scan history filtering (search, verdict, allergens, pagination).
  2. Single history record retrieval by ID.
  3. Single history record deletion.
  4. Clearing all history for an authenticated user.
  5. JSON and CSV export of scan history.
  6. Audit queue statistics endpoint (GET /api/v1/audit/stats).
  7. Audit record status filtering (GET /api/v1/audit/unmapped?status=...).
  8. Audit record deletion (DELETE /api/v1/audit/<record_id>).
"""

import os
import sys
import json
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

from app import app
from models.database import get_db_connection
import services.audit as audit_module


class TestHistoryAndAuditManagement(unittest.TestCase):
    """Integration and functional test suite for Phase 10."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

        # Temporary audit log for testing
        cls.test_audit_path = os.path.join(PROJECT_ROOT, "backend", "data", "test_audit_p10.json")
        cls.orig_audit_path = audit_module.AUDIT_LOG_PATH
        audit_module.AUDIT_LOG_PATH = cls.test_audit_path

    @classmethod
    def tearDownClass(cls):
        audit_module.AUDIT_LOG_PATH = cls.orig_audit_path
        if os.path.exists(cls.test_audit_path):
            os.remove(cls.test_audit_path)

    def setUp(self):
        self.username = "history_tester_p10"
        self.email = "history_p10@example.com"
        self.password = "Secur3P@ssw0rd!"

        # Register if not already exists
        self.client.post(
            "/api/v1/auth/register",
            json={"username": self.username, "email": self.email, "password": self.password}
        )

        # Login to obtain fresh bearer token
        login_resp = self.client.post(
            "/api/v1/auth/login",
            json={"identifier": self.username, "password": self.password}
        )
        self.assertEqual(login_resp.status_code, 200)
        auth_data = login_resp.get_json()
        self.token = auth_data["token"]
        self.user_id = auth_data["user"]["id"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # Clear existing history and seed fresh test scans
        conn = get_db_connection()
        conn.execute("DELETE FROM analysis_history WHERE user_id = ?", (self.user_id,))
        
        # Seed 3 distinct scans
        scans = [
            (
                self.user_id, "scan_1", "8901234567890", "Instant Masala Noodles",
                "Ingredients: Wheat Flour, Palm Oil, INS 621, INS 150d. Contains Wheat.",
                0.95, 74.0, "C", 85.0, "Compatible",
                json.dumps([]), json.dumps(["INS 621", "INS 150d"]), "{}"
            ),
            (
                self.user_id, "scan_2", "8901030000003", "Classic Potato Crisps",
                "Ingredients: Potato, Palm Oil, Salt, Milk Solids, INS 627, INS 631. CONTAINS MILK.",
                0.88, 68.0, "D", 20.0, "ALLERGEN WARNING: Milk",
                json.dumps([{"allergen": "milk", "matched_term": "milk solids", "action_required": "Avoid"}]),
                json.dumps(["INS 627", "INS 631"]), "{}"
            ),
            (
                self.user_id, "scan_3", "N/A", "Fresh Fruit Granola",
                "Ingredients: Rolled Oats, Honey, Almonds, Cinnamon. Contains Almonds.",
                0.92, 95.0, "A", 95.0, "Compatible",
                json.dumps([]), json.dumps([]), "{}"
            )
        ]

        conn.executemany(
            """
            INSERT INTO analysis_history (
                user_id, session_id, ean, product_name, raw_text, ocr_confidence,
                final_score, grade, personal_score, personal_verdict,
                allergen_alerts, additives_summary, system_audit_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            scans
        )
        conn.commit()
        conn.close()

        # Seed temporary audit records
        audit_records = [
            {
                "id": "audit_rec_1",
                "timestamp": "2026-11-06T10:00:00Z",
                "context_identifier": "Instant Noodles",
                "unmapped_tokens": ["UNMAPPED_FLAVOUR_X"],
                "additive_match_confidence": 0.8,
                "ocr_confidence": 0.9,
                "audit_status": "PENDING_EXPERT_REVIEW",
                "review_history": []
            },
            {
                "id": "audit_rec_2",
                "timestamp": "2026-11-06T10:05:00Z",
                "context_identifier": "Energy Bar",
                "unmapped_tokens": ["BIO_EXTRACT_Z"],
                "additive_match_confidence": 0.7,
                "ocr_confidence": 0.85,
                "audit_status": "CONFIRMED_BY_REVIEWER",
                "review_history": [{"timestamp": "2026-11-06T10:10:00Z", "action": "confirm", "reviewer_note": "Botanical extract"}]
            }
        ]
        with open(self.test_audit_path, "w", encoding="utf-8") as f:
            json.dump(audit_records, f, indent=2)

    def test_01_get_history_all_and_pagination(self):
        """GET /api/v1/history returns all 3 records with total_count."""
        resp = self.client.get("/api/v1/history?limit=2&offset=0", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("history", data)
        self.assertEqual(len(data["history"]), 2)
        self.assertEqual(data["total_count"], 3)
        self.assertEqual(data["count"], 2)

    def test_02_get_history_search_filter(self):
        """Search query matches product_name or ean."""
        resp = self.client.get("/api/v1/history?search=Noodles", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["total_count"], 1)
        self.assertEqual(data["history"][0]["product_name"], "Instant Masala Noodles")

        # Search by barcode
        resp2 = self.client.get("/api/v1/history?search=8901030000003", headers=self.headers)
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.get_json()
        self.assertEqual(data2["total_count"], 1)
        self.assertEqual(data2["history"][0]["product_name"], "Classic Potato Crisps")

    def test_03_get_history_verdict_and_allergen_filter(self):
        """Filtering by allergen presence or specific verdict."""
        # Allergen only filter
        resp = self.client.get("/api/v1/history?has_allergens=true", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["total_count"], 1)
        self.assertEqual(data["history"][0]["product_name"], "Classic Potato Crisps")

        # Verdict filter
        resp2 = self.client.get("/api/v1/history?verdict=Compatible", headers=self.headers)
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.get_json()
        self.assertEqual(data2["total_count"], 2)

    def test_04_get_single_history_record_by_id(self):
        """GET /api/v1/history/<id> returns complete record with raw_text."""
        # First get ID from list
        resp = self.client.get("/api/v1/history", headers=self.headers)
        rec_id = resp.get_json()["history"][0]["id"]

        resp_single = self.client.get(f"/api/v1/history/{rec_id}", headers=self.headers)
        self.assertEqual(resp_single.status_code, 200)
        single_data = resp_single.get_json()["record"]
        self.assertEqual(single_data["id"], rec_id)
        self.assertIn("raw_text", single_data)
        self.assertIn("final_score", single_data)

    def test_05_delete_single_history_record(self):
        """DELETE /api/v1/history/<id> deletes specified record."""
        resp = self.client.get("/api/v1/history", headers=self.headers)
        initial_count = resp.get_json()["total_count"]
        rec_id = resp.get_json()["history"][0]["id"]

        del_resp = self.client.delete(f"/api/v1/history/{rec_id}", headers=self.headers)
        self.assertEqual(del_resp.status_code, 200)

        # Confirm count decreased by 1
        resp_after = self.client.get("/api/v1/history", headers=self.headers)
        self.assertEqual(resp_after.get_json()["total_count"], initial_count - 1)

    def test_06_clear_all_user_history(self):
        """DELETE /api/v1/history clears all user records."""
        del_resp = self.client.delete("/api/v1/history", headers=self.headers)
        self.assertEqual(del_resp.status_code, 200)
        self.assertTrue(del_resp.get_json()["deleted_count"] >= 1)

        resp_after = self.client.get("/api/v1/history", headers=self.headers)
        self.assertEqual(resp_after.get_json()["total_count"], 0)

    def test_07_export_history_json_and_csv(self):
        """GET /api/v1/history/export returns JSON or CSV formatted stream."""
        # JSON export
        resp_json = self.client.get("/api/v1/history/export?format=json", headers=self.headers)
        self.assertEqual(resp_json.status_code, 200)
        self.assertEqual(resp_json.mimetype, "application/json")
        exported = json.loads(resp_json.data.decode("utf-8"))
        self.assertIn("history", exported)
        self.assertEqual(len(exported["history"]), 3)

        # CSV export
        resp_csv = self.client.get("/api/v1/history/export?format=csv", headers=self.headers)
        self.assertEqual(resp_csv.status_code, 200)
        self.assertEqual(resp_csv.mimetype, "text/csv")
        csv_text = resp_csv.data.decode("utf-8")
        self.assertIn("Product Name,EAN Barcode,Safety Score", csv_text)
        self.assertIn("Instant Masala Noodles", csv_text)

    def test_08_audit_stats_endpoint(self):
        """GET /api/v1/audit/stats returns aggregated metrics across the queue."""
        resp = self.client.get("/api/v1/audit/stats")
        self.assertEqual(resp.status_code, 200)
        stats = resp.get_json()
        self.assertEqual(stats["total_records"], 2)
        self.assertEqual(stats["pending_count"], 1)
        self.assertEqual(stats["confirmed_count"], 1)
        self.assertEqual(stats["rejected_count"], 0)
        self.assertIn("UNMAPPED_FLAVOUR_X", stats["unique_unmapped_tokens"])

    def test_09_audit_status_filtering(self):
        """GET /api/v1/audit/unmapped?status=... filters by pending/confirmed."""
        resp_pending = self.client.get("/api/v1/audit/unmapped?status=PENDING_EXPERT_REVIEW")
        self.assertEqual(resp_pending.status_code, 200)
        data = resp_pending.get_json()
        self.assertEqual(data["total_records"], 1)
        self.assertEqual(data["records"][0]["id"], "audit_rec_1")

        # Shorthand filter
        resp_short = self.client.get("/api/v1/audit/unmapped?status=confirmed")
        self.assertEqual(resp_short.status_code, 200)
        data_short = resp_short.get_json()
        self.assertEqual(data_short["total_records"], 1)
        self.assertEqual(data_short["records"][0]["id"], "audit_rec_2")

    def test_10_delete_audit_record(self):
        """DELETE /api/v1/audit/<record_id> removes an audit record."""
        resp = self.client.delete("/api/v1/audit/audit_rec_1")
        self.assertEqual(resp.status_code, 200)

        # Confirm it's gone
        resp_list = self.client.get("/api/v1/audit/unmapped")
        self.assertEqual(resp_list.get_json()["total_records"], 1)
        self.assertEqual(resp_list.get_json()["records"][0]["id"], "audit_rec_2")


if __name__ == "__main__":
    unittest.main()
