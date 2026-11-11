"""
Module 3: Actionable Counterfactual Engine (Addressing Research Gap G2)
Implements counterfactual optimization:
Simulates feature interventions (e.g., removing or replacing high-risk additives)
to guide manufacturers and consumers on actionable pathways to elevate food safety.
"""

import copy
import logging
from typing import Dict, List, Any, Optional
from services.scoring_engine import compute_safety_score_and_attributions

logger = logging.getLogger(__name__)


def generate_counterfactual_explanation(
    parsed_additives: List[Dict[str, Any]],
    nutriments: Dict[str, Any],
    current_score: float,
    score_deductions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates actionable counterfactual modifications if current safety score < 75.
    Identifies the single highest-impact negative SHAP feature and simulates its removal/mitigation.
    Returns:
      {
        "target_score": 81.0,
        "recommended_action": "Remove INS 250 (Sodium Nitrite)",
        "potential_score_gain": "+18.5 points"
      }
    """
    # If already high safety (>= 75), no urgent intervention needed
    if current_score >= 75.0 or not score_deductions:
        return {
            "target_score": current_score,
            "recommended_action": "Product meets consumer safety threshold (>=75). Formulation is satisfactory.",
            "potential_score_gain": "+0.0 points"
        }

    # Sort deductions by most negative penalty first
    sorted_deductions = sorted(score_deductions, key=lambda d: float(d.get("points_deducted", 0.0)))
    top_negative = sorted_deductions[0]

    feature_type = top_negative.get("type", "additive")
    feature_label = top_negative.get("feature", "Selected Additive")
    feature_code = top_negative.get("code")
    penalty_pts = abs(float(top_negative.get("points_deducted", 0.0)))

    if feature_type == "additive" and feature_code:
        # Simulate counterfactual: Remove this additive from formulation
        simulated_additives = [
            a for a in parsed_additives
            if str(a.get("code", "")).upper() != str(feature_code).upper()
        ]

        # Re-run scoring engine on modified formulation
        res = compute_safety_score_and_attributions(simulated_additives, nutriments)
        new_score = res["final_score"]
        score_gain = round(new_score - current_score, 1)

        # Check for recommended substitute
        substitute_hint = ""
        for a in parsed_additives:
            if str(a.get("code", "")).upper() == str(feature_code).upper():
                sub = a.get("common_substitute")
                if sub:
                    substitute_hint = f" (or replace with {sub})"
                break

        return {
            "target_score": new_score,
            "recommended_action": f"Remove {feature_label}{substitute_hint}",
            "potential_score_gain": f"+{score_gain:.1f} points"
        }

    elif feature_type == "nutrient":
        # Simulate reducing nutrient to WHO safe baseline
        simulated_nutriments = copy.deepcopy(nutriments)
        if feature_code == "SODIUM":
            simulated_nutriments["sodium_100g"] = 0.35  # Below 0.4g threshold
            action_desc = "Reformulate recipe to reduce sodium below 0.4g/100g"
        elif feature_code == "SUGAR":
            simulated_nutriments["sugars_100g"] = 8.0  # Below 10g threshold
            action_desc = "Reduce added sugars below 10g/100g threshold"
        else:
            simulated_nutriments["saturated_fat_100g"] = 3.0  # Below 4g threshold
            action_desc = "Substitute healthy unsaturated oils to lower saturated fat below 4g/100g"

        res = compute_safety_score_and_attributions(parsed_additives, simulated_nutriments)
        new_score = res["final_score"]
        score_gain = round(new_score - current_score, 1)

        return {
            "target_score": new_score,
            "recommended_action": action_desc,
            "potential_score_gain": f"+{score_gain:.1f} points"
        }

    # Fallback
    target = round(min(100.0, current_score + penalty_pts), 1)
    return {
        "target_score": target,
        "recommended_action": f"Mitigate {feature_label}",
        "potential_score_gain": f"+{penalty_pts:.1f} points"
    }
