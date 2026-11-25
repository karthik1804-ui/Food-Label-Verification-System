"""
Module: Machine Learning Ingredient Classifier & Hybrid Decision Pipeline
===========================================================================
Implements a TF-IDF Vectorizer + Multinomial Logistic Regression pipeline
for food ingredient functional classification and unmapped candidate triage.

Architecture:
  - Vectorization: Sublinear TF-IDF with (1, 2) word n-grams
  - Classifier: Multinomial Logistic Regression (L2 regularization, liblinear/lbfgs)
  - Training Data: Derived from the verified 750-entry INS taxonomy
  - Hybrid Protocol:
      1. Stage 1 (Deterministic Rule-Based / Exact Regex & INS Taxonomy):
         If token/code exists in taxonomy -> 100% deterministic taxonomy classification.
      2. Stage 2 (ML Statistical Inference):
         If token is unmapped or ambiguous -> TF-IDF + Logistic Regression predicts
         functional class (e.g. Color, Preservative, Sweetener, Acidity regulator),
         class probabilities, and top contributing N-gram word weights.
      3. Stage 3 (Confidence Gating & HITL Escalation):
         If ML confidence >= CONFIDENCE_THRESHOLD (0.50 default), classify with flag
         "ml_inferred"; if < threshold, flag for Human-in-the-Loop review.
"""

import os
import re
import json
import logging
import pickle
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

# Standard target functional classes aligned with Codex Alimentarius & FSSAI
STANDARD_FUNCTIONAL_CLASSES = [
    "Color",
    "Preservative",
    "Acidity regulator",
    "Emulsifier",
    "Antioxidant",
    "Flavor enhancer",
    "Sweetener",
    "Anti-caking agent",
    "Thickener",
    "Stabilizer",
    "Other"
]

ML_CONFIDENCE_THRESHOLD = 0.50

TAXONOMY_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "ins_taxonomy.json")
)
MODEL_CACHE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "ml_classifier.pkl")
)


class MLIngredientClassifier:
    """
    TF-IDF Vectorizer + Logistic Regression classifier for food ingredient
    and chemical additive functional class prediction.
    """

    def __init__(self, confidence_threshold: float = ML_CONFIDENCE_THRESHOLD):
        self.confidence_threshold = confidence_threshold
        self.pipeline = None
        self.is_trained = False
        self.classes_ = []
        self._load_or_train()

    def _prepare_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Builds labeled training dataset directly from the authoritative 750-entry INS taxonomy.
        """
        if not os.path.exists(TAXONOMY_PATH):
            logger.warning("Taxonomy file not found at %s. ML training aborted.", TAXONOMY_PATH)
            return [], []

        with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
            taxonomy = json.load(f)

        texts: List[str] = []
        labels: List[str] = []

        for code, entry in taxonomy.items():
            name = entry.get("name", "")
            alts = " ".join(entry.get("alternative_names", []))
            desc = entry.get("description", "")
            # Combine textual cues
            text_rep = f"{name} {alts} {desc}".strip()
            if not text_rep:
                continue

            # Target class resolution
            assigned_class = None
            for fc in entry.get("functional_categories", []):
                if fc in STANDARD_FUNCTIONAL_CLASSES and fc != "Other":
                    assigned_class = fc
                    break
            if not assigned_class:
                primary_class = entry.get("class", "")
                if primary_class in STANDARD_FUNCTIONAL_CLASSES and primary_class != "Other":
                    assigned_class = primary_class
                else:
                    assigned_class = "Other"

            texts.append(text_rep)
            labels.append(assigned_class)

        return texts, labels

    def train(self, save_cache: bool = True) -> Dict[str, Any]:
        """
        Trains TF-IDF vectorizer + Logistic Regression model.
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import Pipeline
            from sklearn.model_selection import StratifiedKFold, cross_val_score
        except ImportError:
            logger.error("scikit-learn is required for MLIngredientClassifier.")
            return {"success": False, "error": "scikit-learn not installed"}

        texts, labels = self._prepare_training_data()
        if not texts or len(texts) < 20:
            return {"success": False, "error": "Insufficient training samples in taxonomy"}

        pipe = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=1500,
                sublinear_tf=True,
                lowercase=True
            )),
            ("clf", LogisticRegression(
                max_iter=1000,
                C=1.0,
                solver="lbfgs",
                random_state=42
            ))
        ])

        # Cross-validation performance check
        cv_scores = []
        try:
            skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            cv_scores = cross_val_score(pipe, texts, labels, cv=skf, scoring="accuracy")
            mean_cv_accuracy = float(np.mean(cv_scores))
        except Exception as e:
            logger.warning("Cross-validation failed: %s", str(e))
            mean_cv_accuracy = 0.0

        pipe.fit(texts, labels)
        self.pipeline = pipe
        self.classes_ = list(pipe.named_steps["clf"].classes_)
        self.is_trained = True

        metrics = {
            "success": True,
            "training_samples": len(texts),
            "num_classes": len(self.classes_),
            "classes": self.classes_,
            "mean_cv_accuracy": round(mean_cv_accuracy, 4),
            "cv_scores": [round(float(s), 4) for s in cv_scores]
        }

        if save_cache:
            try:
                os.makedirs(os.path.dirname(MODEL_CACHE_PATH), exist_ok=True)
                with open(MODEL_CACHE_PATH, "wb") as f:
                    pickle.dump({
                        "pipeline": self.pipeline,
                        "classes": self.classes_,
                        "metrics": metrics
                    }, f)
                logger.info("Saved trained ML model to %s", MODEL_CACHE_PATH)
            except Exception as e:
                logger.warning("Could not persist model cache: %s", str(e))

        return metrics

    def _load_or_train(self) -> None:
        """
        Loads cached model file if present, else trains on taxonomy dataset.
        """
        if os.path.exists(MODEL_CACHE_PATH):
            try:
                with open(MODEL_CACHE_PATH, "rb") as f:
                    data = pickle.load(f)
                    self.pipeline = data.get("pipeline")
                    self.classes_ = data.get("classes", [])
                    self.is_trained = True
                logger.info("Loaded cached ML ingredient model from %s", MODEL_CACHE_PATH)
                return
            except Exception as e:
                logger.warning("Failed to load cached model: %s. Retraining...", str(e))

        self.train(save_cache=True)

    def predict_single(self, text: str) -> Dict[str, Any]:
        """
        Predicts functional category for a single ingredient/additive candidate text.
        Returns:
          - predicted_category: str
          - confidence: float (0.0 to 1.0)
          - probabilities: Dict[str, float]
          - top_attributions: List[Tuple[str, float]] (explainability)
          - is_confident: bool (confidence >= threshold)
        """
        if not self.is_trained or not self.pipeline:
            return {
                "predicted_category": "Other",
                "confidence": 0.0,
                "probabilities": {},
                "top_attributions": [],
                "is_confident": False,
                "error": "Model not trained"
            }

        cleaned = str(text or "").strip()
        if not cleaned:
            return {
                "predicted_category": "Other",
                "confidence": 0.0,
                "probabilities": {},
                "top_attributions": [],
                "is_confident": False
            }

        vec = self.pipeline.named_steps["tfidf"]
        clf = self.pipeline.named_steps["clf"]

        probs = self.pipeline.predict_proba([cleaned])[0]
        pred_idx = int(np.argmax(probs))
        pred_class = self.classes_[pred_idx]
        conf = float(probs[pred_idx])

        # Feature explanation: compute TF-IDF score * class weight for input tokens
        top_attributions: List[Dict[str, Any]] = []
        try:
            vec_test = vec.transform([cleaned])
            feature_names = np.array(vec.get_feature_names_out())
            indices = vec_test.indices
            values = vec_test.data

            if len(self.classes_) == 2:
                coefs = clf.coef_[0] if pred_idx == 1 else -clf.coef_[0]
            else:
                coefs = clf.coef_[pred_idx]

            attributions = []
            for idx, val in zip(indices, values):
                feat_name = feature_names[idx]
                token_contrib = float(val * coefs[idx])
                attributions.append({"token": feat_name, "weight": round(token_contrib, 4)})

            attributions.sort(key=lambda x: x["weight"], reverse=True)
            top_attributions = attributions[:5]
        except Exception as e:
            logger.debug("Feature attribution extraction failed: %s", str(e))

        prob_dict = {
            str(cls_name): round(float(p), 4)
            for cls_name, p in zip(self.classes_, probs)
        }

        return {
            "predicted_category": str(pred_class),
            "confidence": round(conf, 4),
            "probabilities": prob_dict,
            "top_attributions": top_attributions,
            "is_confident": bool(conf >= self.confidence_threshold),
            "scoring_method": "tfidf_logistic_regression"
        }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Batch prediction for multiple texts.
        """
        return [self.predict_single(t) for t in texts]


# Singleton instance
_CLASSIFIER_INSTANCE: Optional[MLIngredientClassifier] = None


def get_ml_classifier() -> MLIngredientClassifier:
    """Returns singleton instance of MLIngredientClassifier."""
    global _CLASSIFIER_INSTANCE
    if _CLASSIFIER_INSTANCE is None:
        _CLASSIFIER_INSTANCE = MLIngredientClassifier()
    return _CLASSIFIER_INSTANCE


def classify_ingredient_hybrid(
    token: str,
    taxonomy_entry: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Hybrid Classification Router:
    1. If taxonomy_entry provided -> 100% Deterministic Rule-Based match.
    2. If unmapped -> Fallback to TF-IDF Logistic Regression ML inference.
    """
    if taxonomy_entry:
        cats = taxonomy_entry.get("functional_categories") or [taxonomy_entry.get("class", "Food Additive")]
        primary = cats[0] if cats else "Food Additive"
        return {
            "token": token,
            "source": "deterministic_taxonomy",
            "category": primary,
            "functional_categories": cats,
            "confidence": 1.0,
            "ml_inferred": False,
            "top_attributions": []
        }

    # Fallback to ML
    classifier = get_ml_classifier()
    ml_res = classifier.predict_single(token)

    return {
        "token": str(token),
        "source": "ml_tfidf_logistic_regression",
        "category": str(ml_res["predicted_category"]),
        "functional_categories": [str(ml_res["predicted_category"])],
        "confidence": float(ml_res["confidence"]),
        "ml_inferred": True,
        "is_confident": bool(ml_res["is_confident"]),
        "probabilities": ml_res["probabilities"],
        "top_attributions": ml_res["top_attributions"]
    }
