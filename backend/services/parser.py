"""
Module 1: INS Taxonomy & Feature Engineering Service
======================================================
Parses INS and E-number additives from food packaging text, maps them
against the authoritative local taxonomy, and constructs numerical feature vectors.

Academic & Regulatory Specifications:
  1. Extract INS numbers from OCR text (INS 102, INS:102, INS-102, INS 500(i)).
  2. Identify additives using official Codex / FSSAI names.
  3. Recognise alternative additive names and synonyms from taxonomy.
  4. Normalise OCR misreads and formatting variations.
  5. Match detected additives against the 750-entry taxonomy.
  6. Identify functional additive categories (Color, Preservative, Acidity regulator, etc.).
  7. Identify individual INS numbers.
  8. Handle and report duplicate detections.
  9. Record unmapped candidate terms for audit.
  10. Report ambiguous detections (generic parent codes like INS 150/500, unnumbered category statements).
  11. Strict MSG rule: Do not classify an additive as MSG unless actually identified as
      monosodium glutamate or INS 621.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ins_taxonomy.json")
_TAXONOMY_CACHE: Optional[Dict[str, Any]] = None
_SYNONYM_CACHE: Optional[Dict[str, str]] = None

# Valid E-number ranges (Codex Alimentarius / EU)
_VALID_E_NUMBER_MIN = 100
_VALID_E_NUMBER_MAX = 1599

# Ambiguous parent codes that should be flagged with an advisory note
AMBIGUOUS_PARENT_CODES = {
    "150": "Caramel Colour (generic) — specific class (150a Plain, 150b Caustic Sulphite, 150c Ammonia, or 150d Sulphite Ammonia) not specified on label.",
    "INS 150": "Caramel Colour (generic) — specific class (150a Plain, 150b Caustic Sulphite, 150c Ammonia, or 150d Sulphite Ammonia) not specified on label.",
    "500": "Sodium Carbonates (generic) — sub-form (500(i) Sodium Carbonate, 500(ii) Sodium Hydrogen Carbonate / Baking Soda, or 500(iii) Sodium Sesquicarbonate) not specified on label.",
    "INS 500": "Sodium Carbonates (generic) — sub-form (500(i) Sodium Carbonate, 500(ii) Sodium Hydrogen Carbonate / Baking Soda, or 500(iii) Sodium Sesquicarbonate) not specified on label.",
    "471": "Mono- and Di-glycerides of Fatty Acids — specific fatty acid source (plant vs animal origin) not specified on label.",
    "INS 471": "Mono- and Di-glycerides of Fatty Acids — specific fatty acid source (plant vs animal origin) not specified on label.",
}

# Generic category phrases that indicate presence of an additive class without specific INS code
GENERIC_CATEGORY_PATTERNS = [
    (r"\bpermitted\s+(?:synthetic|artificial|natural)?\s*colou?rs?\b", "Color", "Generic colour statement without specifying INS number"),
    (r"\badded\s+(?:artificial|synthetic|natural)?\s*colou?rs?\b", "Color", "Generic colour statement without specifying INS number"),
    (r"\bcontains\s+added\s+preservatives?\b", "Preservative", "Generic preservative statement without specifying INS number"),
    (r"\bpermitted\s+preservatives?\b", "Preservative", "Generic preservative statement without specifying INS number"),
    (r"\bcontains\s+artificial\s+sweeteners?\b", "Sweetener", "Generic sweetener statement without specifying INS number"),
    (r"\bcontains\s+added\s+flavou?r\s+enhancers?\b", "Flavor enhancer", "Generic flavour enhancer statement without specifying INS number"),
]


def load_taxonomy() -> Dict[str, Any]:
    """Loads and caches the local ins_taxonomy.json file."""
    global _TAXONOMY_CACHE
    if _TAXONOMY_CACHE is None:
        if os.path.exists(TAXONOMY_PATH):
            with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
                _TAXONOMY_CACHE = json.load(f)
            logger.info("Taxonomy loaded: %d entries", len(_TAXONOMY_CACHE))
        else:
            logger.warning("Taxonomy file not found at %s. Using empty fallback.", TAXONOMY_PATH)
            _TAXONOMY_CACHE = {}
    return _TAXONOMY_CACHE


def get_synonym_map() -> Dict[str, str]:
    """
    Builds and caches an extensive synonym mapping from official names,
    alternative names, and common synonyms to canonical INS codes.
    """
    global _SYNONYM_CACHE
    if _SYNONYM_CACHE is not None:
        return _SYNONYM_CACHE

    taxonomy = load_taxonomy()
    synonyms: Dict[str, str] = {}

    # Seed curated core chemical synonyms
    curated_seeds = {
        "SODIUM NITRITE": "INS 250",
        "SODIUM NITRATE": "INS 251",
        "POTASSIUM NITRITE": "INS 249",
        "POTASSIUM NITRATE": "INS 252",
        "SODIUM BENZOATE": "INS 211",
        "POTASSIUM BENZOATE": "INS 212",
        "POTASSIUM SORBATE": "INS 202",
        "CALCIUM SORBATE": "INS 203",
        "SORBIC ACID": "INS 200",
        "BENZOIC ACID": "INS 210",
        "SULPHUR DIOXIDE": "INS 220",
        "SULFUR DIOXIDE": "INS 220",
        "SODIUM SULPHITE": "INS 221",
        "SODIUM SULFITE": "INS 221",
        "SODIUM METABISULPHITE": "INS 223",
        "SODIUM METABISULFITE": "INS 223",
        "POTASSIUM METABISULPHITE": "INS 224",
        "NISIN": "INS 234",
        "BUTYLATED HYDROXYANISOLE": "INS 320",
        "BUTYLATED HYDROXYTOLUENE": "INS 321",
        "BHA": "INS 320",
        "BHT": "INS 321",
        "ASCORBIC ACID": "INS 300",
        "SODIUM ASCORBATE": "INS 301",
        "CALCIUM ASCORBATE": "INS 302",
        "TOCOPHEROLS": "INS 306",
        "ALPHA TOCOPHEROL": "INS 307",
        "TARTRAZINE": "INS 102",
        "QUINOLINE YELLOW": "INS 104",
        "SUNSET YELLOW": "INS 110",
        "SUNSET YELLOW FCF": "INS 110",
        "CARMOISINE": "INS 122",
        "PONCEAU 4R": "INS 124",
        "ALLURA RED": "INS 129",
        "ALLURA RED AC": "INS 129",
        "BRILLIANT BLUE": "INS 133",
        "BRILLIANT BLUE FCF": "INS 133",
        "FAST GREEN FCF": "INS 143",
        "CURCUMIN": "INS 100",
        "RIBOFLAVIN": "INS 101",
        "BETA CAROTENE": "INS 160A",
        "CARAMEL IV": "INS 150D",
        "CARAMEL COLOUR": "INS 150D",
        "CARAMEL COLOR": "INS 150D",
        "ASPARTAME": "INS 951",
        "ACESULFAME K": "INS 950",
        "ACESULFAME POTASSIUM": "INS 950",
        "SUCRALOSE": "INS 955",
        "SACCHARIN": "INS 954",
        "SODIUM SACCHARIN": "INS 954",
        "CYCLAMATE": "INS 952",
        "STEVIA": "INS 960",
        "STEVIOL GLYCOSIDES": "INS 960",
        "SORBITOL": "INS 420",
        "MONOSODIUM GLUTAMATE": "INS 621",
        "MSG": "INS 621",
        "DISODIUM INOSINATE": "INS 631",
        "DISODIUM GUANYLATE": "INS 627",
        "LECITHIN": "INS 322",
        "SOY LECITHIN": "INS 322",
        "SOYA LECITHIN": "INS 322",
        "MONO AND DIGLYCERIDES": "INS 471",
        "CARRAGEENAN": "INS 407",
        "XANTHAN GUM": "INS 415",
        "GUAR GUM": "INS 412",
        "CITRIC ACID": "INS 330",
        "LACTIC ACID": "INS 270",
        "ACETIC ACID": "INS 260",
        "PHOSPHORIC ACID": "INS 338",
        "SODIUM BICARBONATE": "INS 500",
        "BAKING SODA": "INS 500",
        "POTASSIUM CHLORIDE": "INS 508",
    }
    synonyms.update(curated_seeds)

    # Populate dynamically from taxonomy entries
    for key, item in taxonomy.items():
        clean_key = re.sub(r"(?i:^INS|^E|[\s\-_:()\[\]])", "", key).upper()
        canonical_code = f"INS {clean_key}"

        name = item.get("name")
        if name:
            clean_name = re.sub(r"\s*\([^)]*\)", "", name).strip().upper()
            if len(clean_name) >= 3 and not clean_name.startswith("ADDITIVE"):
                synonyms[clean_name] = canonical_code

        for alt in item.get("alternative_names", []):
            clean_alt = re.sub(r"\s*\([^)]*\)", "", alt).strip().upper()
            if len(clean_alt) >= 3 and not clean_alt.startswith("ADDITIVE"):
                synonyms[clean_alt] = canonical_code

    _SYNONYM_CACHE = synonyms
    return _SYNONYM_CACHE


def normalize_ocr_errors(text: str) -> str:
    """
    Normalizes common OCR character misreads (I→1, l→1, O→0) specifically
    within INS and E-number token contexts without damaging regular English words.
    """
    if not text:
        return ""

    def clean_ins_match(match):
        prefix = match.group(1)
        body = match.group(2)
        cleaned = (body.replace("I", "1").replace("l", "1")
                   .replace("O", "0").replace("o", "0"))
        return f"{prefix}{cleaned}"

    def clean_e_match(match):
        prefix = match.group(1)
        body = match.group(2)
        cleaned = (body.replace("I", "1").replace("l", "1")
                   .replace("O", "0").replace("o", "0"))
        return f"{prefix}{cleaned}"

    # Normalize 1NS / 1N5 / IN5 glitches
    text = re.sub(r"\b1NS\b", "INS", text, flags=re.IGNORECASE)
    text = re.sub(r"\b1N5\b", "INS", text, flags=re.IGNORECASE)
    text = re.sub(r"\bIN5\b", "INS", text, flags=re.IGNORECASE)

    # Pass 1: INS tokens
    text = re.sub(
        r"(\bINS\s*[:\-]?\s*)([0-9IlOo]{2,4}[a-zA-Z]?(?:\([ivxIVX1-9]+\))?)",
        clean_ins_match, text, flags=re.IGNORECASE
    )

    # Pass 2: E-number tokens (only immediately after E-prefix in INS context)
    text = re.sub(
        r"(\bE\s*[:\-]?\s*)([0-9IlOo]{2,4}[a-zA-Z]?(?:\([ivxIVX1-9]+\))?)",
        clean_e_match, text, flags=re.IGNORECASE
    )

    return text


def _is_valid_e_number(digits_str: str) -> bool:
    """
    Returns True only if the numeric part of an E-number falls within the
    known Codex Alimentarius food additive range (100–1599).
    Prevents matching expiry dates (E2026), serial codes (E10, E5), etc.
    """
    try:
        base = int(re.match(r"(\d+)", digits_str).group(1))
        return _VALID_E_NUMBER_MIN <= base <= _VALID_E_NUMBER_MAX
    except (AttributeError, ValueError):
        return False


def extract_additive_tokens(text: str, deduplicate: bool = True) -> List[str]:
    """
    Extracts additive candidates using validated regex patterns:
      1. Standard INS tokens: INS 250, INS:551, INS-160c, INS 500(i)
      2. Validated E-numbers: E250, E-250 (range 100-1599, excluding nutrition units)
      3. Category-bracketed numbers: 'permitted colours (102, 110)', 'emulsifier (322)'
      4. Official chemical names & synonyms (760+ dynamic entries from taxonomy)
    """
    if not text:
        return []

    cleaned = normalize_ocr_errors(text)
    found_tokens: List[str] = []

    # 1. INS variants: INS 250, INS:551, INS-160c, INS 500(i)
    ins_pattern = re.compile(
        r"\bINS\s*[:\-]?\s*(\d{2,4}[a-zA-Z]?(?:\([ivxIVX1-9]+\))?)",
        re.IGNORECASE
    )
    for match in ins_pattern.finditer(cleaned):
        code_body = match.group(1).upper()
        found_tokens.append(f"INS {code_body}")

    # 2. E-number variants — with range validation AND nutrition-context filtering
    _NUTRITION_CONTEXT = re.compile(
        r"(?:vitamin|vit\.|tocopherol|vitamin\s+e)\s*$",
        re.IGNORECASE
    )
    _QUANTITY_UNIT_SUFFIX = re.compile(
        r"^(?:mg|g\b|mcg|iu|ml|%|kg|μg|ug|ppm)",
        re.IGNORECASE
    )

    e_pattern = re.compile(
        r"\bE\s*[:\-]?\s*(\d{2,4}[a-zA-Z]?(?:\([ivxIVX1-9]+\))?)\b",
        re.IGNORECASE
    )
    for match in e_pattern.finditer(cleaned):
        digits_part = match.group(1)

        start_pos = match.start()
        prefix_window = cleaned[max(0, start_pos - 15):start_pos]
        if _NUTRITION_CONTEXT.search(prefix_window):
            continue

        suffix_pos = match.end()
        suffix_window = cleaned[suffix_pos:suffix_pos + 6].lstrip()
        if _QUANTITY_UNIT_SUFFIX.match(suffix_window):
            continue

        if _is_valid_e_number(digits_part):
            code_body = digits_part.upper()
            found_tokens.append(f"INS {code_body}")

    # 3. Category parenthetical code lists: e.g. 'colour (102, 110)', 'emulsifier (322, 471)'
    category_paren_pattern = re.compile(
        r"(?:colou?r|acidity\s+regulator|preservative|emulsifier|stabiliser|stabilizer|flavour\s+enhancer|flavor\s+enhancer|sweetener|raising\s+agent|thickener|antioxidant|anti\-?caking\s+agent)s?\s*(?:\([^)]*\))?\s*\(\s*([0-9IlOoivxIVX1-9,\s\-\(\)]+)\s*\)",
        re.IGNORECASE
    )
    for m in category_paren_pattern.finditer(cleaned):
        inside_paren = m.group(1)
        raw_items = inside_paren.split(",")
        for item_str in raw_items:
            clean_item = re.sub(r"[^\w\(\)]", "", item_str.strip()).upper()
            # Clean OCR glitch in digits
            clean_item = clean_item.replace("I", "1").replace("L", "1").replace("O", "0")
            if re.match(r"^\d{2,4}[A-Z]?(?:\([IVX1-9]+\))?$", clean_item):
                found_tokens.append(f"INS {clean_item}")

    # 4. Official chemical names and synonyms from dynamic taxonomy dictionary
    synonym_map = get_synonym_map()
    upper_text = cleaned.upper()
    for name, code in sorted(synonym_map.items(), key=lambda x: -len(x[0])):
        pattern = r"\b" + re.escape(name) + r"\b"
        if re.search(pattern, upper_text):
            found_tokens.append(code)

    if not deduplicate:
        return found_tokens

    # Deduplicate preserving first-seen order
    unique_tokens: List[str] = []
    seen: set = set()
    for t in found_tokens:
        clean_key = re.sub(r"[\s\-_:()\[\]]", "", t.upper())
        if clean_key not in seen:
            seen.add(clean_key)
            unique_tokens.append(t)

    return unique_tokens


def parse_additives_detailed(
    text: str,
    ocr_confidence: float = 1.0
) -> Dict[str, Any]:
    """
    Complete Phase 8 Additive Identification & Classification Engine:
      1. Extracts INS tokens, E-numbers, parenthetical codes, and chemical names
      2. Normalizes text and OCR glyphs
      3. Resolves against the 750-entry taxonomy
      4. Groups detected additives into functional categories
      5. Isolates individual canonical INS numbers
      6. Handles and logs duplicate detections
      7. Identifies unmapped tokens
      8. Detects and reports ambiguous parent codes and generic category mentions
      9. Enforces strict MSG identification rule (only INS 621 / monosodium glutamate)
    """
    taxonomy = load_taxonomy()
    raw_tokens = extract_additive_tokens(text, deduplicate=False)

    parsed_additives: List[Dict[str, Any]] = []
    unmapped_tokens: List[str] = []
    ambiguous_detections: List[Dict[str, Any]] = []
    detected_categories: Dict[str, List[str]] = {}
    individual_ins_codes: List[str] = []
    duplicate_detections: List[Dict[str, Any]] = []

    seen_codes: Dict[str, int] = {}
    upper_text = (text or "").upper()

    for token in raw_tokens:
        clean_num = re.sub(r"(?i:^INS|^E|[\s\-:_()\[\]])", "", token).upper()

        # Check for ambiguous parent code (e.g. INS 150, INS 500, INS 471)
        if clean_num in AMBIGUOUS_PARENT_CODES or token in AMBIGUOUS_PARENT_CODES or f"INS {clean_num}" in AMBIGUOUS_PARENT_CODES:
            ambiguous_note = (
                AMBIGUOUS_PARENT_CODES.get(clean_num) or
                AMBIGUOUS_PARENT_CODES.get(token) or
                AMBIGUOUS_PARENT_CODES.get(f"INS {clean_num}")
            )
            canonical_amb_code = f"INS {clean_num}"
            if not any(a.get("code") == canonical_amb_code for a in ambiguous_detections):
                ambiguous_detections.append({
                    "code": canonical_amb_code,
                    "name": f"Additive {clean_num}",
                    "ambiguity_type": "generic_parent_code",
                    "explanation": ambiguous_note
                })

        item = (
            taxonomy.get(token) or
            taxonomy.get(clean_num) or
            taxonomy.get(f"INS {clean_num}") or
            taxonomy.get(f"E{clean_num}")
        )

        if not item and clean_num == "150":
            # Informative parent resolution for generic Caramel Colour
            item = {
                "code": "INS 150",
                "name": "Caramel Colour (generic)",
                "class": "Color",
                "functional_categories": ["Color"],
                "is_color": True,
                "color_origin": "synthetic",
                "alternative_names": ["Caramel", "Caramel Color", "Caramel Colour"],
                "verified_source": "Codex Alimentarius (CXS 192-1995)",
                "hazard_level": "Moderate",
                "hazard_weight": 0.5,
                "verified": True
            }

        if item:
            canonical_code = item.get("code", f"INS {clean_num}")
            clean_canonical = re.sub(r"(?i:^INS|^E|[\s\-:_()\[\]])", "", canonical_code).upper()

            # Handle duplicate detection
            if clean_canonical in seen_codes:
                seen_codes[clean_canonical] += 1
                duplicate_detections.append({
                    "code": canonical_code,
                    "token": token,
                    "times_detected": seen_codes[clean_canonical]
                })
                continue
            else:
                seen_codes[clean_canonical] = 1

            categories = list(item.get("functional_categories", [item.get("class", "Food Additive")]))
            primary_class = categories[0] if categories else item.get("class", "Food Additive")

            additive_entry = {
                "code":                  canonical_code,
                "clean_code":            clean_canonical,
                "name":                  item.get("name", f"Additive {clean_num}"),
                "official_name":         item.get("official_name") or item.get("name"),
                "class":                 primary_class,
                "functional_categories": categories,
                "is_color":              bool(item.get("is_color", False)),
                "color_origin":          item.get("color_origin", "not_applicable"),
                "alternative_names":     item.get("alternative_names", []),
                "verified_source":       item.get("verified_source", "Codex Alimentarius (CXS 192-1995) / FSSAI (2011)"),
                "hazard_level":          item.get("hazard_level", "Moderate"),
                "hazard_weight":         float(item.get("hazard_weight", 0.5)),
                "common_substitute":     item.get("common_substitute", ""),
                "description":           item.get("description", ""),
                "source":                item.get("source", "ins_taxonomy_v2"),
                "verified":              item.get("verified", False),
            }
            parsed_additives.append(additive_entry)
            individual_ins_codes.append(canonical_code)

            # Group into functional categories
            for cat in categories:
                if cat not in detected_categories:
                    detected_categories[cat] = []
                detected_categories[cat].append(canonical_code)
        else:
            unmapped_tokens.append(token)

    # Check for generic unnumbered category statements
    for pattern, category_name, explanation in GENERIC_CATEGORY_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Check if we already detected a specific code of this category
            has_specific_code = bool(detected_categories.get(category_name))
            if not has_specific_code:
                ambiguous_detections.append({
                    "matched_statement": match.group(0),
                    "category": category_name,
                    "ambiguity_type": "generic_category_statement_without_code",
                    "explanation": explanation
                })

    # Additive match confidence: fraction of detected tokens resolved in taxonomy
    total = len(raw_tokens)
    if total == 0:
        additive_match_conf = 1.0
    else:
        matched_ratio = len(parsed_additives) / total
        additive_match_conf = round(max(0.30, min(0.98, 0.65 + (0.33 * matched_ratio))), 2)

    return {
        "parsed_additives": parsed_additives,
        "unmapped_tokens": unmapped_tokens,
        "additive_match_confidence": additive_match_conf,
        "detected_categories": detected_categories,
        "individual_ins_codes": individual_ins_codes,
        "duplicate_detections": duplicate_detections,
        "ambiguous_detections": ambiguous_detections,
        "total_extracted_candidates": total
    }


def parse_additives_and_audit(
    text: str,
    ocr_confidence: float = 1.0
) -> Tuple[List[Dict[str, Any]], List[str], float]:
    """
    Standard backward-compatible interface:
    Returns (parsed_additives, unmapped_tokens, additive_match_confidence).
    """
    res = parse_additives_detailed(text, ocr_confidence=ocr_confidence)
    return res["parsed_additives"], res["unmapped_tokens"], res["additive_match_confidence"]


def construct_feature_vector(
    parsed_additives: List[Dict[str, Any]],
    nutriments: Dict[str, Any]
) -> Dict[str, float]:
    """
    Constructs a numerical feature vector for downstream rule evaluation.
    """
    features: Dict[str, float] = {
        "count_total":          float(len(parsed_additives)),
        "count_severe":         0.0,
        "count_high":           0.0,
        "count_moderate":       0.0,
        "count_low":            0.0,
        "total_hazard_weight":  0.0,
        "class_preservative":   0.0,
        "class_color":          0.0,
        "class_sweetener":      0.0,
        "class_flavor":         0.0,
        "class_emulsifier":     0.0,
        "has_ins_250":          0.0,
        "has_ins_211":          0.0,
        "has_ins_102":          0.0,
        "has_ins_621":          0.0,
        "has_ins_150d":         0.0,
        "has_ins_951":          0.0,
        "sugars_100g":          float(nutriments.get("sugars_100g") or 0.0),
        "sodium_100g":          float(nutriments.get("sodium_100g") or 0.0),
        "saturated_fat_100g":   float(nutriments.get("saturated_fat_100g") or 0.0),
    }

    for item in parsed_additives:
        h_level = str(item.get("hazard_level", "")).lower()
        h_weight = float(item.get("hazard_weight", 0.5))
        features["total_hazard_weight"] += h_weight

        if h_level == "severe":     features["count_severe"] += 1.0
        elif h_level == "high":     features["count_high"] += 1.0
        elif h_level == "moderate": features["count_moderate"] += 1.0
        else:                       features["count_low"] += 1.0

        f_class = str(item.get("class", "")).lower()
        if "preserv"  in f_class: features["class_preservative"] += 1.0
        elif "color"  in f_class: features["class_color"] += 1.0
        elif "sweet"  in f_class: features["class_sweetener"] += 1.0
        elif "flavor" in f_class or "enhanc" in f_class: features["class_flavor"] += 1.0
        elif "emuls"  in f_class or "stabil" in f_class: features["class_emulsifier"] += 1.0

        code_str = str(item.get("code", "")).upper()
        if "250"  in code_str: features["has_ins_250"]  = 1.0
        if "211"  in code_str: features["has_ins_211"]  = 1.0
        if "102"  in code_str: features["has_ins_102"]  = 1.0
        if "621"  in code_str: features["has_ins_621"]  = 1.0
        if "150D" in code_str: features["has_ins_150d"] = 1.0
        if "951"  in code_str: features["has_ins_951"]  = 1.0

    return features
