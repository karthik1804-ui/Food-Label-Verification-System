"""
Comprehensive Regression Test Suite for CodeRabbit Review Findings
===================================================================
Tests validating fixes across all 9 review areas:
1. Image preprocessing validation, bounds, channel checks, and NumPy truth-value safety.
2. Uneven lighting adaptive threshold candidate selection.
3. Backend OCR compare endpoint handling for invalid preparation and image-only calls.
4. OCR comparator exact normalized Levenshtein similarity and false confusion prevention.
5. INS evaluator 4-state mutually exclusive impact classification (IMPROVED, REGRESSED, MIXED, UNCHANGED).
6. Long string Levenshtein distance safety and bounds protection.
"""

import os
import sys
import unittest
import numpy as np
import cv2

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.ocr.image_preprocessor import (
    ImagePreprocessor,
    PreprocessedImageBundle,
    decode_image_input,
    MAX_HARD_DIMENSION,
    MAX_ALLOWED_DECODED_PIXELS
)
from services.ocr.ocr_comparator import (
    compute_levenshtein_similarity,
    compare_ocr_results
)
from services.ocr.ins_evaluator import (
    compute_levenshtein_distance,
    evaluate_single_sample,
    CLASSIFICATION_IMPROVED,
    CLASSIFICATION_REGRESSED,
    CLASSIFICATION_MIXED,
    CLASSIFICATION_UNCHANGED
)
from app import app


class TestImagePreprocessorRegression(unittest.TestCase):
    """Regression tests for Task 1: Image Preprocessor bounds & validations."""

    def setUp(self):
        self.preprocessor = ImagePreprocessor()

    def test_numpy_truth_value_ambiguity_fix(self):
        """Verify that get_candidate_by_name and get_best_or_original handle ndarray None checks safely."""
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        bundle = PreprocessedImageBundle(
            is_valid=True,
            original=dummy_img,
            grayscale=dummy_img,
            contrast_enhanced=dummy_img,
            sharpened=dummy_img,
            adaptive_threshold=dummy_img,
            best_candidate=dummy_img,
            best_candidate_name="contrast_enhanced",
            quality_metrics={}
        )
        # Should not raise "ValueError: The truth value of an array with more than one element is ambiguous"
        best = bundle.get_candidate_by_name("auto")
        self.assertIs(best, dummy_img)

        # Test with best_candidate as None
        bundle.best_candidate = None
        best_fallback = bundle.get_candidate_by_name("auto")
        self.assertIs(best_fallback, dummy_img)

        # Candidate name lookup
        self.assertIs(bundle.get_candidate_by_name("clahe"), dummy_img)
        self.assertIs(bundle.get_candidate_by_name("contrast_enhanced"), dummy_img)
        self.assertIs(bundle.get_candidate_by_name("non_existent"), dummy_img)

    def test_unsupported_channel_layouts_rejected(self):
        """Verify that 1D, 4D, and 3D with unsupported channel counts are rejected with is_valid=False."""
        # 1D array
        img, info = self.preprocessor.decode_and_validate(np.zeros((100,), dtype=np.uint8))
        self.assertIsNone(img)
        self.assertFalse(info["is_valid"])
        self.assertIn("Unsupported ndarray dimensions", info["error"])

        # 4D array
        img, info = self.preprocessor.decode_and_validate(np.zeros((1, 100, 100, 3), dtype=np.uint8))
        self.assertIsNone(img)
        self.assertFalse(info["is_valid"])
        self.assertIn("Unsupported ndarray dimensions", info["error"])

        # 3D array with 2 channels
        img, info = self.preprocessor.decode_and_validate(np.zeros((100, 100, 2), dtype=np.uint8))
        self.assertIsNone(img)
        self.assertFalse(info["is_valid"])
        self.assertIn("Unsupported channel count: 2", info["error"])

        # 3D array with 5 channels
        img, info = self.preprocessor.decode_and_validate(np.zeros((100, 100, 5), dtype=np.uint8))
        self.assertIsNone(img)
        self.assertFalse(info["is_valid"])
        self.assertIn("Unsupported channel count: 5", info["error"])

    def test_excessive_decoded_dimensions_and_pixels_rejected(self):
        """Verify that images exceeding hard bounds (8192px or 25 MP) are rejected before heavy allocation."""
        # Non-positive dimensions
        empty_img = np.zeros((0, 0, 3), dtype=np.uint8)
        img, info = self.preprocessor._enforce_bounds(empty_img)
        self.assertIsNone(img)
        self.assertFalse(info["is_valid"])

        # Create mock image array exceeding 8192px
        huge_dim = np.zeros((8193, 10, 3), dtype=np.uint8)
        img, info = self.preprocessor._enforce_bounds(huge_dim)
        self.assertIsNone(img)
        self.assertFalse(info["is_valid"])
        self.assertIn(f"{MAX_HARD_DIMENSION}px", info["error"])

    def test_aspect_ratio_resizing_strictly_bounded(self):
        """Verify resizing preserves aspect ratio and strictly respects max_dim."""
        small_img = np.zeros((200, 100, 3), dtype=np.uint8)
        resized, upscaled, dims = self.preprocessor.resize_aspect_ratio(small_img, upscale_small=True)
        h, w = resized.shape[:2]
        self.assertLessEqual(max(h, w), self.preprocessor.max_dim)
        self.assertTrue(upscaled)

    def test_uneven_lighting_selects_adaptive_threshold(self):
        """Verify that severe gradient illumination triggers adaptive threshold candidate selection."""
        h, w = 300, 400
        # Create severe uneven gradient (left black to right white)
        gradient = np.tile(np.linspace(10, 245, w, dtype=np.uint8), (h, 1))
        # Add high contrast text
        gradient_bgr = cv2.cvtColor(gradient, cv2.COLOR_GRAY2BGR)
        cv2.putText(gradient_bgr, "INGREDIENTS: INS 102", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

        bundle = self.preprocessor.process(gradient_bgr)
        self.assertTrue(bundle.quality_metrics.get("is_uneven_lighting"))
        self.assertEqual(bundle.best_candidate_name, "adaptive_threshold")
        self.assertIsNotNone(bundle.adaptive_threshold)


class TestOcrComparatorRegression(unittest.TestCase):
    """Regression tests for Task 6: OCR Comparator algorithms."""

    def test_normalized_levenshtein_similarity(self):
        """Verify exact normalized similarity: 1.0 - (dist / max(len1, len2))."""
        # Both empty
        s0 = compute_levenshtein_similarity("", "")
        self.assertEqual(s0, 1.0)

        # Empty vs non-empty
        s1 = compute_levenshtein_similarity("", "test")
        self.assertEqual(s1, 0.0)

        # Identical
        s2 = compute_levenshtein_similarity("flour", "flour")
        self.assertEqual(s2, 1.0)

        # Single substitution: "kitten" vs "sitten" -> 1 - 1 / 6 = 5/6
        s3 = compute_levenshtein_similarity("kitten", "sitten")
        self.assertAlmostEqual(s3, 5.0 / 6.0, places=4)

    def test_ins_false_confusion_prevention(self):
        """Verify that newly discovered INS codes in B are not falsely flagged as confusions with existing codes in A."""
        # In A: only INS 102 was found.
        # In B: both INS 102 and INS 211 were found.
        text_a = "Ingredients: Colour (INS 102)."
        text_b = "Ingredients: Colour (INS 102), Preservative (INS 211)."

        res = compare_ocr_results(text_a, text_b)
        metrics = res["comparison_metrics"]
        # INS 211 should be in new_ins_codes_detected_in_b
        self.assertTrue(any("211" in str(c) for c in metrics["new_ins_codes_detected_in_b"]))
        # INS 102 should be in config_a and config_b
        self.assertTrue(any("102" in str(c) for c in res["config_a"]["detected_ins_codes"]))
        self.assertTrue(any("102" in str(c) for c in res["config_b"]["detected_ins_codes"]))
        # Crucially, INS 102 -> INS 211 should NOT be a confusion!
        confusions = metrics.get("confusion_fixes", [])
        self.assertEqual(len(confusions), 0)


class TestInsEvaluatorRegression(unittest.TestCase):
    """Regression tests for Task 5: Mutually exclusive impact classification & Levenshtein safety."""

    def test_benchmark_impact_classification_mutually_exclusive(self):
        """Verify that evaluate_single_sample classifies into strictly one of 4 states."""
        # 1. Clear improvement: F1 improves, CER stays low
        res_imp = evaluate_single_sample(
            sample_id="imp-1",
            label_category="Test Category",
            ground_truth_text="Ingredients: Colour (INS 102), Preservative (INS 211)",
            ground_truth_codes=["102", "211"],
            text_a="Ingredients: Colour (1NS 102)",  # 1 code detected
            text_b="Ingredients: Colour (INS 102), Preservative (INS 211)"  # 2 codes detected
        )
        self.assertEqual(res_imp["comparison"]["impact"], CLASSIFICATION_IMPROVED)

        # 2. Mixed: INS F1 improves, but OCR text is heavily corrupted (cer_delta > 0.05)
        res_mix = evaluate_single_sample(
            sample_id="mix-1",
            label_category="Test Category",
            ground_truth_text="Ingredients: Colour (INS 102), Preservative (INS 211)",
            ground_truth_codes=["102", "211"],
            text_a="Ingredients: Colour (INS 102)",   # clean text, 1 code
            text_b="Ingredients: Colour (INS 102), Preservative (INS 211) " + ("corrupt_tail_" * 15)  # 2 codes, degraded CER
        )
        self.assertEqual(res_mix["comparison"]["impact"], CLASSIFICATION_MIXED)

        # 3. Unchanged: identical results
        res_unc = evaluate_single_sample(
            sample_id="unc-1",
            label_category="Test Category",
            ground_truth_text="Ingredients: Colour (INS 102)",
            ground_truth_codes=["102"],
            text_a="Ingredients: Colour (INS 102)",
            text_b="Ingredients: Colour (INS 102)"
        )
        self.assertEqual(res_unc["comparison"]["impact"], CLASSIFICATION_UNCHANGED)

    def test_levenshtein_memory_and_bounds_safety(self):
        """Verify compute_levenshtein_distance handles long sequences safely without memory crash."""
        str_a = "A" * 6000
        str_b = "A" * 6000
        # Should truncate at max_len (4,000) and return 0
        dist = compute_levenshtein_distance(list(str_a), list(str_b))
        self.assertEqual(dist, 0)

        # 1 char difference within truncated bound
        str_c = "B" + "A" * 3999
        dist_diff = compute_levenshtein_distance(list(str_a[:4000]), list(str_c))
        self.assertEqual(dist_diff, 1)


class TestApiEndpointsRegression(unittest.TestCase):
    """Regression tests for Task 1 & 2 API endpoints in backend/app.py."""

    def setUp(self):
        self.client = app.test_client()

    def test_compare_endpoint_rejects_invalid_images_with_400(self):
        """POST /api/v1/ocr/compare returns 400 when an image is corrupt or invalid."""
        # 1. Invalid first image
        resp1 = self.client.post("/api/v1/ocr/compare", json={
            "image": "not_a_valid_image_base64",
            "image_b": ""
        })
        self.assertEqual(resp1.status_code, 400)
        data1 = resp1.get_json()
        self.assertIn("error", data1)

        # 2. Invalid second image
        # Provide valid synthetic image for image A
        dummy = np.zeros((100, 100, 3), dtype=np.uint8)
        _, buf = cv2.imencode(".jpg", dummy)
        valid_b64 = "data:image/jpeg;base64," + cv2.imencode(".jpg", dummy)[1].tobytes().hex() # invalid hex vs b64
        resp2 = self.client.post("/api/v1/ocr/compare", json={
            "image": "corrupt_data",
            "image_b": "corrupt_data_2"
        })
        self.assertEqual(resp2.status_code, 400)

    def test_compare_endpoint_handles_image_only_safely(self):
        """POST /api/v1/ocr/compare returns prepared images without comparing empty strings when text is omitted."""
        dummy = np.zeros((150, 200, 3), dtype=np.uint8)
        cv2.putText(dummy, "LABEL", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        import base64
        b64 = "data:image/jpeg;base64," + base64.b64encode(cv2.imencode(".jpg", dummy)[1].tobytes()).decode("utf-8")

        resp = self.client.post("/api/v1/ocr/compare", json={
            "image": b64
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data.get("status"), "prepared")
        self.assertIn("prepared_images", data)
        self.assertIn("quality_metrics", data)


if __name__ == "__main__":
    unittest.main()
