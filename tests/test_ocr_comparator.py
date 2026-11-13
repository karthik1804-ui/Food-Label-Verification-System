"""
Tests for Phase 4: OCR Comparison Mode
======================================
Validates:
  - Levenshtein similarity metric calculation
  - Detection of character confusion corrections (1NS -> INS, 1O2 -> 102, 62I -> 621)
  - Differential downstream additive extraction between Config A and Config B
  - Structured comparison payload integrity (does not merge outputs)
  - REST endpoint: POST /api/v1/ocr/compare
"""

import os
import sys
import unittest
import base64
import numpy as np
import cv2

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

from services.ocr.ocr_comparator import (
    compare_ocr_results,
    compute_levenshtein_similarity,
    detect_character_confusion_fixes
)
from app import app


class TestOcrComparator(unittest.TestCase):
    """Test suite for OCR comparison engine and endpoint."""

    def setUp(self):
        self.client = app.test_client()

    def test_levenshtein_similarity_identical_and_differing(self):
        """Calculates accurate normalized similarity ratio."""
        self.assertEqual(compute_levenshtein_similarity("Ingredients: Sugar, Salt", "Ingredients: Sugar, Salt"), 1.0)
        self.assertEqual(compute_levenshtein_similarity("", ""), 1.0)
        self.assertEqual(compute_levenshtein_similarity("ABC", ""), 0.0)

        sim = compute_levenshtein_similarity("Wheat Flour, 1NS 102", "Wheat Flour, INS 102")
        self.assertGreater(sim, 0.90)

    def test_detect_character_confusion_fixes(self):
        """Identifies known OCR character confusions corrected between Config A and Config B."""
        text_a = "Ingredients: 1NS 1O2 Tartrazine, 1NS 211, Flavour 62I"
        text_b = "Ingredients: INS 102 Tartrazine, INS 211, Flavour 621"

        fixes = detect_character_confusion_fixes(text_a, text_b)
        self.assertTrue(len(fixes) >= 3)
        tokens_fixed = [f["erroneous_token_in_a"] for f in fixes]
        self.assertIn("1NS", tokens_fixed)
        self.assertIn("1O2", tokens_fixed)
        self.assertIn("62I", tokens_fixed)

    def test_compare_ocr_results_structure_and_additives(self):
        """Generates structured comparison with word counts, confidence delta, and INS parsing."""
        # Config A is missing INS 102 due to poor contrast
        text_a = "Ingredients: Water, Sugar, Preservative INS 211"
        # Config B has crisp OCR with INS 102 detected
        text_b = "Ingredients: Water, Sugar, INS 102, Preservative INS 211"

        res = compare_ocr_results(
            text_a=text_a,
            text_b=text_b,
            confidence_a=0.72,
            confidence_b=0.88,
            timings_a={"ocr_ms": 15.0},
            timings_b={"preprocessing_ms": 8.0, "ocr_ms": 16.0}
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["config_a"]["confidence"], 0.72)
        self.assertEqual(res["config_b"]["confidence"], 0.88)
        self.assertAlmostEqual(res["comparison_metrics"]["confidence_delta"], 0.16, places=2)

        # INS 102 should be recognized in Config B
        self.assertIn("INS 102", res["comparison_metrics"]["new_ins_codes_detected_in_b"])
        # Outputs must remain strictly separated (not merged)
        self.assertEqual(res["config_a"]["text"], text_a)
        self.assertEqual(res["config_b"]["text"], text_b)

    def test_api_ocr_compare_endpoint(self):
        """POST /api/v1/ocr/compare returns structured comparison JSON."""
        # Create small test image
        img = np.zeros((200, 300, 3), dtype=np.uint8)
        img.fill(240)
        _, buf = cv2.imencode(".jpg", img)
        img_b64 = "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode("utf-8")

        payload = {
            "image_base64": img_b64,
            "text_a": "Flour, Sugar, 1NS 102",
            "text_b": "Flour, Sugar, INS 102",
            "confidence_a": 0.70,
            "confidence_b": 0.85
        }
        res = self.client.post("/api/v1/ocr/compare", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertEqual(data["status"], "success")
        self.assertIn("config_a", data)
        self.assertIn("config_b", data)
        self.assertIn("comparison_metrics", data)
        self.assertIn("prepared_images", data)


if __name__ == "__main__":
    unittest.main()
