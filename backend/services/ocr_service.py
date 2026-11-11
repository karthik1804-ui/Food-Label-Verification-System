"""
Module: OCR Image Preprocessing, Ingredient Section Identification & Safety Gate
================================================================================
Computer vision preprocessing and OCR safety evaluation for food packaging labels:
  - Blur detection (Laplacian variance)
  - Contrast Limited Adaptive Histogram Equalization (CLAHE) for curved/uneven lighting
  - Small font edge sharpening via unsharp masking
  - Ingredient section boundary identification and extraction
  - Parenthesis-aware ingredient clause separation
  - OCR safety gate: prevents definitive dietary scoring from insufficient OCR evidence
"""

import re
import base64
import logging
from typing import Tuple, Dict, Any, List, Optional
import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Blurriness threshold: Laplacian variance < 70.0 is considered blurry
BLUR_THRESHOLD = 70.0

# Minimum resolution recommendation
MIN_RECOMMENDED_WIDTH = 1000
MIN_RECOMMENDED_HEIGHT = 800

# Boundary markers that typically terminate the ingredients section on packaging
SECTION_TERMINATORS = [
    r"\bnutrition(?:al)?\s*(?:facts|info|information)?\b",
    r"\bmfg(?:\.|\s+date)?\b",
    r"\bmfd(?:\.|\s+by)?\b",
    r"\bmanufactured\s+by\b",
    r"\bmarketed\s+by\b",
    r"\bpacked\s+by\b",
    r"\bbest\s+before\b",
    r"\bexpiry\s*(?:date)?\b",
    r"\bnet\s+wt(?:\.|\s+weight)?\b",
    r"\bfssai\b",
    r"\blic(?:\.|\s+no)?\b",
    r"\bstore\s+in\s+a\s+cool\b",
    r"\bcountry\s+of\s+origin\b",
    r"\bcustomer\s+care\b",
    r"\bfor\s+feedback\b",
    r"\bbar\s*code\b"
]


def decode_image_input(image_input: Any) -> Optional[np.ndarray]:
    """
    Decodes an image from bytes, bytearray, base64 string, or existing numpy array.
    Returns BGR numpy array or None on failure.
    """
    if image_input is None:
        return None

    if isinstance(image_input, np.ndarray):
        return image_input

    try:
        raw_bytes = None
        if isinstance(image_input, (bytes, bytearray)):
            raw_bytes = bytes(image_input)
        elif isinstance(image_input, str):
            clean_str = image_input.strip()
            if "," in clean_str:
                clean_str = clean_str.split(",", 1)[1]
            raw_bytes = base64.b64decode(clean_str)

        if raw_bytes:
            nparr = np.frombuffer(raw_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
    except Exception as e:
        logger.warning("Failed to decode image input: %s", str(e))

    return None


def assess_image_quality(img: np.ndarray) -> Dict[str, Any]:
    """
    Evaluates image sharpness (Laplacian variance), illumination uniformity,
    and dimensions for OCR suitability.
    """
    if img is None or img.size == 0:
        return {
            "is_valid": False,
            "blur_score": 0.0,
            "is_blurry": True,
            "lighting_uniformity": 0.0,
            "is_uneven_lighting": True,
            "dimensions": (0, 0),
            "quality_grade": "Unusable"
        }

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img

    # 1. Sharpness via Laplacian variance
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    is_blurry = lap_var < BLUR_THRESHOLD

    # 2. Lighting uniformity across 4 quadrants
    mid_y, mid_x = h // 2, w // 2
    quadrants = [
        gray[:mid_y, :mid_x],
        gray[:mid_y, mid_x:],
        gray[mid_y:, :mid_x],
        gray[mid_y:, mid_x:]
    ]
    quad_means = [float(np.mean(q)) for q in quadrants if q.size > 0]
    lighting_std = float(np.std(quad_means)) if quad_means else 0.0
    is_uneven = lighting_std > 35.0  # High standard deviation between quadrants

    # 3. Overall quality grade
    if is_blurry or w < 400 or h < 300:
        grade = "Low" if lap_var > 40.0 else "Unusable"
    elif is_uneven or w < MIN_RECOMMENDED_WIDTH:
        grade = "Adequate"
    else:
        grade = "High"

    return {
        "is_valid": True,
        "blur_score": round(lap_var, 2),
        "is_blurry": is_blurry,
        "lighting_uniformity_score": round(max(0.0, 100.0 - lighting_std * 2), 1),
        "is_uneven_lighting": is_uneven,
        "dimensions": (w, h),
        "quality_grade": grade
    }


def preprocess_label_image(
    image_input: Any,
    upscale_small: bool = True
) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
    """
    Performs full computer vision preprocessing on a food package image:
      1. Image decoding and validation
      2. Quality assessment (sharpness, lighting)
      3. Resolution normalization (upscaling small packaging labels)
      4. CLAHE contrast enhancement for curved/glossy surfaces
      5. Unsharp masking to sharpen small ingredient fonts
    Returns: (preprocessed_grayscale_image, quality_metrics)
    """
    img = decode_image_input(image_input)
    if img is None:
        return None, {"is_valid": False, "error": "Invalid or unreadable image data"}

    metrics = assess_image_quality(img)
    h, w = img.shape[:2]

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img

    # Resolution upscaling for small packaging labels
    if upscale_small and (w < MIN_RECOMMENDED_WIDTH or h < MIN_RECOMMENDED_HEIGHT):
        scale_x = max(1.0, MIN_RECOMMENDED_WIDTH / max(1, w))
        scale_y = max(1.0, MIN_RECOMMENDED_HEIGHT / max(1, h))
        scale = max(scale_x, scale_y)
        if scale > 1.1:
            new_w = int(w * scale)
            new_h = int(h * scale)
            gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            metrics["upscaled"] = True
            metrics["processed_dimensions"] = (new_w, new_h)
    else:
        metrics["upscaled"] = False
        metrics["processed_dimensions"] = (w, h)

    # Adaptive Contrast Enhancement (CLAHE) - handles curved packaging shadows
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(gray)

    # Unsharp Masking for small font crispness
    blurred = cv2.GaussianBlur(contrast_enhanced, (0, 0), sigmaX=3.0)
    sharpened = cv2.addWeighted(contrast_enhanced, 1.4, blurred, -0.4, 0)

    return sharpened, metrics


def identify_ingredient_section(raw_text: str) -> Dict[str, Any]:
    """
    Identifies and isolates the ingredient section from whole-package OCR text.
    Filters out nutrition panels, manufacturer addresses, and marketing text.
    """
    if not raw_text or not raw_text.strip():
        return {
            "section_found": False,
            "ingredient_text": "",
            "raw_text": "",
            "confidence_indicator": 0.0
        }

    text_clean = raw_text.strip()
    
    # Ingredient header patterns (English, French, Hindi romanized, common variants)
    header_pattern = re.compile(
        r"(?:^|\n|\b)(?:ingredients?|ingr[eé]dients?|contents?|contains?|samagri)\s*[:\-]\s*",
        re.IGNORECASE
    )

    match = header_pattern.search(text_clean)
    if not match:
        # No explicit header found; use entire text with lower section confidence
        return {
            "section_found": False,
            "ingredient_text": text_clean,
            "raw_text": text_clean,
            "confidence_indicator": 0.5
        }

    start_idx = match.end()
    remaining_text = text_clean[start_idx:]

    # Search for the earliest boundary terminator in the remaining text
    end_idx = len(remaining_text)
    for term in SECTION_TERMINATORS:
        term_match = re.search(term, remaining_text, re.IGNORECASE)
        if term_match and term_match.start() < end_idx:
            # Only terminate if we've already captured a meaningful chunk of text
            if term_match.start() > 20:
                end_idx = term_match.start()

    isolated_section = remaining_text[:end_idx].strip()
    # Strip any trailing colon or punctuation
    isolated_section = re.sub(r"[\s\:\-]+$", "", isolated_section)

    return {
        "section_found": True,
        "ingredient_text": isolated_section if len(isolated_section) > 10 else text_clean,
        "raw_text": text_clean,
        "confidence_indicator": 0.95
    }


def clean_and_separate_ingredients(ingredient_text: str) -> List[str]:
    """
    Cleans OCR artifacts and splits ingredients into individual clauses.
    Preserves commas located inside parentheses (e.g. 'Permitted colors (INS 102, INS 110)').
    """
    if not ingredient_text:
        return []

    # 1. Normalize common OCR character glitches in INS contexts
    cleaned = ingredient_text
    cleaned = re.sub(r"\b1NS\b", "INS", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b1N5\b", "INS", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bIN5\b", "INS", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bE\s*-\s*", "E", cleaned)

    # 2. Parenthesis-aware splitting on commas, semicolons, bullets, and newlines
    # Walk character-by-character tracking paren depth
    ingredients = []
    current_token = []
    paren_depth = 0
    bracket_depth = 0

    for ch in cleaned:
        if ch in "([{":
            paren_depth += 1
            current_token.append(ch)
        elif ch in ")]}":
            paren_depth = max(0, paren_depth - 1)
            current_token.append(ch)
        elif ch in [",", ";", "•", "*", "|", "\n"] and paren_depth == 0 and bracket_depth == 0:
            token_str = "".join(current_token).strip()
            if len(token_str) > 1:
                # Clean stray leading/trailing quotes or periods
                token_clean = re.sub(r"^[\.\:\,\-\s]+|[\.\:\,\-\s]+$", "", token_str)
                if token_clean:
                    ingredients.append(token_clean)
            current_token = []
        else:
            current_token.append(ch)

    # Add final token
    if current_token:
        token_str = "".join(current_token).strip()
        token_clean = re.sub(r"^[\.\:\,\-\s]+|[\.\:\,\-\s]+$", "", token_str)
        if len(token_clean) > 1:
            ingredients.append(token_clean)

    return ingredients


def evaluate_ocr_quality_and_safety_gate(
    ocr_confidence: float,
    raw_text: str,
    image_quality: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Academic OCR Safety Gate:
    Evaluates whether the extracted OCR text provides sufficient evidentiary
    quality to permit definitive dietary risk scoring.

    Safety Rules:
      - ocr_confidence < 0.40 -> Insufficient text reliability.
      - is_blurry (Laplacian var < 70) -> Critical image degradation.
      - text length < 10 characters -> Missing or incomplete ingredient list.
      - In any failure condition, flags extraction warning and marks
        definitive_dietary_score_suppressed = True.
    """
    effective_conf = max(0.0, min(1.0, float(ocr_confidence if ocr_confidence is not None else 1.0)))
    clean_text = (raw_text or "").strip()
    text_len = len(clean_text)

    is_blurry = bool(image_quality.get("is_blurry", False)) if image_quality else False
    blur_score = float(image_quality.get("blur_score", 100.0)) if image_quality else 100.0

    flag_reasons: List[str] = []
    uncertain_tokens: List[str] = []

    # 1. Check OCR confidence threshold
    if effective_conf < 0.40:
        flag_reasons.append(
            f"Critical: Low OCR quality ({effective_conf:.0%}). Potential transcription errors; manual verification recommended."
        )

    # 2. Check blur threshold
    if is_blurry:
        flag_reasons.append(
            f"Degraded: Image is blurry (sharpness score {blur_score:.1f} < {BLUR_THRESHOLD}). Camera may have been moving or out of focus."
        )

    # 3. Check text sufficiency
    if text_len < 10:
        flag_reasons.append(
            "Incomplete: Extracted text is too short (< 10 chars) to represent a valid food ingredient list."
        )

    # 4. Search for uncertain or garbled tokens (symbols mixed with letters, e.g. 'c@rn', '1%s')
    garbled_pattern = re.compile(r"\b[a-zA-Z0-9]*[@#\$%^&*~][a-zA-Z0-9]*\b")
    for word in clean_text.split():
        if garbled_pattern.search(word) and len(word) > 2:
            uncertain_tokens.append(word)

    if uncertain_tokens:
        flag_reasons.append(
            f"Suspicious tokens detected ({len(uncertain_tokens)} unreadable character clusters). Potential OCR distortion."
        )

    is_safe = (len(flag_reasons) == 0)

    safety_warning = None
    recommendation = None
    if not is_safe:
        safety_warning = "CRITICAL OCR EXTRACTION WARNING: Image quality is insufficient for a reliable dietary verification."
        recommendation = (
            "Please upload or capture a clearer, well-lit photo. Flatten curved packaging, avoid flash reflections, "
            "and ensure the entire INGREDIENTS section is crisp and in focus."
        )

    return {
        "is_safe_for_decision": is_safe,
        "definitive_dietary_score_suppressed": not is_safe,
        "ocr_confidence": effective_conf,
        "text_length": text_len,
        "safety_warning": safety_warning,
        "recommendation": recommendation,
        "flag_reasons": flag_reasons,
        "uncertain_tokens": uncertain_tokens[:10],
        "image_quality": image_quality or {}
    }
