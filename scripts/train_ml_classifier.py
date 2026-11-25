"""
Stand-Alone Training, Cross-Validation & Benchmark Script
=========================================================
Project: Food Label Verification System
Module: TF-IDF Vectorizer + Multinomial Logistic Regression Ingredient Classifier

Usage:
    python scripts/train_ml_classifier.py [--save] [--evaluate]

Generates:
    - Trained pickled model: backend/data/ml_classifier.pkl
    - Detailed evaluation JSON: backend/data/ml_evaluation_results.json
"""

import os
import sys
import json
import pickle
import argparse
import numpy as np

# Ensure backend directory is in python search path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

TAXONOMY_PATH = os.path.join(BASE_DIR, "backend", "data", "ins_taxonomy.json")
MODEL_OUT_PATH = os.path.join(BASE_DIR, "backend", "data", "ml_classifier.pkl")
EVAL_OUT_PATH = os.path.join(BASE_DIR, "backend", "data", "ml_evaluation_results.json")

STANDARD_CLASSES = [
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


def load_dataset():
    if not os.path.exists(TAXONOMY_PATH):
        raise FileNotFoundError(f"Taxonomy file not found at {TAXONOMY_PATH}")

    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)

    texts, labels = [], []
    for code, entry in taxonomy.items():
        name = entry.get("name", "")
        alts = " ".join(entry.get("alternative_names", []))
        desc = entry.get("description", "")
        text = f"{name} {alts} {desc}".strip()
        if not text:
            continue

        assigned = None
        for fc in entry.get("functional_categories", []):
            if fc in STANDARD_CLASSES and fc != "Other":
                assigned = fc
                break
        if not assigned:
            cls_name = entry.get("class", "")
            if cls_name in STANDARD_CLASSES and cls_name != "Other":
                assigned = cls_name
            else:
                assigned = "Other"

        texts.append(text)
        labels.append(assigned)

    return np.array(texts), np.array(labels)


def train_and_evaluate(save_model=True, save_eval=True):
    print("=" * 70)
    print("FOOD LABEL VERIFICATION SYSTEM — ML INGREDIENT CLASSIFIER TRAINING")
    print("=" * 70)

    texts, labels = load_dataset()
    classes_sorted = sorted(list(set(labels)))
    print(f"[*] Loaded {len(texts)} samples across {len(classes_sorted)} functional classes.")

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

    print("[*] Running 5-Fold Stratified Cross-Validation...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    y_true, y_pred = [], []
    fold_records = []

    for fold_num, (train_idx, test_idx) in enumerate(skf.split(texts, labels), 1):
        pipe.fit(texts[train_idx], labels[train_idx])
        fold_preds = pipe.predict(texts[test_idx])
        acc = accuracy_score(labels[test_idx], fold_preds)
        fold_records.append({"fold": fold_num, "accuracy": round(acc, 4)})
        y_true.extend(labels[test_idx])
        y_pred.extend(fold_preds)
        print(f"    - Fold {fold_num}: Accuracy = {acc * 100:.2f}%")

    overall_acc = accuracy_score(y_true, y_pred)
    macro_prec = precision_score(y_true, y_pred, average="macro")
    macro_rec = recall_score(y_true, y_pred, average="macro")
    macro_f1 = f1_score(y_true, y_pred, average="macro")
    weighted_f1 = f1_score(y_true, y_pred, average="weighted")

    print("\n" + "=" * 70)
    print("CROSS-VALIDATION BENCHMARK RESULTS")
    print("=" * 70)
    print(f"Overall Accuracy:  {overall_acc * 100:.2f}%")
    print(f"Macro Precision:   {macro_prec * 100:.2f}%")
    print(f"Macro Recall:      {macro_rec * 100:.2f}%")
    print(f"Macro F1-Score:    {macro_f1 * 100:.2f}%")
    print(f"Weighted F1-Score: {weighted_f1 * 100:.2f}%")
    print("=" * 70)
    print("\nDetailed Classification Report:")
    print(classification_report(y_true, y_pred, digits=4))

    # Fit final pipeline on 100% of dataset
    print("[*] Fitting final model on complete dataset...")
    pipe.fit(texts, labels)

    eval_data = {
        "dataset_size": len(texts),
        "num_classes": len(classes_sorted),
        "classes": classes_sorted,
        "overall_accuracy": round(overall_acc, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "k_fold_scores": fold_records,
        "classification_report": classification_report(y_true, y_pred, digits=4, output_dict=True),
        "confusion_matrix": {
            "classes": classes_sorted,
            "matrix": confusion_matrix(y_true, y_pred, labels=classes_sorted).tolist()
        }
    }

    if save_model:
        os.makedirs(os.path.dirname(MODEL_OUT_PATH), exist_ok=True)
        with open(MODEL_OUT_PATH, "wb") as f:
            pickle.dump({
                "pipeline": pipe,
                "classes": list(pipe.named_steps["clf"].classes_),
                "metrics": eval_data
            }, f)
        print(f"[✓] Saved model artifact to: {MODEL_OUT_PATH}")

    if save_eval:
        os.makedirs(os.path.dirname(EVAL_OUT_PATH), exist_ok=True)
        with open(EVAL_OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(eval_data, f, indent=2)
        print(f"[✓] Saved evaluation metrics to: {EVAL_OUT_PATH}")

    return eval_data


if __name__ == "__main__":
    train_and_evaluate()
