"""
Rule-Based Food Safety Indicator Engine
========================================
Computes a Consumer Food Safety Indicator Score (0-100 scale) using a
transparent, rule-based additive penalty system.

IMPORTANT METHODOLOGICAL DISCLAIMER:
-------------------------------------
This is a RULE-BASED INDICATOR, not a machine-learning model.
The per-additive penalty values are derived from relative hazard classifications
(EFSA, FSSAI, Codex Alimentarius) combined with WHO nutrient thresholds.
They are NOT Shapley values computed from a trained predictive model.

Do NOT interpret this score as a medical or scientific health risk assessment.
It is an educational indicator designed to flag additives and nutrients that
regulatory bodies have associated with potential concerns at high consumption levels.

The term "SHAP" has been removed from this module. Previous versions incorrectly
used that terminology for what are effectively weighted rule deductions.

Formula:
  Indicator Score = Base Score (90.0) + Σ(Rule Deductions)
  where each deduction reflects a regulatory concern, not a model prediction.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

BASE_BASELINE_SCORE = 90.0
SCORING_METHOD = "rule_based_indicator"
SCORING_VERSION = "2.0.0"

# Regulatory concern classification for deduction magnitudes.
# Sources: EFSA opinions, FSSAI permitted lists, Codex Alimentarius.
# These are relative concern weights — NOT absolute health risk quantities.
# Each penalty is intentionally conservative and symmetric with the taxonomy hazard_level.
_SPECIFIC_ADDITIVE_PENALTIES = {
    # Nitrites/Nitrates — IARC Group 2A carcinogen potential (processed meat context)
    "INS 250": (-18.5, "INS 250 (Sodium Nitrite)", "IARC Group 2A; EFSA 2017 opinion"),
    "INS 251": (-16.0, "INS 251 (Sodium Nitrate)", "IARC related; associated with nitrite conversion"),
    # Benzoate — hyperactivity concern (EFSA 2009 Southampton study replication)
    "INS 211": (-12.0, "INS 211 (Sodium Benzoate)", "EFSA hyperactivity concern; restricted in some jurisdictions"),
    # Azo dyes — Southampton 6 colorants; EFSA 2008 opinion
    "INS 102": (-9.5,  "INS 102 (Tartrazine)",        "Southampton 6; EFSA ADI 7.5 mg/kg bw/day"),
    "INS 110": (-9.0,  "INS 110 (Sunset Yellow FCF)", "Southampton 6; EFSA reduced ADI"),
    "INS 129": (-10.5, "INS 129 (Allura Red AC)",     "Southampton 6; EFSA concern"),
    # Antioxidants — BHA/BHT IARC 2B (possibly carcinogenic)
    "INS 320": (-11.0, "INS 320 (Butylated Hydroxyanisole BHA)", "IARC Group 2B; some bans"),
    "INS 321": (-11.0, "INS 321 (Butylated Hydroxytoluene BHT)", "Potential endocrine concern"),
    # Sulphite — allergen for asthmatics (EU mandatory declaration)
    "INS 220": (-10.0, "INS 220 (Sulphur Dioxide)", "EU allergen list; asthma trigger"),
    # Caramel IV — 4-methylimidazole concern (California Prop 65)
    "INS 150D": (-8.0, "INS 150d (Caramel IV Sulphite Ammonia)", "4-MEI concern; California Prop 65"),
    # Aspartame — IARC Group 2B (2023 re-classification); disputed
    "INS 951": (-8.5, "INS 951 (Aspartame)", "IARC Group 2B (2023); EFSA ADI maintained"),
    # MSG — generally recognised as safe; mild concern at high doses
    "INS 621": (-7.5, "INS 621 (Monosodium Glutamate)", "EFSA: safe at normal use levels; sensitivity reported"),
}

# Hazard-level fallback penalties for additives not in the specific list above.
# Derived from taxonomy hazard_level and hazard_weight fields.
_HAZARD_LEVEL_MULTIPLIERS = {
    "severe":   -15.0,
    "high":     -12.0,
    "moderate":  -6.0,
    "low":       -2.5,
}


def calculate_grade(score: float) -> str:
    """Maps indicator score to A–E grade scale."""
    if score >= 80.0:
        return "A"
    elif score >= 70.0:
        return "B"
    elif score >= 55.0:
        return "C"
    elif score >= 40.0:
        return "D"
    else:
        return "E"


def compute_rule_based_score(
    parsed_additives: List[Dict[str, Any]],
    nutriments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes the Rule-Based Food Safety Indicator Score.

    Returns a dict with:
      - final_score: float (0.0–100.0)
      - grade: str ('A'–'E')
      - base_baseline_score: float (90.0)
      - score_deductions: list of rule deductions (NOT Shapley values)
      - scoring_method: str ('rule_based_indicator')
      - scoring_disclaimer: str
    """
    base_score = BASE_BASELINE_SCORE
    deductions: List[Dict[str, Any]] = []
    seen_codes: set = set()

    # --- Additive rule deductions ---
    for additive in parsed_additives:
        code = str(additive.get("code", "")).upper().strip()
        name = additive.get("name", code)
        h_level = str(additive.get("hazard_level", "Moderate")).lower()
        h_weight = float(additive.get("hazard_weight", 0.4))

        if code in seen_codes:
            continue
        seen_codes.add(code)

        if code in _SPECIFIC_ADDITIVE_PENALTIES:
            pts, label, rationale = _SPECIFIC_ADDITIVE_PENALTIES[code]
            deductions.append({
                "feature": label,
                "type": "additive",
                "code": code,
                "points_deducted": pts,
                "rationale": rationale,
                "rule_source": "specific_additive_penalty"
            })
        else:
            # Generalised fallback using hazard level + weight
            multiplier = _HAZARD_LEVEL_MULTIPLIERS.get(h_level, -6.0)
            pts = round(multiplier * h_weight, 1)
            deductions.append({
                "feature": f"{code} ({name})",
                "type": "additive",
                "code": code,
                "points_deducted": pts,
                "rationale": f"Hazard level: {h_level.capitalize()}; weight: {h_weight}",
                "rule_source": "hazard_level_fallback"
            })

    # --- Nutrient rule deductions (WHO thresholds) ---
    sugars  = float(nutriments.get("sugars_100g") or 0.0)
    sodium  = float(nutriments.get("sodium_100g") or 0.0)
    sat_fat = float(nutriments.get("saturated_fat_100g") or 0.0)

    # Sodium: WHO recommends <2g salt/day = <0.8g sodium/day;
    # per-serving threshold used: 0.4g sodium/100g
    if sodium > 0.4:
        if 1.0 <= sodium <= 1.4:
            sodium_penalty = -9.0
        else:
            excess = sodium - 0.4
            sodium_penalty = round(-min(18.0, 4.0 + (excess * 6.0)), 1)
        deductions.append({
            "feature": "High Sodium Content",
            "type": "nutrient",
            "code": "SODIUM",
            "points_deducted": sodium_penalty,
            "rationale": f"WHO threshold 0.4g/100g; actual {sodium:.2f}g/100g",
            "rule_source": "who_nutrient_threshold"
        })

    # Sugar: WHO free sugars <10% energy; >10g/100g flag
    if sugars > 10.0:
        excess_sugar = sugars - 10.0
        sugar_penalty = round(-min(15.0, 3.0 + (excess_sugar * 0.5)), 1)
        deductions.append({
            "feature": "High Sugar Content",
            "type": "nutrient",
            "code": "SUGAR",
            "points_deducted": sugar_penalty,
            "rationale": f"WHO free sugar guideline; actual {sugars:.1f}g/100g",
            "rule_source": "who_nutrient_threshold"
        })

    # Saturated fat: >4g/100g (UK traffic light threshold for red)
    if sat_fat > 4.0:
        excess_fat = sat_fat - 4.0
        fat_penalty = round(-min(12.0, 2.5 + (excess_fat * 0.8)), 1)
        deductions.append({
            "feature": "High Saturated Fat",
            "type": "nutrient",
            "code": "SAT_FAT",
            "points_deducted": fat_penalty,
            "rationale": f"UK FSA red threshold 4g/100g; actual {sat_fat:.1f}g/100g",
            "rule_source": "fsa_nutrient_threshold"
        })

    total_deduction = sum(d["points_deducted"] for d in deductions)
    raw_final = base_score + total_deduction
    final_score = round(max(5.0, min(100.0, raw_final)), 1)
    grade = calculate_grade(final_score)

    return {
        "final_score": final_score,
        "grade": grade,
        "base_baseline_score": base_score,
        "score_deductions": deductions,
        "scoring_method": SCORING_METHOD,
        "scoring_version": SCORING_VERSION,
        "scoring_disclaimer": (
            "This is a rule-based indicator score using regulatory concern weights. "
            "It is NOT a machine-learning model output. "
            "Do not interpret as a medical or scientific health risk assessment."
        )
    }


# ---------------------------------------------------------------------------
# Backward-compatibility alias — preserves existing test imports
# ---------------------------------------------------------------------------
def compute_safety_score_and_attributions(
    parsed_additives: List[Dict[str, Any]],
    nutriments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Backward-compatible wrapper for compute_rule_based_score().
    Existing tests and callers continue to work unchanged.
    """
    return compute_rule_based_score(parsed_additives, nutriments)
