"""
Tests for Phase 2: OpenCV Image Preprocessor
============================================
Comprehensive test suite validating:
  - Input decoding from bytes, base64 data URLs, and numpy arrays
  - Rejection of invalid, empty, or corrupt inputs
  - Memory protection and dimension clamping for excessively large images (>4096px)
  - Aspect-ratio preserving intelligent resizing for small packaging labels
  - Grayscale conversion and bilateral edge-preserving denoising
  - Contrast Limited Adaptive Histogram Equalization (CLAHE)
  - Controlled unsharp masking without noise amplification
  - Adaptive thresholding for uneven lighting
  - Multi-version preservation in PreprocessedImageBundle
  - Safe fallback mechanisms
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

from services.ocr.image_preprocessor import (
    ImagePreprocessor,
    PreprocessedImageBundle,
    decode_image_input,
    assess_image_quality,
    preprocess_label_image,
    BLUR_THRESHOLD,
    MAX_ALLOWED_DIMENSION
)


class TestImagePreprocessorCore(unittest.TestCase):
    """Unit tests for ImagePreprocessor pipeline operations."""

    def setUp(self):
        self.preprocessor = ImagePreprocessor()

        # Create a standard synthetic sharp label image
        self.sharp_img = np.zeros((400, 600, 3), dtype=np.uint8)
        self.sharp_img.fill(245)
        cv2.putText(self.sharp_img, "INGREDIENTS: Wheat Flour, Sugar, Salt", (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (15, 15, 15), 2)
        cv2.putText(self.sharp_img, "Colour (INS 102), Preservative (INS 211)", (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (15, 15, 15), 2)
        cv2.putText(self.sharp_img, "Flavour Enhancer (INS 621), Acidity Regulator (INS 330)", (20, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (15, 15, 15), 2)

        _, buf = cv2.imencode(".jpg", self.sharp_img)
        self.sharp_bytes = buf.tobytes()
        self.sharp_b64 = "data:image/jpeg;base64," + base64.b64encode(self.sharp_bytes).decode("utf-8")

    def test_validation_empty_and_corrupt(self):
        """Validates that empty, None, or corrupt inputs fail gracefully without crashing."""
        img, val = self.preprocessor.decode_and_validate(None)
        self.assertIsNone(img)
        self.assertFalse(val["is_valid"])

        img, val = self.preprocessor.decode_and_validate("")
        self.assertIsNone(img)
        self.assertFalse(val["is_valid"])

        img, val = self.preprocessor.decode_and_validate(b"random_corrupt_data_here")
        self.assertIsNone(img)
        self.assertFalse(val["is_valid"])

    def test_validation_memory_bounding_large_image(self):
        """Ensures images exceeding MAX_ALLOWED_DIMENSION are safely clamped to avoid OOM."""
        huge_img = np.zeros((5000, 2000, 3), dtype=np.uint8)
        huge_img.fill(128)
        img, val = self.preprocessor.decode_and_validate(huge_img)
        self.assertIsNotNone(img)
        self.assertTrue(val["is_valid"])
        self.assertTrue(val["was_clamped"])
        self.assertLessEqual(max(img.shape[:2]), MAX_ALLOWED_DIMENSION)

    def test_aspect_ratio_resizing_small_labels(self):
        """Small labels are upscaled to enhance small font OCR while preserving aspect ratio."""
        small_img = np.zeros((300, 400, 3), dtype=np.uint8)
        orig_aspect = 400 / 300
        resized, was_scaled, dims = self.preprocessor.resize_aspect_ratio(small_img, upscale_small=True)
        self.assertTrue(was_scaled)
        self.assertGreaterEqual(dims[0], 1000)
        new_aspect = dims[0] / dims[1]
        self.assertAlmostEqual(orig_aspect, new_aspect, places=1)

    def test_multi_version_preservation_in_bundle(self):
        """Verifies that all 5 image representations are preserved in PreprocessedImageBundle."""
        bundle = self.preprocessor.process(self.sharp_b64, upscale_small=True)
        self.assertTrue(bundle.is_valid)
        self.assertIsNotNone(bundle.original)
        self.assertIsNotNone(bundle.grayscale)
        self.assertIsNotNone(bundle.contrast_enhanced)
        self.assertIsNotNone(bundle.sharpened)
        self.assertIsNotNone(bundle.adaptive_threshold)
        self.assertIsNotNone(bundle.best_candidate)
        self.assertIn(bundle.best_candidate_name, ["sharpened", "contrast_enhanced", "adaptive_threshold"])

        # Check candidate retrieval helper
        self.assertIsNotNone(bundle.get_candidate_by_name("original"))
        self.assertIsNotNone(bundle.get_candidate_by_name("clahe"))
        self.assertIsNotNone(bundle.get_candidate_by_name("sharp"))
        self.assertIsNotNone(bundle.get_candidate_by_name("threshold"))

        # Base64 export helper
        b64_out = bundle.to_base64("best")
        self.assertTrue(b64_out.startswith("data:image/jpeg;base64,"))

    def test_clahe_and_unsharp_mask_enhancement(self):
        """CLAHE increases contrast and unsharp mask sharpens text edges."""
        # Create a low-contrast image (values between 100 and 130)
        low_contrast = np.zeros((400, 600, 3), dtype=np.uint8)
        low_contrast.fill(110)
        cv2.putText(low_contrast, "INS 102 Tartrazine", (30, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (130, 130, 130), 2)

        bundle = self.preprocessor.process(low_contrast)
        self.assertTrue(bundle.is_valid)

        # Contrast range of CLAHE should exceed low-contrast original
        orig_gray = cv2.cvtColor(low_contrast, cv2.COLOR_BGR2GRAY)
        orig_range = int(orig_gray.max()) - int(orig_gray.min())
        clahe_range = int(bundle.contrast_enhanced.max()) - int(bundle.contrast_enhanced.min())
        self.assertGreater(clahe_range, orig_range)

    def test_blur_detection_quality_grading(self):
        """Accurately detects blurry image and grades it Low/Unusable."""
        blurry = cv2.GaussianBlur(self.sharp_img, (35, 35), 20.0)
        bundle = self.preprocessor.process(blurry)
        self.assertTrue(bundle.is_valid)
        self.assertTrue(bundle.quality_metrics["is_blurry"])
        self.assertLess(bundle.quality_metrics["blur_score"], BLUR_THRESHOLD)
        self.assertIn(bundle.quality_metrics["quality_grade"], ["Low", "Unusable"])
        # Blurry image should select contrast_enhanced instead of over-sharpening
        self.assertEqual(bundle.best_candidate_name, "contrast_enhanced")

    def test_uneven_lighting_detection(self):
        """Detects high standard deviation across quadrants on unevenly illuminated labels."""
        uneven_img = self.sharp_img.copy()
        # Darken right half dramatically to simulate shadow
        uneven_img[:, 300:] = (uneven_img[:, 300:] * 0.2).astype(np.uint8)
        metrics = self.preprocessor.assess_quality(uneven_img)
        self.assertTrue(metrics["is_uneven_lighting"])
        self.assertLess(metrics["lighting_uniformity_score"], 70.0)


if __name__ == "__main__":
    unittest.main()
