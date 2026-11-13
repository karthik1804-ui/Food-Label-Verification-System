"""
CLI Benchmark Runner: INS Detection Accuracy & OCR Preprocessing Evaluation
==========================================================================
Executes reproducible evaluations comparing Configuration A and Configuration B
across standard food packaging label datasets.

Usage:
  python scripts/evaluate_ocr_ins.py [--json]
"""

import os
import sys
import json
import argparse

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

from services.ocr.ins_evaluator import run_benchmark_suite


def main():
    parser = argparse.ArgumentParser(description="Evaluate INS Detection Accuracy (Config A vs Config B)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON summary")
    args = parser.parse_args()

    results = run_benchmark_suite()

    if args.json:
        print(json.dumps(results, indent=2))
        return

    summary = results["benchmark_summary"]
    samples = results["samples"]

    print("=" * 80)
    print(" FOOD LABEL VERIFICATION SYSTEM - OCR PIPELINE EVALUATION REPORT")
    print(" Configuration A: Raw Tesseract (No OpenCV)")
    print(" Configuration B: OpenCV Preprocessed + Tesseract")
    print("=" * 80)
    print(f"Total Test Samples Evaluated : {summary['total_samples']}")
    print(f"Improved Recognition Samples : {summary['improved_samples']}")
    print(f"Regressed Recognition Samples: {summary.get('regressed_samples', 0)}")
    print(f"Mixed Outcome Samples        : {summary.get('mixed_samples', 0)}")
    print(f"Unchanged Baseline Samples   : {summary.get('unchanged_samples', 0)}")
    print("-" * 80)
    print("ERROR RATE METRICS:")
    print(f"  Configuration A Mean CER : {summary['mean_cer_config_a']:.4f}")
    print(f"  Configuration B Mean CER : {summary['mean_cer_config_b']:.4f}")
    print(f"  CER Relative Reduction   : {summary['cer_relative_reduction_pct']}%")
    print(f"  Configuration A Mean WER : {summary['mean_wer_config_a']:.4f}")
    print(f"  Configuration B Mean WER : {summary['mean_wer_config_b']:.4f}")
    print(f"  WER Relative Reduction   : {summary['wer_relative_reduction_pct']}%")
    print("-" * 80)
    print("INS CODE DETECTION (ACADEMIC PRF1 METRICS):")
    a_m = summary["config_a_ins_metrics"]
    b_m = summary["config_b_ins_metrics"]
    print(f"  Config A -> Precision: {a_m['precision']:.4f} | Recall: {a_m['recall']:.4f} | F1: {a_m['f1_score']:.4f}")
    print(f"  Config B -> Precision: {b_m['precision']:.4f} | Recall: {b_m['recall']:.4f} | F1: {b_m['f1_score']:.4f}")
    print(f"  Absolute F1 Score Gain : +{summary['f1_absolute_gain']:.4f}")
    print("=" * 80)
    print("\nSAMPLE-BY-SAMPLE AUDIT BREAKDOWN:")
    for s in samples:
        print(f"\n[Sample ID: {s['sample_id']}] - {s['label_category']}")
        print(f"  Ground Truth Additive Codes : {s['ground_truth']['codes']}")
        print(f"  Config A Detected Codes     : {s['config_a']['detected_codes']} (CER: {s['config_a']['cer']}, WER: {s['config_a']['wer']})")
        print(f"  Config B Detected Codes     : {s['config_b']['detected_codes']} (CER: {s['config_b']['cer']}, WER: {s['config_b']['wer']})")
        print(f"  Outcome Impact              : {s['comparison']['impact']} (F1 Delta: {s['comparison']['f1_improvement']:+.4f})")
        if s['comparison']['new_correct_codes']:
            print(f"  Newly Recovered Codes (B)   : {s['comparison']['new_correct_codes']}")
    print("=" * 80)


if __name__ == "__main__":
    main()
