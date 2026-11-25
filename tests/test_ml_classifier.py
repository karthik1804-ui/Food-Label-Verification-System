"""
Test Suite: Hybrid Rule-Based + TF-IDF Logistic Regression Ingredient Classification
=====================================================================================
Validates:
  1. TF-IDF vectorizer + Logistic Regression model training and 5-fold cross-validation.
  2. Model inference on canonical chemical terms, synthetic colors, preservatives, and sweeteners.
  3. Feature attribution / explainability extraction (TF-IDF * Logistic Regression weights).
  4. Hybrid decision router: Deterministic rule-based priority for mapped INS codes vs. ML fallback for unmapped tokens.
  5. Integration with parse_additives_detailed and the main /api/v1/analyze pipeline.
  6. Direct REST API endpoints: POST /api/v1/ml/classify and GET /api/v1/ml/benchmark.
"""

import unittest
import json
import os
import sys

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from services.ml_classifier import (
    MLIngredientClassifier,
    get_ml_classifier,
    classify_ingredient_hybrid,
    STANDARD_FUNCTIONAL_CLASSES
)
from services.parser import parse_additives_detailed
import app as flask_app_module


class TestMLClassifier(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.classifier = get_ml_classifier()
        cls.app = flask_app_module.app.test_client()

    def test_01_model_is_trained_and_has_classes(self):
        """Verifies model initialized and trained with standard functional classes."""
        self.assertTrue(self.classifier.is_trained)
        self.assertGreaterEqual(len(self.classifier.classes_), 5)
        for expected in ["Color", "Preservative", "Sweetener", "Acidity regulator"]:
            self.assertIn(expected, self.classifier.classes_)

    def test_02_predict_single_functional_classes(self):
        """Verifies TF-IDF Logistic Regression correctly predicts standard functional categories."""
        test_cases = [
            ("synthetic red dye azo colorant", "Color"),
            ("sodium benzoate chemical preservative antimicrobial", "Preservative"),
            ("aspartame intense zero calorie sweetener", "Sweetener"),
            ("monosodium glutamate umami flavor enhancer", "Flavor enhancer"),
            ("citric acid sour buffering ph regulator", "Acidity regulator"),
        ]
        for text, expected_category in test_cases:
            res = self.classifier.predict_single(text)
            self.assertEqual(
                res["predicted_category"],
                expected_category,
                f"Failed for input '{text}': predicted {res['predicted_category']}, expected {expected_category}"
            )
            self.assertGreater(res["confidence"], 0.30)
            self.assertIn("probabilities", res)
            self.assertIn(expected_category, res["probabilities"])

    def test_03_explainability_attributions(self):
        """Verifies top feature attributions return contributing n-gram tokens and weights."""
        res = self.classifier.predict_single("artificial yellow food dye")
        self.assertEqual(res["predicted_category"], "Color")
        self.assertIn("top_attributions", res)
        self.assertIsInstance(res["top_attributions"], list)
        self.assertGreater(len(res["top_attributions"]), 0)
        top_tokens = [a["token"] for a in res["top_attributions"]]
        # At least one color-indicative token must be present
        self.assertTrue(any(t in ["dye", "yellow", "food", "yellow food"] for t in top_tokens))
        self.assertIsInstance(res["top_attributions"][0]["weight"], float)

    def test_04_hybrid_classification_router(self):
        """Verifies Stage 1 deterministic priority and Stage 2 ML inference fallback."""
        # Case A: Known taxonomy entry -> 100% deterministic rule-based
        tax_entry = {
            "code": "INS 102",
            "name": "Tartrazine",
            "class": "Color",
            "functional_categories": ["Color"]
        }
        hybrid_known = classify_ingredient_hybrid("INS 102", taxonomy_entry=tax_entry)
        self.assertEqual(hybrid_known["source"], "deterministic_taxonomy")
        self.assertEqual(hybrid_known["confidence"], 1.0)
        self.assertFalse(hybrid_known["ml_inferred"])
        self.assertEqual(hybrid_known["category"], "Color")

        # Case B: Unmapped candidate token -> ML statistical inference
        hybrid_unmapped = classify_ingredient_hybrid("potassium sorbate food preservative")
        self.assertEqual(hybrid_unmapped["source"], "ml_tfidf_logistic_regression")
        self.assertTrue(hybrid_unmapped["ml_inferred"])
        self.assertEqual(hybrid_unmapped["category"], "Preservative")
        self.assertGreater(hybrid_unmapped["confidence"], 0.40)

    def test_05_parser_integration_unmapped_triage(self):
        """Verifies parse_additives_detailed automatically runs ML triage on unmapped tokens."""
        text = "Ingredients: Refined wheat flour, water, INS 102, INS 9999_UNKNOWN"
        result = parse_additives_detailed(text)
        self.assertIn("ml_classifications", result)
        self.assertIsInstance(result["ml_classifications"], list)
        self.assertGreaterEqual(len(result["ml_classifications"]), 1)
        unmapped_ml = result["ml_classifications"][0]
        self.assertIn("9999", unmapped_ml["token"])
        self.assertTrue(unmapped_ml["ml_inferred"])

    def test_06_api_ml_classify_endpoint_single_and_batch(self):
        """Verifies POST /api/v1/ml/classify endpoint handles single and batch queries."""
        # Single query
        res_single = self.app.post("/api/v1/ml/classify", json={"text": "aspartame artificial sweetener"})
        self.assertEqual(res_single.status_code, 200)
        data_single = json.loads(res_single.data)
        self.assertEqual(data_single["status"], "success")
        self.assertEqual(data_single["result"]["category"], "Sweetener")

        # Batch query
        res_batch = self.app.post("/api/v1/ml/classify", json={
            "tokens": ["sunset yellow dye", "sodium nitrite cure"]
        })
        self.assertEqual(res_batch.status_code, 200)
        data_batch = json.loads(res_batch.data)
        self.assertEqual(data_batch["status"], "success")
        self.assertEqual(data_batch["total_processed"], 2)
        self.assertEqual(data_batch["results"][0]["category"], "Color")
        self.assertEqual(data_batch["results"][1]["category"], "Preservative")

    def test_07_api_ml_benchmark_endpoint(self):
        """Verifies GET /api/v1/ml/benchmark returns cross-validation metrics."""
        res = self.app.get("/api/v1/ml/benchmark")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        metrics = data["metrics"]
        self.assertTrue(metrics["success"])
        self.assertGreater(metrics["training_samples"], 100)
        self.assertGreater(metrics["mean_cv_accuracy"], 0.70)
        self.assertIsInstance(metrics["cv_scores"], list)
        self.assertEqual(len(metrics["cv_scores"]), 5)

    def test_08_full_analyze_v1_includes_ml_classifications(self):
        """Verifies POST /api/v1/analyze includes ml_classifications in payload response."""
        payload = {
            "text": "Water, vegetable oil, INS 211, INS 9999_UNKNOWN"
        }
        res = self.app.post("/api/v1/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("ml_classifications", data)
        self.assertIsInstance(data["ml_classifications"], list)
        self.assertGreaterEqual(len(data["ml_classifications"]), 1)
        ml_item = data["ml_classifications"][0]
        self.assertTrue(ml_item.get("ml_inferred"))
        self.assertIn("category", ml_item)
        self.assertIn("confidence", ml_item)


if __name__ == "__main__":
    unittest.main()
