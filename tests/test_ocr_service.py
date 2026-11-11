"""
Phase 7 Tests: OCR Image Preprocessing, Ingredient Section Identification & Safety Gate
========================================================================================
Comprehensive test suite for:
  - backend/services/ocr_service.py
  - Image decoding and quality assessment (Laplacian blur variance, dimensions)
  - CLAHE contrast enhancement and unsharp masking for curved/small packaging fonts
  - Ingredient section header isolation and boundary extraction
  - Parenthesis-aware ingredient clause separation
  - OCR safety gate: prevents definitive dietary scoring from low-confidence / blurry OCR
  - REST endpoints: POST /api/v1/ocr/preprocess and POST /api/v1/ocr/extract-section
  - Integration with POST /api/v1/analyze
"""

import os
import sys
import json
import base64
import unittest
import numpy as np
import cv2

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

from services.ocr_service import (
    decode_image_input,
    assess_image_quality,
    preprocess_label_image,
    identify_ingredient_section,
    clean_and_separate_ingredients,
    evaluate_ocr_quality_and_safety_gate,
    BLUR_THRESHOLD
)
from app import app


class TestImagePreprocessing(unittest.TestCase):
    """Tests for OpenCV image decoding, blur metrics, and enhancement filters."""

    def setUp(self):
        # Create a sharp synthetic packaging image
        self.sharp_img = np.zeros((400, 600, 3), dtype=np.uint8)
        self.sharp_img.fill(240)
        cv2.putText(self.sharp_img, "INGREDIENTS: Wheat flour, Sugar, INS 102", (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2)
        cv2.putText(self.sharp_img, "Preservative INS 211, Citric Acid INS 330", (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2)

        # Create a heavily blurred image
        self.blurry_img = cv2.GaussianBlur(self.sharp_img, (31, 31), 15.0)

    def test_decode_image_input_variants(self):
        """Decodes raw bytes, base64 strings, and numpy arrays correctly."""
        # 1. Direct numpy array
        self.assertIsNotNone(decode_image_input(self.sharp_img))

        # 2. Encoded bytes
        _, buffer = cv2.imencode(".jpg", self.sharp_img)
        img_bytes = buffer.tobytes()
        decoded_from_bytes = decode_image_input(img_bytes)
        self.assertIsNotNone(decoded_from_bytes)
        self.assertEqual(decoded_from_bytes.shape[0], 400)

        # 3. Base64 data URL
        b64_str = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode("utf-8")
        decoded_from_b64 = decode_image_input(b64_str)
        self.assertIsNotNone(decoded_from_b64)

        # 4. Corrupted / invalid input returns None
        self.assertIsNone(decode_image_input(b"not_an_image_header"))
        self.assertIsNone(decode_image_input(None))

    def test_assess_image_quality_sharp_vs_blurry(self):
        """Correctly classifies sharp text vs blurry degraded capture."""
        sharp_metrics = assess_image_quality(self.sharp_img)
        self.assertTrue(sharp_metrics["is_valid"])
        self.assertFalse(sharp_metrics["is_blurry"])
        self.assertGreater(sharp_metrics["blur_score"], BLUR_THRESHOLD)

        blurry_metrics = assess_image_quality(self.blurry_img)
        self.assertTrue(blurry_metrics["is_valid"])
        self.assertTrue(blurry_metrics["is_blurry"])
        self.assertLess(blurry_metrics["blur_score"], BLUR_THRESHOLD)
        self.assertIn(blurry_metrics["quality_grade"], ["Low", "Unusable"])

    def test_preprocess_label_image_enhancement(self):
        """Applies CLAHE and unsharp masking, returning grayscale enhanced frame."""
        enhanced, metrics = preprocess_label_image(self.sharp_img, upscale_small=True)
        self.assertIsNotNone(enhanced)
        self.assertEqual(len(enhanced.shape), 2)  # Grayscale
        self.assertTrue(metrics["is_valid"])
        # Low-res 600px width should be upscaled
        self.assertTrue(metrics.get("upscaled", False))
        self.assertGreaterEqual(metrics["processed_dimensions"][0], 1000)


class TestIngredientSectionExtraction(unittest.TestCase):
    """Tests for ingredient header identification and clause separation."""

    def test_identify_ingredient_section_with_surrounding_noise(self):
        """Extracts ingredient section and excludes manufacturer address and nutrition facts."""
        label_text = (
            "Manufactured by Global Foods Ltd, Industrial Area Phase II, Mumbai 400001. "
            "Net Wt. 250 g. "
            "INGREDIENTS: Wheat Flour (65%), Edible Vegetable Oil, Sugar, "
            "Permitted Synthetic Food Colour (INS 102), Acidity Regulator (INS 330). "
            "NUTRITION INFORMATION per 100g: Energy 450 kcal, Protein 7g, Carbohydrates 65g. "
            "Store in a cool and dry place."
        )
        res = identify_ingredient_section(label_text)
        self.assertTrue(res["section_found"])
        self.assertGreaterEqual(res["confidence_indicator"], 0.90)

        ing_text = res["ingredient_text"]
        self.assertIn("Wheat Flour", ing_text)
        self.assertIn("INS 102", ing_text)
        self.assertNotIn("Manufactured by", ing_text)
        self.assertNotIn("NUTRITION INFORMATION", ing_text)

    def test_identify_ingredient_section_fallback_without_header(self):
        """When no header is present, returns full text with lower section confidence."""
        raw_text = "Sugar, Cocoa Solids, Emulsifier INS 322, Artificial Vanilla Flavour."
        res = identify_ingredient_section(raw_text)
        self.assertFalse(res["section_found"])
        self.assertEqual(res["ingredient_text"], raw_text)
        self.assertEqual(res["confidence_indicator"], 0.5)

    def test_clean_and_separate_ingredients_parenthesis_aware(self):
        """Splits ingredients on commas but keeps commas inside parentheses intact."""
        text = (
            "Refined Wheat Flour, Sugar, Hydrogenated Vegetable Oil, "
            "Permitted Synthetic Colours (INS 102, INS 110), "
            "Emulsifiers (1NS 322, INS 471), Iodised Salt, Raising Agent (INS 500(ii))."
        )
        items = clean_and_separate_ingredients(text)

        # Expected clauses:
        # 1. Refined Wheat Flour
        # 2. Sugar
        # 3. Hydrogenated Vegetable Oil
        # 4. Permitted Synthetic Colours (INS 102, INS 110)  <- NOT split!
        # 5. Emulsifiers (INS 322, INS 471)                 <- 1NS normalized to INS!
        # 6. Iodised Salt
        # 7. Raising Agent (INS 500(ii))
        self.assertEqual(len(items), 7)
        self.assertIn("Permitted Synthetic Colours (INS 102, INS 110)", items)
        self.assertTrue(any("INS 322" in it for it in items))  # Normalized from 1NS 322


class TestOcrSafetyGate(unittest.TestCase):
    """Tests for academic OCR confidence gate and score suppression."""

    def test_low_confidence_triggers_safety_warning_and_score_suppression(self):
        """OCR confidence < 0.40 suppresses definitive dietary score and flags extraction warning."""
        res = evaluate_ocr_quality_and_safety_gate(
            ocr_confidence=0.35,
            raw_text="Wheat flour, sugar, unknown #$# chemicals."
        )
        self.assertFalse(res["is_safe_for_decision"])
        self.assertTrue(res["definitive_dietary_score_suppressed"])
        self.assertIsNotNone(res["safety_warning"])
        self.assertIn("EXTRACTION WARNING", res["safety_warning"])
        self.assertTrue(len(res["flag_reasons"]) > 0)
        self.assertIsNotNone(res["recommendation"])

    def test_blurry_image_triggers_safety_warning(self):
        """Blurry image suppresses definitive score even if word confidence is nominal."""
        image_quality = {
            "is_blurry": True,
            "blur_score": 45.0,
            "quality_grade": "Low"
        }
        res = evaluate_ocr_quality_and_safety_gate(
            ocr_confidence=0.85,
            raw_text="Sugar, flour, salt",
            image_quality=image_quality
        )
        self.assertFalse(res["is_safe_for_decision"])
        self.assertTrue(res["definitive_dietary_score_suppressed"])
        self.assertTrue(any("blurry" in r.lower() for r in res["flag_reasons"]))

    def test_high_quality_ocr_passes_safety_gate(self):
        """Good OCR confidence and clean text pass the safety gate cleanly."""
        res = evaluate_ocr_quality_and_safety_gate(
            ocr_confidence=0.92,
            raw_text="Ingredients: Sugar, Wheat Flour, Cocoa Powder, Emulsifier INS 322.",
            image_quality={"is_blurry": False, "blur_score": 150.0, "quality_grade": "High"}
        )
        self.assertTrue(res["is_safe_for_decision"])
        self.assertFalse(res["definitive_dietary_score_suppressed"])
        self.assertIsNone(res["safety_warning"])
        self.assertEqual(len(res["flag_reasons"]), 0)


class TestOcrApiEndpoints(unittest.TestCase):
    """Integration tests for Flask OCR endpoints."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

        # Synthetic test image
        img = np.zeros((300, 500, 3), dtype=np.uint8)
        img.fill(250)
        cv2.putText(img, "INGREDIENTS: Water, Sugar, INS 102", (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        _, buffer = cv2.imencode(".jpg", img)
        self.test_b64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")

    def test_ocr_preprocess_endpoint(self):
        """POST /api/v1/ocr/preprocess returns quality metrics and enhanced image."""
        payload = {"image_base64": self.test_b64}
        res = self.client.post("/api/v1/ocr/preprocess", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("quality_metrics", data)
        self.assertIn("enhanced_image_base64", data)
        self.assertTrue(data["quality_metrics"]["is_valid"])

    def test_ocr_preprocess_endpoint_empty_error(self):
        """POST /api/v1/ocr/preprocess returns 400 on empty input."""
        res = self.client.post("/api/v1/ocr/preprocess", json={})
        self.assertEqual(res.status_code, 400)

    def test_ocr_extract_section_endpoint(self):
        """POST /api/v1/ocr/extract-section isolates ingredients and checks OCR safety."""
        payload = {
            "raw_text": "Mfg: 2026. INGREDIENTS: Sugar, Milk Solid, INS 102, INS 211. Net Wt 100g.",
            "ocr_confidence": 0.88
        }
        res = self.client.post("/api/v1/ocr/extract-section", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["section_info"]["section_found"])
        self.assertTrue(data["separated_count"] >= 3)
        self.assertTrue(data["ocr_safety"]["is_safe_for_decision"])

    def test_analyze_endpoint_provisional_on_low_ocr_confidence(self):
        """POST /api/v1/analyze marks provisional verdict when ocr_confidence is low."""
        payload = {
            "text": "Sugar, INS 102",
            "ocr_confidence": 0.25,  # Critical low confidence
            "dietary_profile": {"avoid_synthetic_colors": True}
        }
        res = self.client.post("/api/v1/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        personal_eval = data["personal_evaluation"]
        system_audit = data["system_audit"]

        self.assertTrue(system_audit["ocr_uncertainty_warning"])
        self.assertTrue(personal_eval.get("is_provisional", False))
        self.assertTrue(personal_eval.get("definitive_score_suppressed", False))
        self.assertIn("PROVISIONAL", personal_eval["personal_verdict"])


if __name__ == "__main__":
    unittest.main()
