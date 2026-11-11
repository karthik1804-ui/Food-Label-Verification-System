"""
Module: Personalised Dietary Preference and Allergen Matching Engine
=====================================================================
Evaluates parsed additives and ingredient text against a user's personalised
dietary profile (allergens, functional category avoidance, custom INS codes).

Rules & Academic Constraints:
  - Generates an independent Personalised Suitability Score (0–100).
  - Allergen alerts are flagged separately with top priority and are NOT
    confused with general additive deductions.
  - Explanations state user preference conflicts without fabricating universal
    medical claims.
  - Deterministic rule-based scoring: No SHAP/ML fabrication.
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Known animal-derived additives (Codex / Vegetarian Society references)
ANIMAL_DERIVED_INS: Dict[str, str] = {
    "120": "Carmine / Cochineal (derived from dried female cochineal insects)",
    "INS 120": "Carmine / Cochineal (derived from dried female cochineal insects)",
    "E120": "Carmine / Cochineal (derived from dried female cochineal insects)",
    "428": "Gelatin (derived from animal collagen)",
    "INS 428": "Gelatin (derived from animal collagen)",
    "E428": "Gelatin (derived from animal collagen)",
    "542": "Bone Phosphate (derived from animal bones)",
    "INS 542": "Bone Phosphate (derived from animal bones)",
    "E542": "Bone Phosphate (derived from animal bones)",
    "901": "Beeswax (produced by honey bees)",
    "INS 901": "Beeswax (produced by honey bees)",
    "E901": "Beeswax (produced by honey bees)",
    "904": "Shellac (resin secreted by female lac insects)",
    "INS 904": "Shellac (resin secreted by female lac insects)",
    "E904": "Shellac (resin secreted by female lac insects)",
    "920": "L-Cysteine (often produced from duck feathers or animal bristles)",
    "INS 920": "L-Cysteine (often produced from duck feathers or animal bristles)",
    "E920": "L-Cysteine (often produced from duck feathers or animal bristles)",
}

# Major food allergens and token keywords for detection in raw text & additive names
ALLERGEN_KEYWORD_MAP: Dict[str, List[str]] = {
    "peanuts": ["peanut", "groundnut", "arachis oil"],
    "tree_nuts": ["tree nut", "almond", "cashew", "walnut", "hazelnut", "pistachio", "pecan", "macadamia", "brazil nut"],
    "dairy": ["milk", "dairy", "casein", "whey", "lactose", "butter", "cheese", "cream", "milk solid", "skimmed milk", "sodium caseinate"],
    "gluten": ["gluten", "wheat", "barley", "rye", "malt", "oat", "spelt", "semolina", "maida", "atta", "wheat flour"],
    "soy": ["soy", "soya", "soybean", "tofu", "soy lecithin", "edamame"],
    "egg": ["egg", "albumin", "albumen", "ovalbumin", "egg powder", "egg yolk", "lysozyme"],
    "fish": ["fish", "cod", "salmon", "tuna", "anchovy", "gelatin (fish)", "isinglass"],
    "shellfish": ["shellfish", "crustacean", "crab", "shrimp", "prawn", "lobster", "mussel", "oyster", "clam"],
    "sesame": ["sesame", "tahini", "til", "gingelly"],
    "sulfites": [
        "sulfite", "sulphite", "sulfur dioxide", "sulphur dioxide",
        "metabisulfite", "metabisulphite", "e220", "e221", "e222", "e223",
        "e224", "e225", "e226", "e227", "e228", "ins 220", "ins 223"
    ],
    "mustard": ["mustard", "mustard seed", "mustard oil"],
}

SCORING_DISCLAIMER: str = (
    "This personalised suitability score (0-100) is calculated deterministically from "
    "user-configured dietary preferences, allergen keyword matching, and INS taxonomy "
    "functional classifications. It is an informational verification tool and does "
    "not constitute a medical diagnosis or clinical health guarantee."
)


def check_allergens(
    raw_text: str,
    user_allergens: List[str],
    parsed_additives: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Scans raw ingredient text and detected additives for occurrences of allergens
    specified in user_allergens. Returns a list of structured allergen alert objects.
    """
    if not user_allergens:
        return []

    text_lower = (raw_text or "").lower()
    
    # Also inspect detected additive names and alternative names
    additive_texts = []
    if parsed_additives:
        for a in parsed_additives:
            name = a.get("name", "")
            alt_names = a.get("alternative_names", [])
            additive_texts.append(name.lower())
            for alt in alt_names:
                additive_texts.append(alt.lower())
    combined_additive_text = " ".join(additive_texts)

    alerts = []
    seen_allergens = set()

    for allergen in user_allergens:
        key = allergen.strip().lower()
        if not key or key in seen_allergens:
            continue

        keywords = ALLERGEN_KEYWORD_MAP.get(key, [key])
        matched = False

        for kw in keywords:
            pattern = r"\b" + re.escape(kw) + r"(?:s|es)?\b"
            # 1. Check raw text
            match = re.search(pattern, text_lower)
            if match:
                alerts.append({
                    "allergen": allergen,
                    "matched_term": match.group(0),
                    "source": "raw_ingredient_text",
                    "severity": "CRITICAL",
                    "message": f"Critical allergen detected: '{match.group(0)}' matches your configured allergy to {allergen}.",
                    "action_required": "Avoid consumption if allergic."
                })
                seen_allergens.add(key)
                matched = True
                break

            # 2. Check additive names
            if not matched and combined_additive_text:
                match_add = re.search(pattern, combined_additive_text)
                if match_add:
                    alerts.append({
                        "allergen": allergen,
                        "matched_term": match_add.group(0),
                        "source": "detected_additive_name",
                        "severity": "CRITICAL",
                        "message": f"Critical allergen detected in additive: '{match_add.group(0)}' matches your configured allergy to {allergen}.",
                        "action_required": "Avoid consumption if allergic."
                    })
                    seen_allergens.add(key)
                    matched = True
                    break

    return alerts


def evaluate_dietary_preferences(
    parsed_additives: List[Dict[str, Any]],
    raw_text: str,
    dietary_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates detected additives and raw text against the user's dietary profile.
    Produces deterministic rule-based scoring (0-100), segmented into:
      - critical_violations (allergens, strictly avoided INS codes, animal derivatives)
      - warnings (category conflicts, caution INS codes)
      - acceptable_additives (detected additives with no profile conflicts)
      - score_deductions (transparent rule-based audit breakdown)
    """
    if not dietary_profile:
        return {
            "personal_score": 100,
            "personal_verdict": "No Profile Applied (Guest Mode)",
            "allergen_alerts": [],
            "critical_violations": [],
            "warnings": [],
            "acceptable_additives": parsed_additives or [],
            "preference_conflicts": [],
            "caution_items": [],
            "score_deductions": [],
            "preset_name": "none",
            "is_personalized": False,
            "disclaimer": SCORING_DISCLAIMER
        }

    preset_name = dietary_profile.get("preset_name", "custom")
    avoid_colors = bool(dietary_profile.get("avoid_synthetic_colors", False))
    avoid_preserv = bool(dietary_profile.get("avoid_preservatives", False))
    avoid_sweeteners = bool(dietary_profile.get("avoid_artificial_sweeteners", False))
    avoid_msg = bool(dietary_profile.get("avoid_msg_flavor_enhancers", False))
    avoid_animal = bool(dietary_profile.get("avoid_animal_derivatives", False))
    user_allergens = list(dietary_profile.get("custom_allergens") or [])
    
    custom_avoid_ins = {c.strip().upper() for c in (dietary_profile.get("custom_avoid_ins") or [])}
    custom_caution_ins = {c.strip().upper() for c in (dietary_profile.get("custom_caution_ins") or [])}

    # 1. Allergen Detection
    allergen_alerts = check_allergens(raw_text, user_allergens, parsed_additives)

    critical_violations: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    acceptable_additives: List[Dict[str, Any]] = []
    score_deductions: List[Dict[str, Any]] = []

    # Record allergen deductions (CRITICAL: -50 per matched allergen)
    for alert in allergen_alerts:
        deduction_entry = {
            "rule_id": "RULE_CRITICAL_ALLERGEN",
            "item_code": alert.get("allergen", "Allergen"),
            "item_name": f"Allergen: {alert.get('allergen')}",
            "conflict_type": "allergen_violation",
            "severity": "CRITICAL",
            "points_deducted": 50,
            "reason": alert.get("message", "Allergen conflict"),
            "source": "User Dietary Profile (Allergens)"
        }
        score_deductions.append(deduction_entry)
        critical_violations.append({
            "type": "allergen",
            "name": alert.get("allergen"),
            "term": alert.get("matched_term"),
            "message": alert.get("message"),
            "severity": "CRITICAL"
        })

    # 2. Additive Matching
    for item in parsed_additives:
        code = str(item.get("code", "")).upper()
        clean_code = str(item.get("clean_code", "")).upper()
        name = item.get("name", "Additive")
        color_origin = str(item.get("color_origin", "not_applicable")).lower()
        is_color = bool(item.get("is_color", False))
        categories = [str(c).lower() for c in item.get("functional_categories", [])]
        raw_class = str(item.get("class", "")).lower()

        additive_conflicts = []
        is_acceptable = True

        # Check explicit custom avoid (CRITICAL: -20)
        is_explicit_avoid = (
            code in custom_avoid_ins or
            clean_code in custom_avoid_ins or
            f"INS {clean_code}" in custom_avoid_ins or
            f"E{clean_code}" in custom_avoid_ins
        )
        if is_explicit_avoid:
            deduction = 20
            reason = f"Explicitly listed in your avoided INS codes list ({code})."
            crit_item = {
                "rule_id": "RULE_EXPLICIT_AVOID_INS",
                "item_code": code,
                "item_name": name,
                "conflict_type": "custom_avoid_code",
                "severity": "CRITICAL",
                "points_deducted": deduction,
                "reason": reason,
                "source": "User Custom Avoidance List"
            }
            score_deductions.append(crit_item)
            critical_violations.append({
                "type": "custom_avoid_code",
                "code": code,
                "name": name,
                "reason": reason,
                "severity": "CRITICAL"
            })
            is_acceptable = False
            continue  # Don't double-penalize the same additive with category checks

        # Check animal derivatives (CRITICAL: -20 if strictly avoided)
        if avoid_animal and (clean_code in ANIMAL_DERIVED_INS or code in ANIMAL_DERIVED_INS):
            origin_note = ANIMAL_DERIVED_INS.get(clean_code) or ANIMAL_DERIVED_INS.get(code) or "Animal origin"
            deduction = 20
            reason = f"Potentially derived from animal sources: {origin_note}."
            crit_item = {
                "rule_id": "RULE_ANIMAL_DERIVATIVE",
                "item_code": code,
                "item_name": name,
                "conflict_type": "animal_derived",
                "severity": "CRITICAL",
                "points_deducted": deduction,
                "reason": reason,
                "source": "Codex / Vegetarian Standards"
            }
            score_deductions.append(crit_item)
            critical_violations.append({
                "type": "animal_derived",
                "code": code,
                "name": name,
                "reason": reason,
                "severity": "CRITICAL"
            })
            is_acceptable = False
            continue

        # Check explicit custom caution (WARNING: -5)
        is_explicit_caution = (
            code in custom_caution_ins or
            clean_code in custom_caution_ins or
            f"INS {clean_code}" in custom_caution_ins or
            f"E{clean_code}" in custom_caution_ins
        )
        if is_explicit_caution:
            deduction = 5
            reason = f"Listed in your caution/sensitivity list ({code})."
            warn_item = {
                "rule_id": "RULE_CAUTION_INS",
                "item_code": code,
                "item_name": name,
                "conflict_type": "custom_caution_code",
                "severity": "WARNING",
                "points_deducted": deduction,
                "reason": reason,
                "source": "User Caution List"
            }
            score_deductions.append(warn_item)
            warnings.append({
                "type": "custom_caution_code",
                "code": code,
                "name": name,
                "reason": reason,
                "severity": "WARNING"
            })
            is_acceptable = False

        # Check synthetic colors (WARNING: -15)
        if avoid_colors and (color_origin == "synthetic" or (is_color and color_origin != "natural")):
            deduction = 15
            reason = f"Synthetic/artificial food color ({name}) contradicts your preference to avoid synthetic colors."
            warn_item = {
                "rule_id": "RULE_SYNTHETIC_COLOR",
                "item_code": code,
                "item_name": name,
                "conflict_type": "synthetic_color",
                "severity": "WARNING",
                "points_deducted": deduction,
                "reason": reason,
                "source": "INS Taxonomy / Food Color Specification"
            }
            score_deductions.append(warn_item)
            warnings.append({
                "type": "synthetic_color",
                "code": code,
                "name": name,
                "reason": reason,
                "severity": "WARNING"
            })
            is_acceptable = False

        # Check preservatives (WARNING: -15)
        if avoid_preserv and (any("preserv" in c for c in categories) or "preserv" in raw_class):
            deduction = 15
            reason = f"Food preservative ({name}) contradicts your preference to avoid added chemical preservatives."
            warn_item = {
                "rule_id": "RULE_PRESERVATIVE",
                "item_code": code,
                "item_name": name,
                "conflict_type": "preservative",
                "severity": "WARNING",
                "points_deducted": deduction,
                "reason": reason,
                "source": "INS Functional Class 2"
            }
            score_deductions.append(warn_item)
            warnings.append({
                "type": "preservative",
                "code": code,
                "name": name,
                "reason": reason,
                "severity": "WARNING"
            })
            is_acceptable = False

        # Check artificial sweeteners (WARNING: -15)
        if avoid_sweeteners and (any("sweeten" in c for c in categories) or "sweeten" in raw_class):
            deduction = 15
            reason = f"Intense/artificial sweetener ({name}) contradicts your preference to avoid sweeteners."
            warn_item = {
                "rule_id": "RULE_ARTIFICIAL_SWEETENER",
                "item_code": code,
                "item_name": name,
                "conflict_type": "artificial_sweetener",
                "severity": "WARNING",
                "points_deducted": deduction,
                "reason": reason,
                "source": "INS Functional Class 1"
            }
            score_deductions.append(warn_item)
            warnings.append({
                "type": "artificial_sweetener",
                "code": code,
                "name": name,
                "reason": reason,
                "severity": "WARNING"
            })
            is_acceptable = False

        # Check MSG / Flavor enhancers (WARNING: -15)
        if avoid_msg and (any("flavor" in c or "enhanc" in c for c in categories) or "enhanc" in raw_class or "621" in clean_code):
            deduction = 15
            reason = f"Flavor enhancer ({name}) contradicts your preference to avoid MSG and flavour enhancers."
            warn_item = {
                "rule_id": "RULE_FLAVOR_ENHANCER",
                "item_code": code,
                "item_name": name,
                "conflict_type": "flavor_enhancer",
                "severity": "WARNING",
                "points_deducted": deduction,
                "reason": reason,
                "source": "INS Functional Class 5"
            }
            score_deductions.append(warn_item)
            warnings.append({
                "type": "flavor_enhancer",
                "code": code,
                "name": name,
                "reason": reason,
                "severity": "WARNING"
            })
            is_acceptable = False

        if is_acceptable:
            acceptable_additives.append(item)

    # 3. Deterministic Score Computation (0-100)
    raw_score = 100
    for d in score_deductions:
        raw_score -= d.get("points_deducted", 0)

    # Critical Safety Cap:
    # If any critical allergen is detected, score is capped strictly at 20 max
    if allergen_alerts:
        personal_score = min(20, max(0, raw_score))
    else:
        personal_score = max(0, min(100, raw_score))

    # 4. Formulate Scientific Verdict
    if allergen_alerts:
        personal_verdict = "ALLERGEN WARNING - Unsafe for Configured Profile"
    elif personal_score >= 90:
        personal_verdict = "Highly Suitable"
    elif personal_score >= 70:
        personal_verdict = "Moderately Suitable / Minor Conflicts"
    elif personal_score >= 40:
        personal_verdict = "Caution - Notable Conflicts"
    else:
        personal_verdict = "High Risk / Unsuitable for Profile"

    # Backward-compatible structures
    preference_conflicts = [
        {
            "code": w.get("code", "N/A"),
            "name": w.get("name", "Additive"),
            "conflict_type": w.get("conflict_type") or w.get("type", "conflict"),
            "type": w.get("type", "conflict"),
            "reason": w.get("reason", ""),
            "deduction": w.get("points_deducted") or w.get("deduction", 15)
        }
        for w in (critical_violations + warnings) if w.get("type") != "allergen"
    ]
    caution_items = [
        {
            "code": w.get("code", "N/A"),
            "name": w.get("name", "Additive"),
            "caution_type": w.get("type", "custom_caution_code"),
            "reason": w.get("reason", ""),
            "deduction": w.get("points_deducted") or w.get("deduction", 5)
        }
        for w in warnings if w.get("type") == "custom_caution_code"
    ]

    return {
        "personal_score": personal_score,
        "personal_verdict": personal_verdict,
        "allergen_alerts": allergen_alerts,
        "critical_violations": critical_violations,
        "warnings": warnings,
        "acceptable_additives": acceptable_additives,
        "preference_conflicts": preference_conflicts,
        "caution_items": caution_items,
        "score_deductions": score_deductions,
        "preset_name": preset_name,
        "is_personalized": True,
        "disclaimer": SCORING_DISCLAIMER
    }
