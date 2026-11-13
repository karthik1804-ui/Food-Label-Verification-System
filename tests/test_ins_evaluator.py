"""
Unit Tests for INS Detection Accuracy & OCR Quality Evaluation Engine
=====================================================================
Validates CER, WER, Precision, Recall, F1 calculations, and benchmark execution.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

from services.ocr.ins_evaluator import (
    compute_cer,
    compute_wer,
    compute_detection_prf1,
    evaluate_single_sample,
    run_benchmark_suite,
    BENCHMARK_SAMPLES
)
from app import app


class TestInsEvaluator(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_cer_computation(self):
        """CER should accurately reflect character-level edit distance ratio."""
        # Exact match -> 0.0
        self.assertEqual(compute_cer("INS 102", "INS 102"), 0.0)

        # 1 substitution out of 7 characters -> 1/7 ~= 0.1429
        self.assertAlmostEqual(compute_cer("INS 102", "1NS 102"), 0.1429, places=3)

        # Empty hypothesis -> 1.0
        self.assertEqual(compute_cer("Tartrazine", ""), 1.0)

    def test_wer_computation(self):
        """WER should accurately reflect word-level edit distance ratio."""
        ref = "Acidity Regulator INS 330 Preservative"
        hyp = "Acidity Regulator 1NS 330 Preservative"
        # 1 word different out of 5 words = 0.20
        self.assertEqual(compute_wer(ref, hyp), 0.2)

        # Identical words
        self.assertEqual(compute_wer("Clean Label Only", "Clean Label Only"), 0.0)

    def test_detection_prf1_calculation(self):
        """Validates TP, FP, FN, Precision, Recall, and F1 score."""
        gt_codes = ["102", "211", "330"]

        # Perfect detection
        det_perfect = ["INS 102", "INS 211", "INS 330"]
        res = compute_detection_prf1(gt_codes, det_perfect)
        self.assertEqual(res["tp_count"], 3)
        self.assertEqual(res["fp_count"], 0)
        self.assertEqual(res["fn_count"], 0)
        self.assertEqual(res["precision"], 1.0)
        self.assertEqual(res["recall"], 1.0)
        self.assertEqual(res["f1_score"], 1.0)

        # 1 missed (FN), 1 hallucinated/extra (FP)
        det_partial = ["INS 102", "INS 211", "INS 621"]
        res2 = compute_detection_prf1(gt_codes, det_partial)
        self.assertEqual(res2["tp_count"], 2)  # 102, 211
        self.assertEqual(res2["fp_count"], 1)  # 621
        self.assertEqual(res2["fn_count"], 1)  # 330
        self.assertAlmostEqual(res2["precision"], 2 / 3, places=3)
        self.assertAlmostEqual(res2["recall"], 2 / 3, places=3)
        self.assertAlmostEqual(res2["f1_score"], 2 / 3, places=3)

    def test_evaluate_single_sample(self):
        """Evaluates a single sample and tags impact appropriately."""
        res = evaluate_single_sample(
            sample_id="SAMPLE-TEST",
            label_category="Test Label",
            ground_truth_text="Ingredients: Sugar, Salt, Tartrazine (INS 102), Citric Acid (INS 330).",
            ground_truth_codes=["102", "330"],
            text_a="Ingredients: Sugar, Salt, Preservative.",  # missed additives due to contrast loss
            text_b="Ingredients: Sugar, Salt, Tartrazine (INS 102), Citric Acid (INS 330)."  # all additives captured
        )

        self.assertEqual(res["comparison"]["impact"], "IMPROVED")
        self.assertGreater(res["config_b"]["metrics"]["f1_score"], res["config_a"]["metrics"]["f1_score"])
        self.assertLess(res["config_b"]["cer"], res["config_a"]["cer"])

    def test_run_benchmark_suite(self):
        """Executes full benchmark suite across all predefined samples."""
        summary = run_benchmark_suite()

        self.assertEqual(summary["status"], "success")
        bench = summary["benchmark_summary"]

        self.assertEqual(bench["total_samples"], len(BENCHMARK_SAMPLES))
        self.assertGreater(bench["improved_samples"], 0)
        self.assertEqual(bench["degraded_samples"], 0)

        # Config B should show higher F1 score and lower CER
        self.assertGreater(bench["config_b_ins_metrics"]["f1_score"], bench["config_a_ins_metrics"]["f1_score"])
        self.assertLess(bench["mean_cer_config_b"], bench["mean_cer_config_a"])
        self.assertLess(bench["mean_wer_config_b"], bench["mean_wer_config_a"])

    def test_api_ocr_benchmark_endpoint(self):
        """GET /api/v1/ocr/benchmark returns 200 and benchmark summary JSON."""
        res = self.client.get("/api/v1/ocr/benchmark")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("benchmark_summary", data)
        self.assertIn("samples", data)

    def test_api_ocr_evaluate_endpoint(self):
        """POST /api/v1/ocr/evaluate evaluates custom ground truth comparison."""
        payload = {
            "sample_id": "TEST-EVAL-01",
            "label_category": "Test Evaluation Label",
            "ground_truth_text": "Ingredients: Sugar, Salt, Tartrazine INS 102, Citric Acid INS 330.",
            "ground_truth_codes": ["102", "330"],
            "text_a": "Ingredients: Sugar, Salt, Preservative.",
            "text_b": "Ingredients: Sugar, Salt, Tartrazine INS 102, Citric Acid INS 330.",
            "confidence_a": 0.70,
            "confidence_b": 0.92
        }
        res = self.client.post("/api/v1/ocr/evaluate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        eval_data = data["evaluation"]
        self.assertEqual(eval_data["comparison"]["impact"], "IMPROVED")
        self.assertEqual(eval_data["config_b"]["metrics"]["f1_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
