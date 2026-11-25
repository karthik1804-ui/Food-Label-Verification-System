"""
Module: OCR Comparison Engine (Configuration A vs. Configuration B)
===================================================================
Provides structured comparative analysis between:
  - Configuration A (Standard / Raw Tesseract)
  - Configuration B (Improved / OpenCV Preprocessed + Tesseract)

Evaluates:
  - Text differences and character-level edit distance
  - Word counts and tokenization variations
  - Word-level confidence comparisons (with explicit caveats)
  - Preprocessing and OCR execution timings
  - Downstream INS additive extraction differential (precision/recall impact)
  - Specific character confusion patterns (e.g. 1NS -> INS, 1O2 -> 102, 62I -> 621)
"""

import time
import logging
import re
from typing import Dict, Any, List, Optional
import difflib

from services.parser import parse_additives_detailed
from services.ocr.ins_evaluator import compute_levenshtein_distance

logger = logging.getLogger(__name__)

# Known OCR character substitutions in food ingredient contexts
KNOWN_CONFUSION_PATTERNS = [
    ("1NS", "INS"),
    ("1N5", "INS"),
    ("IN5", "INS"),
    ("1O2", "102"),
    ("11O", "110"),
    ("62I", "621"),
    ("62l", "621"),
    ("63I", "635"),
    ("E-", "E"),
    ("E ", "E")
]


def compute_levenshtein_similarity(s1: str, s2: str) -> float:
    """
    Computes exact normalized Levenshtein similarity (0.0 to 1.0) based on
    character edit distance normalized by maximum input length:
        Similarity = 1.0 - (LevenshteinDistance / max(len(s1), len(s2)))
    Handles empty strings safely and returns 1.0 for two empty strings.
    """
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    dist = compute_levenshtein_distance(list(s1), list(s2))
    return round(max(0.0, 1.0 - (dist / max_len)), 4)


def detect_character_confusion_fixes(text_a: str, text_b: str) -> List[Dict[str, str]]:
    """
    Identifies known OCR confusions that were corrected between text_a and text_b
    using aligned replacement spans.
    Prevents false positives where a token was deleted or appears elsewhere in the text.
    """
    fixes = []
    if not text_a or not text_b:
        return fixes

    # 1. Character-level aligned replacement spans
    matcher = difflib.SequenceMatcher(None, text_a.upper(), text_b.upper())
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace":
            span_a = text_a.upper()[i1:i2]
            span_b = text_b.upper()[j1:j2]
            for bad_token, good_token in KNOWN_CONFUSION_PATTERNS:
                if bad_token in span_a and good_token in span_b and bad_token not in span_b:
                    fix_record = {
                        "erroneous_token_in_a": bad_token,
                        "corrected_token_in_b": good_token,
                        "aligned_span_a": text_a[i1:i2],
                        "aligned_span_b": text_b[j1:j2],
                        "note": f"Character confusion corrected: '{bad_token}' in Config A resolved to '{good_token}' in Config B"
                    }
                    if not any(f["erroneous_token_in_a"] == bad_token and f["corrected_token_in_b"] == good_token for f in fixes):
                        fixes.append(fix_record)

    # 2. Token-level aligned word substitutions
    tokens_a = re.findall(r"\b[A-Za-z0-9\-:]+\b", text_a.upper())
    tokens_b = re.findall(r"\b[A-Za-z0-9\-:]+\b", text_b.upper())
    token_matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)
    for tag, i1, i2, j1, j2 in token_matcher.get_opcodes():
        if tag == "replace":
            sub_a = tokens_a[i1:i2]
            sub_b = tokens_b[j1:j2]
            for t_a in sub_a:
                for t_b in sub_b:
                    for bad_token, good_token in KNOWN_CONFUSION_PATTERNS:
                        if bad_token in t_a and good_token in t_b and bad_token not in t_b:
                            fix_record = {
                                "erroneous_token_in_a": bad_token,
                                "corrected_token_in_b": good_token,
                                "aligned_span_a": t_a,
                                "aligned_span_b": t_b,
                                "note": f"Character confusion corrected: '{bad_token}' in Config A resolved to '{good_token}' in Config B"
                            }
                            if not any(f["erroneous_token_in_a"] == bad_token and f["corrected_token_in_b"] == good_token for f in fixes):
                                fixes.append(fix_record)

    return fixes


def compare_ocr_results(
    text_a: str,
    text_b: str,
    confidence_a: Optional[float] = None,
    confidence_b: Optional[float] = None,
    timings_a: Optional[Dict[str, float]] = None,
    timings_b: Optional[Dict[str, float]] = None,
    quality_metrics: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Performs comprehensive structured comparison between Configuration A and Configuration B.
    Does NOT automatically merge outputs.
    Does NOT treat higher Tesseract confidence as proof of higher accuracy.
    """
    clean_a = (text_a or "").strip()
    clean_b = (text_b or "").strip()

    words_a = clean_a.split()
    words_b = clean_b.split()
    word_count_a = len(words_a)
    word_count_b = len(words_b)

    conf_a = round(float(confidence_a), 3) if confidence_a is not None else 1.0
    conf_b = round(float(confidence_b), 3) if confidence_b is not None else 1.0
    confidence_delta = round(conf_b - conf_a, 3)

    # Downstream INS parsing impact comparison
    parsed_a = parse_additives_detailed(clean_a, ocr_confidence=conf_a) if clean_a else {"parsed_additives": []}
    parsed_b = parse_additives_detailed(clean_b, ocr_confidence=conf_b) if clean_b else {"parsed_additives": []}

    additives_a = parsed_a.get("parsed_additives", [])
    additives_b = parsed_b.get("parsed_additives", [])

    all_codes_a = [str(a.get("code")) for a in additives_a if a.get("code")]
    all_codes_b = [str(b.get("code")) for b in additives_b if b.get("code")]

    # Code occurrence frequencies to accurately track repeated additives
    counts_a = {c: all_codes_a.count(c) for c in set(all_codes_a)}
    counts_b = {c: all_codes_b.count(c) for c in set(all_codes_b)}

    codes_a = sorted(list(counts_a.keys()))
    codes_b = sorted(list(counts_b.keys()))

    new_codes_in_b = [c for c in codes_b if c not in codes_a]
    lost_codes_in_b = [c for c in codes_a if c not in codes_b]

    # Additional occurrences of repeated codes (e.g., code appeared 1x in A, but 2x in B)
    repeated_codes_added_in_b = [
        c for c, count in counts_b.items() if count > counts_a.get(c, 0) and c in codes_a
    ]

    # Character confusion and similarity analysis
    similarity = compute_levenshtein_similarity(clean_a, clean_b)
    confusion_fixes = detect_character_confusion_fixes(clean_a, clean_b)

    return {
        "status": "success",
        "config_a": {
            "name": "Configuration A (Standard / Raw Tesseract)",
            "text": clean_a,
            "confidence": conf_a,
            "word_count": word_count_a,
            "char_count": len(clean_a),
            "parsed_additives_count": len(additives_a),
            "detected_ins_codes": codes_a,
            "ins_code_counts": counts_a,
            "timings_ms": timings_a or {}
        },
        "config_b": {
            "name": "Configuration B (Improved / OpenCV Preprocessed + Tesseract)",
            "text": clean_b,
            "confidence": conf_b,
            "word_count": word_count_b,
            "char_count": len(clean_b),
            "parsed_additives_count": len(additives_b),
            "detected_ins_codes": codes_b,
            "ins_code_counts": counts_b,
            "timings_ms": timings_b or {}
        },
        "comparison_metrics": {
            "similarity_ratio": similarity,
            "word_count_delta": word_count_b - word_count_a,
            "confidence_delta": confidence_delta,
            "new_ins_codes_detected_in_b": new_codes_in_b,
            "lost_ins_codes_in_b": lost_codes_in_b,
            "repeated_codes_added_in_b": repeated_codes_added_in_b,
            "confusion_fixes": confusion_fixes,
            "character_confusion_count": len(confusion_fixes),
            "quality_metrics": quality_metrics or {}
        },
        "evaluation_notes": [
            "Higher Tesseract confidence does not inherently prove higher semantic accuracy.",
            "Inspect physical label ground truth to confirm newly detected additive codes.",
            "Configuration B isolates small fonts and equalizes curved packaging glare via CLAHE."
        ]
    }
