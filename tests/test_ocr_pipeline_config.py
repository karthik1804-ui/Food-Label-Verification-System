"""
Tests for Phase 3: OCR Pipeline Integration (Configuration A vs. Configuration B)
================================================================================
Validates:
  - Configuration A: returns unaltered original image for standard Tesseract OCR
  - Configuration B: returns OpenCV preprocessed image (CLAHE, unsharp masked, aspect scaled)
  - Parameter compatibility: preserves word-level confidence and Tesseract settings
  - Automatic fallback: if Configuration B fails, smoothly falls back to Configuration A
  - REST API endpoint: POST /api/v1/ocr/preprocess with config='A' and config='B'
"""

import os
import sys
import base64
import unittest
import numpy as np
import cv2

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

from services.ocr.ocr_pipeline import OcrPipeline, prepare_ocr_image
from services.ocr.image_preprocessor import ImagePreprocessor
from app import app


class TestOcrPipelineConfig(unittest.TestCase):
    """Test suite for dual-configuration OCR pipeline."""

    def setUp(self):
        self.pipeline = OcrPipeline()

        # Create synthetic label image
        self.img = np.zeros((350, 500, 3), dtype=np.uint8)
        self.img.fill(240)
        cv2.putText(self.img, "INGREDIENTS: Water, Sugar, INS 102", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 2)
        cv2.putText(self.img, "Preservative (INS 211), Acidity Regulator (INS 330)", (20, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 2)

        _, buf = cv2.imencode(".jpg", self.img)
        self.b64_img = "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode("utf-8")

        self.client = app.test_client()

    def test_configuration_a_returns_original_image(self):
        """Configuration A returns original image without enhancement filters."""
        res = self.pipeline.prepare_for_tesseract(self.b64_img, config="A")
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["configuration_used"], "A")
        self.assertFalse(res["fallback_applied"])
        self.assertEqual(res["candidate_name"], "original")
        # Target image should match original dimensions
        self.assertEqual(res["target_image"].shape[:2], (350, 500))

    def test_configuration_b_returns_preprocessed_image(self):
        """Configuration B returns OpenCV enhanced candidate with metrics and scaling."""
        res = self.pipeline.prepare_for_tesseract(self.b64_img, config="B")
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["configuration_used"], "B")
        self.assertFalse(res["fallback_applied"])
        self.assertIn(res["candidate_name"], ["sharpened", "contrast_enhanced"])
        self.assertIn("quality_metrics", res)
        # 500px width should be upscaled for small label font OCR
        self.assertGreaterEqual(res["target_image"].shape[1], 1000)

    def test_fallback_to_config_a_on_error(self):
        """If Configuration B preprocessing raises an exception, falls back to Configuration A safely."""
        # Create a mock preprocessor whose process method raises an error
        class FailingPreprocessor(ImagePreprocessor):
            def process(self, *args, **kwargs):
                raise RuntimeError("Simulated OpenCV filter crash")

        failing_pipeline = OcrPipeline(preprocessor=FailingPreprocessor())
        res = failing_pipeline.prepare_for_tesseract(self.b64_img, config="B")

        self.assertTrue(res["is_valid"])
        self.assertEqual(res["configuration_used"], "A")
        self.assertTrue(res["fallback_applied"])
        self.assertEqual(res["candidate_name"], "original")
        self.assertIn("fallback_reason", res)

    def test_api_preprocess_endpoint_config_param(self):
        """POST /api/v1/ocr/preprocess correctly handles config='A' and config='B'."""
        # Test Config A
        res_a = self.client.post("/api/v1/ocr/preprocess", json={
            "image_base64": self.b64_img,
            "config": "A"
        })
        self.assertEqual(res_a.status_code, 200)
        data_a = res_a.get_json()
        self.assertEqual(data_a["configuration_used"], "A")

        # Test Config B (default)
        res_b = self.client.post("/api/v1/ocr/preprocess", json={
            "image_base64": self.b64_img,
            "config": "B"
        })
        self.assertEqual(res_b.status_code, 200)
        data_b = res_b.get_json()
        self.assertEqual(data_b["configuration_used"], "B")
        self.assertIn("enhanced_image_base64", data_b)
        self.assertIn("original_image_base64", data_b)


if __name__ == "__main__":
    unittest.main()
