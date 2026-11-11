"""
Food Label Verification System — Main Flask API Server
======================================================
Explainable Rule-Based Food Safety Indicator and Personalised
Dietary Verification System Using Deep Learning and OCR.

IMPORTANT: This system uses a deterministic rule-based indicator score — NOT an ML model.
The scoring_engine.py module clearly labels all deductions as rule-based.
The term 'SHAP' has been removed from all modules and API responses.

Endpoints:
  POST /api/v1/analyze           — Full analysis pipeline (universal + personalised)
  GET  /api/v1/analyze           — Barcode query via ?ean= parameter
  GET  /api/v1/product/<barcode>  — Barcode validation + product lookup
  POST /api/v1/barcode/decode    — Image-based barcode detection (OpenCV BarcodeDetector)
  POST /api/v1/auth/register     — User registration
  POST /api/v1/auth/login        — User authentication
  POST /api/v1/auth/logout       — Session revocation
  GET  /api/v1/auth/me           — Current authenticated user and dietary profile
  GET  /api/v1/profile           — Retrieve user dietary profile
  PUT  /api/v1/profile           — Update user dietary profile
  GET  /api/v1/profile/presets   — List dietary presets (vegan, clean label, etc.)
  GET  /api/v1/history           — User scan history
  GET  /api/v1/audit/unmapped    — Human-in-the-loop audit queue
  POST /api/v1/audit/<id>/review — Reviewer action (confirm/reject/correct)
  GET  /api/health               — Health status
  POST /analyze                  — Legacy backward-compatible endpoint
"""

import os
import sys
import json
import base64
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(__file__))

from models.database import init_db, get_db_connection
from services.barcode import validate_ean13, fetch_product_by_barcode
from services.parser import (
    parse_additives_and_audit,
    parse_additives_detailed,
    construct_feature_vector,
    load_taxonomy
)
from services.scoring_engine import compute_rule_based_score, compute_safety_score_and_attributions
from services.counterfactual import generate_counterfactual_explanation
from services.audit import (
    evaluate_system_audit,
    get_audit_records,
    update_audit_record,
    get_audit_statistics,
    delete_audit_record
)
from services.regulatory_checker import get_regulatory_info_batch
from services.auth_service import (
    register_user,
    authenticate_user,
    verify_token,
    revoke_token,
    get_user_profile,
    update_user_profile,
    get_user_preferences,
    update_category_preferences,
    manage_additive_preference,
    manage_allergy_preferences,
    DIETARY_PRESETS
)
from services.preference_engine import evaluate_dietary_preferences
from services.barcode_decoder import decode_barcode_from_image
from services.personal_scoring import (
    get_user_history,
    count_user_history,
    get_history_record_by_id,
    delete_history_record,
    clear_user_history,
    export_user_history
)
from services.ocr_service import (
    preprocess_label_image,
    identify_ingredient_section,
    clean_and_separate_ingredients,
    evaluate_ocr_quality_and_safety_gate,
    assess_image_quality,
    decode_image_input
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("FoodLabelVerificationSystem")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = (
        "Content-Type, Authorization, X-Requested-With, Accept"
    )
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


# Pre-load data and initialize database on startup
load_taxonomy()
try:
    init_db()
except Exception as e:
    logger.warning("Database init on startup note: %s", str(e))


def _get_authenticated_user(req) -> Optional[Dict[str, Any]]:
    """Extracts and verifies Bearer token from Authorization header or query param."""
    auth_header = req.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        return verify_token(token)
    token_param = req.args.get("token") or (req.get_json(silent=True) or {}).get("token")
    if token_param:
        return verify_token(str(token_param).strip())
    return None


# ---------------------------------------------------------------------------
# Input Validation Helpers
# ---------------------------------------------------------------------------

def _validate_analyze_input(data: dict) -> tuple:
    """
    Validates /api/v1/analyze request payload.
    Returns (is_valid: bool, error_message: str)
    """
    if not isinstance(data, dict):
        return False, "Request body must be a JSON object"

    ean = data.get("ean") or data.get("barcode")
    text = data.get("text") or data.get("ingredients_text")

    if ean is not None:
        if not isinstance(ean, str):
            return False, "'ean' must be a string"
        if len(ean.strip()) > 20:
            return False, "'ean' too long — EAN-13 is 13 digits"

    if text is not None:
        if not isinstance(text, str):
            return False, "'text' must be a string"
        if len(text) > 10000:
            return False, "'text' too long — maximum 10,000 characters"

    if not ean and not text:
        return False, "Request must include 'ean' (barcode) or 'text' (ingredient text)"

    ocr_conf = data.get("ocr_confidence")
    if ocr_conf is not None:
        try:
            val = float(ocr_conf)
            if not (0.0 <= val <= 1.0):
                return False, "'ocr_confidence' must be between 0.0 and 1.0"
        except (TypeError, ValueError):
            return False, "'ocr_confidence' must be a float between 0.0 and 1.0"

    return True, ""


def _merge_nutrients(base: dict, override: dict) -> dict:
    """Merges base nutrients with optional user overrides."""
    result = dict(base)
    for key in ("sugars_100g", "sodium_100g", "saturated_fat_100g"):
        if key in override and override[key] is not None:
            try:
                result[key] = float(override[key])
            except (TypeError, ValueError):
                pass
    return result


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET", "OPTIONS"])
def index():
    if request.method == "OPTIONS":
        return "", 200
    return jsonify({
        "status": "healthy",
        "service": "food-label-verification-system",
        "version": "2.0.0",
        "scoring_method": "rule_based_indicator",
        "endpoints": {
            "analyze":     "POST /api/v1/analyze",
            "product":     "GET  /api/v1/product/<barcode>",
            "barcode_decode": "POST /api/v1/barcode/decode",
            "auth":        "POST /api/v1/auth/login",
            "profile":     "GET  /api/v1/profile",
            "history":     "GET  /api/v1/history",
            "audit_queue": "GET  /api/v1/audit/unmapped",
            "audit_review":"POST /api/v1/audit/<id>/review",
            "health":      "GET  /api/health"
        }
    })


@app.route("/api/health", methods=["GET", "OPTIONS"])
@app.route("/health", methods=["GET", "OPTIONS"])
def health():
    if request.method == "OPTIONS":
        return "", 200
    return jsonify({
        "status": "healthy",
        "service": "food-label-verification-system",
        "version": "2.0.0",
        "scoring_method": "rule_based_indicator"
    })


@app.route("/api/v1/analyze", methods=["POST", "GET", "OPTIONS"])
def analyze_v1():
    """
    Main food safety analysis endpoint.

    POST body (JSON):
      {
        "ean": "8901234567890",          // EAN-13 barcode (preferred)
        "text": "...",                   // Raw ingredient text (from OCR)
        "ocr_confidence": 0.85,          // Mean Tesseract word confidence (0.0–1.0)
        "nutrients": {...},              // Optional nutrient override
        "product": {...}                 // Optional product metadata override
      }

    Response schema (v2.0):
      - product: metadata
      - parsed_additives: taxonomy-mapped additive list
      - safety_indicator: rule-based score with explicit methodology label
      - regulatory_info: per-additive regulatory reference data
      - counterfactual: reformulation suggestion (when score < 75)
      - system_audit: 4-way confidence + HITL flag + flag reasons
    """
    if request.method == "OPTIONS":
        return "", 200

    # Parse request
    if request.method == "GET":
        data = {
            "ean": request.args.get("ean") or request.args.get("barcode", ""),
            "ocr_confidence": request.args.get("ocr_confidence", 1.0)
        }
    else:
        data = request.get_json(silent=True) or {}

    # Input validation
    is_valid, error_msg = _validate_analyze_input(data)
    if not is_valid:
        return jsonify({"error": "Invalid request", "message": error_msg}), 400

    try:
        ean = str(data.get("ean") or data.get("barcode") or "").strip()
        custom_text = str(data.get("text") or data.get("ingredients_text") or "").strip()
        custom_nutrients = data.get("nutrients") or {}
        custom_product = data.get("product") or {}
        raw_ocr_conf = data.get("ocr_confidence")
        if raw_ocr_conf is not None:
            try:
                ocr_confidence = float(raw_ocr_conf)
            except (ValueError, TypeError):
                ocr_confidence = 1.0 if not custom_text else 0.85
        else:
            ocr_confidence = 1.0 if not custom_text else 0.85
        # Clamp to [0, 1]
        ocr_confidence = max(0.0, min(1.0, ocr_confidence))

        # --- 1. Product & Nutrient Resolution ---
        product_found = False
        if ean:
            is_valid_ean = validate_ean13(ean)
            product_info = fetch_product_by_barcode(ean)
            product_found = bool(product_info.get("found", False))
            if custom_product:
                product_info.update(custom_product)
            raw_text = custom_text or product_info.get("ingredients_text", "")
            nutriments = _merge_nutrients(product_info.get("nutriments", {}), custom_nutrients)
            # If text came from database (not OCR), it has full confidence
            effective_ocr_conf = ocr_confidence if custom_text else 1.0
        else:
            is_valid_ean = False
            product_found = False
            raw_text = custom_text
            nutriments = {
                "sugars_100g":       float(custom_nutrients.get("sugars_100g") or 0.0),
                "sodium_100g":       float(custom_nutrients.get("sodium_100g") or 0.0),
                "saturated_fat_100g": float(custom_nutrients.get("saturated_fat_100g") or 0.0),
            }
            product_info = {
                "ean":           ean or "N/A",
                "name":          custom_product.get("name") or "Direct Ingredient Scan",
                "brand":         custom_product.get("brand") or "User Submitted",
                "category":      custom_product.get("category") or "Scanned Product",
                "found":         False,
                "lookup_status": "not_provided"
            }
            effective_ocr_conf = ocr_confidence  # OCR text from frontend

        # --- 2. Module 1: INS Taxonomy Parsing & Ingredient Section Identification ---
        section_info = identify_ingredient_section(raw_text)
        separated_ingredients = clean_and_separate_ingredients(section_info.get("ingredient_text") or raw_text)

        parsed_detail = parse_additives_detailed(raw_text, ocr_confidence=effective_ocr_conf)
        parsed_additives = parsed_detail["parsed_additives"]
        unmapped_tokens = parsed_detail["unmapped_tokens"]
        additive_match_conf = parsed_detail["additive_match_confidence"]

        # --- 3. Module 2: Rule-Based Safety Indicator ---
        scoring_res = compute_rule_based_score(parsed_additives, nutriments)
        final_score = scoring_res["final_score"]
        deductions = scoring_res["score_deductions"]

        # --- 4. Module 3: Counterfactual Engine ---
        counterfactual = generate_counterfactual_explanation(
            parsed_additives=parsed_additives,
            nutriments=nutriments,
            current_score=final_score,
            score_deductions=deductions
        )

        # --- 5. Regulatory Reference Lookup ---
        additive_codes = [a.get("code", "") for a in parsed_additives]
        regulatory_info = get_regulatory_info_batch(additive_codes)

        # --- 6. Module 4: Human-in-the-Loop Audit (4-way confidence) ---
        # Determine barcode_decode_status as a string enum — NOT a float.
        # EAN-13 manual entry provides only pass/fail signal; inventing a
        # decimal confidence value would be scientifically misleading.
        from services.audit import (
            BARCODE_STATUS_VALID,
            BARCODE_STATUS_INVALID,
            BARCODE_STATUS_NOT_PROVIDED,
        )
        if not ean:
            barcode_decode_status = BARCODE_STATUS_NOT_PROVIDED
            # Product identity confidence: neutral baseline 0.5 when no barcode was provided
            product_identity_confidence = 0.5
        elif not is_valid_ean:
            barcode_decode_status = BARCODE_STATUS_INVALID
            # Checksum failure means product identity cannot be established
            product_identity_confidence = 0.0
        else:
            barcode_decode_status = BARCODE_STATUS_VALID
            # Checksum is valid; product identity confidence depends on whether product was actually found
            product_identity_confidence = 1.0 if product_found else 0.0

        audit_res = evaluate_system_audit(
            additive_match_confidence=additive_match_conf,
            unmapped_tokens=unmapped_tokens,
            ocr_confidence=effective_ocr_conf,
            barcode_decode_status=barcode_decode_status,
            product_identity_confidence=product_identity_confidence,
            context_identifier=ean or product_info.get("name", "DirectScan"),
            raw_text=raw_text
        )

        # OCR Safety Gate Evaluation (Quality, Blur & Text Sufficiency)
        ocr_safety = evaluate_ocr_quality_and_safety_gate(
            ocr_confidence=effective_ocr_conf,
            raw_text=raw_text
        )
        audit_res["ocr_safety_gate"] = ocr_safety
        audit_res["ingredient_section_found"] = section_info.get("section_found", False)
        audit_res["separated_ingredients_count"] = len(separated_ingredients)
        audit_res["detected_categories"] = parsed_detail.get("detected_categories", {})
        audit_res["individual_ins_codes"] = parsed_detail.get("individual_ins_codes", [])
        audit_res["ambiguous_detections"] = parsed_detail.get("ambiguous_detections", [])
        audit_res["duplicate_detections"] = parsed_detail.get("duplicate_detections", [])

        # Critical OCR uncertainty gate (< 0.40 or degraded text)
        if not ocr_safety["is_safe_for_decision"]:
            audit_res["ocr_uncertainty_warning"] = True
            for reason in ocr_safety.get("flag_reasons", []):
                if reason not in audit_res["flag_reasons"]:
                    audit_res["flag_reasons"].append(reason)
            audit_res["flagged_for_human_review"] = True
        else:
            audit_res["ocr_uncertainty_warning"] = False

        # --- 6b. Personalised Dietary Preference & Allergen Matching ---
        auth_user = _get_authenticated_user(request)
        user_id = auth_user["id"] if auth_user else None

        active_profile = None
        if auth_user:
            active_profile = get_user_profile(user_id)
        # Check inline dietary_profile override
        req_profile = data.get("dietary_profile")
        if isinstance(req_profile, dict):
            if active_profile:
                active_profile = dict(active_profile)
                active_profile.update(req_profile)
            else:
                active_profile = req_profile

        personal_eval = evaluate_dietary_preferences(
            parsed_additives=parsed_additives,
            raw_text=raw_text,
            dietary_profile=active_profile or {}
        )

        # Safety Gate: Suppress definitive dietary verdict if OCR evidence is insufficient
        if ocr_safety.get("definitive_dietary_score_suppressed"):
            personal_eval["is_provisional"] = True
            personal_eval["definitive_score_suppressed"] = True
            personal_eval["extraction_warning"] = ocr_safety.get("safety_warning")
            personal_eval["recommendation"] = ocr_safety.get("recommendation")
            if not str(personal_eval.get("personal_verdict", "")).startswith("ALLERGEN WARNING"):
                personal_eval["personal_verdict"] = f"PROVISIONAL: {personal_eval.get('personal_verdict')} (Low OCR Confidence)"

        # Persistent Scan History Logging in SQLite
        try:
            conn = get_db_connection()
            conn.execute(
                """
                INSERT INTO analysis_history (
                    user_id, session_id, ean, product_name, raw_text, ocr_confidence,
                    final_score, grade, personal_score, personal_verdict,
                    allergen_alerts, additives_summary, system_audit_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    f"scan_{ean or 'direct'}",
                    ean or "N/A",
                    product_info.get("name", "Scanned Product"),
                    raw_text[:2000] if raw_text else "",
                    effective_ocr_conf,
                    scoring_res["final_score"],
                    scoring_res["grade"],
                    personal_eval.get("personal_score", 100),
                    personal_eval.get("personal_verdict", "N/A"),
                    json.dumps(personal_eval.get("allergen_alerts", [])),
                    json.dumps([a.get("code") for a in parsed_additives]),
                    json.dumps({"flagged": audit_res.get("flagged_for_human_review", False)})
                )
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning("Could not persist analysis history: %s", str(e))

        # --- 7. Build Clean Response ---
        cleaned_additives = []
        for a in parsed_additives:
            code = a.get("code", "")
            reg = regulatory_info.get(code, {})
            cleaned_additives.append({
                "code":                  code,
                "name":                  a.get("name", "Additive"),
                "class":                 a.get("class", "Food Additive"),
                "functional_categories": a.get("functional_categories", [a.get("class", "Food Additive")]),
                "is_color":              bool(a.get("is_color", False)),
                "color_origin":          a.get("color_origin", "not_applicable"),
                "alternative_names":     a.get("alternative_names", []),
                "verified_source":       a.get("verified_source", ""),
                "hazard_level":          a.get("hazard_level", "Moderate"),
                "description":           a.get("description", ""),
                "common_substitute":     a.get("common_substitute", ""),
                "regulatory": {
                    "authority":            reg.get("authority", ""),
                    "source_url":           reg.get("source_url", ""),
                    "fssai_status":         reg.get("fssai_status", "Not checked"),
                    "efsa_adi":             reg.get("efsa_adi", ""),
                    "codex_status":         reg.get("codex_status", ""),
                    "applicable_conditions": reg.get("applicable_conditions", ""),
                    "regulatory_notes":     reg.get("regulatory_notes", ""),
                    "verified":             reg.get("verified", False),
                    "last_verified":        reg.get("last_verified", ""),
                    "source_refs":          reg.get("source_refs", []),
                } if reg else None
            })

        cleaned_deductions = [
            {
                "feature":         d["feature"],
                "type":            d["type"],
                "code":            d.get("code", ""),
                "points_deducted": d["points_deducted"],
                "rationale":       d.get("rationale", ""),
                "rule_source":     d.get("rule_source", ""),
            }
            for d in deductions
        ]

        response_payload = {
            "product": {
                "ean":           product_info.get("ean", ean or "N/A"),
                "name":          product_info.get("name", "Scanned Product"),
                "brand":         product_info.get("brand", ""),
                "category":      product_info.get("category", "Packaged Food"),
                "valid_ean13":   is_valid_ean,
                "found_in_db":   product_found,
                "lookup_status": product_info.get("lookup_status", "not_provided"),
            },
            "parsed_additives": cleaned_additives,
            "unmapped_tokens": unmapped_tokens,
            "safety_indicator": {
                "final_score":         scoring_res["final_score"],
                "grade":               scoring_res["grade"],
                "base_baseline_score": scoring_res["base_baseline_score"],
                "score_deductions":    cleaned_deductions,
                "scoring_method":      scoring_res["scoring_method"],
                "scoring_version":     scoring_res["scoring_version"],
                "scoring_disclaimer":  scoring_res["scoring_disclaimer"],
            },
            # Keep backward-compatible field name
            "safety_scoring": {
                "final_score":         scoring_res["final_score"],
                "grade":               scoring_res["grade"],
                "base_baseline_score": scoring_res["base_baseline_score"],
                "score_deductions":    cleaned_deductions,
            },
            "counterfactual_explanation": counterfactual,
            "system_audit": audit_res,
            "personal_evaluation": personal_eval,
            "detected_categories": parsed_detail.get("detected_categories", {}),
            "individual_ins_codes": parsed_detail.get("individual_ins_codes", []),
            "ambiguous_detections": parsed_detail.get("ambiguous_detections", []),
            "duplicate_detections": parsed_detail.get("duplicate_detections", []),
        }

        return jsonify(response_payload), 200

    except Exception as e:
        logger.exception("Error in /api/v1/analyze: %s", str(e))
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e)
        }), 500


@app.route("/api/v1/product/<barcode>", methods=["GET", "OPTIONS"])
def get_product(barcode):
    """EAN-13 validation and Open Food Facts product lookup."""
    if request.method == "OPTIONS":
        return "", 200

    clean_code = barcode.strip()
    is_valid = validate_ean13(clean_code)
    prod = fetch_product_by_barcode(clean_code)

    return jsonify({
        "valid_ean13": is_valid,
        "product_found": prod.get("found", False),
        "lookup_status": prod.get("lookup_status", "not_found"),
        "product": prod
    })


@app.route("/api/v1/audit/unmapped", methods=["GET", "OPTIONS"])
def audit_queue():
    """Returns unmapped additive records for human review."""
    if request.method == "OPTIONS":
        return "", 200

    status_filter = request.args.get("status")  # optional filter
    records = get_audit_records(status_filter=status_filter)

    return jsonify({
        "total_records": len(records),
        "records": records
    })


@app.route("/api/v1/audit/<record_id>/review", methods=["POST", "OPTIONS"])
def review_audit_record(record_id):
    """
    Reviewer action endpoint.

    POST body:
      {
        "action": "confirm" | "reject" | "correct",
        "corrected_tokens": ["INS 250", "INS 211"],  // required for 'correct'
        "reviewer_note": "Optional explanation"
      }
    """
    if request.method == "OPTIONS":
        return "", 200

    body = request.get_json(silent=True) or {}
    action = body.get("action", "").strip().lower()
    corrected_tokens = body.get("corrected_tokens")
    reviewer_note = body.get("reviewer_note", "")

    if not action:
        return jsonify({"error": "Missing 'action' field"}), 400

    result = update_audit_record(
        record_id=record_id,
        action=action,
        corrected_tokens=corrected_tokens,
        reviewer_note=reviewer_note
    )

    status_code = 200 if result["success"] else 400
    return jsonify(result), status_code


@app.route("/api/v1/audit/stats", methods=["GET", "OPTIONS"])
def audit_stats_endpoint():
    """Returns aggregated statistics on the human-in-the-loop review queue."""
    if request.method == "OPTIONS":
        return "", 200
    stats = get_audit_statistics()
    return jsonify(stats), 200


@app.route("/api/v1/audit/<record_id>", methods=["DELETE", "OPTIONS"])
def delete_audit_record_endpoint(record_id):
    """Deletes an audit queue record by record_id."""
    if request.method == "OPTIONS":
        return "", 200
    deleted = delete_audit_record(record_id)
    if not deleted:
        return jsonify({"error": "Not Found", "message": f"Audit record '{record_id}' not found"}), 404
    return jsonify({"success": True, "message": f"Audit record '{record_id}' deleted"}), 200



# ---------------------------------------------------------------------------
# Image-Based Barcode Detection
# ---------------------------------------------------------------------------

@app.route("/api/v1/barcode/decode", methods=["POST", "OPTIONS"])
def decode_barcode_image_endpoint():
    """Detects and decodes 1D barcode from uploaded image or base64 data."""
    if request.method == "OPTIONS":
        return "", 200

    img_bytes = None
    if "image" in request.files:
        img_bytes = request.files["image"].read()
    else:
        body = request.get_json(silent=True) or {}
        b64_data = body.get("image_base64") or body.get("image")
        if b64_data:
            if "," in b64_data:
                b64_data = b64_data.split(",", 1)[1]
            try:
                img_bytes = base64.b64decode(b64_data)
            except Exception:
                return jsonify({"error": "Invalid base64 image data"}), 400

    if not img_bytes:
        return jsonify({
            "error": "No image provided. Send file in 'image' field or base64 string in 'image_base64'."
        }), 400

    result = decode_barcode_from_image(img_bytes)
    return jsonify(result), 200


# ---------------------------------------------------------------------------
# User Authentication Endpoints
# ---------------------------------------------------------------------------

@app.route("/api/v1/auth/register", methods=["POST", "OPTIONS"])
def auth_register():
    """Registers a new user account."""
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json(silent=True) or {}
    ok, user_data, err = register_user(
        data.get("username", ""),
        data.get("email", ""),
        data.get("password", "")
    )
    if not ok:
        return jsonify({"error": "Registration failed", "message": err}), 400
    return jsonify({"message": "User registered successfully", "user": user_data}), 201


@app.route("/api/v1/auth/login", methods=["POST", "OPTIONS"])
def auth_login():
    """Authenticates user credentials and issues session token."""
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json(silent=True) or {}
    identifier = data.get("identifier") or data.get("username") or data.get("email") or ""
    password = data.get("password") or ""
    ok, auth_payload, err = authenticate_user(identifier, password)
    if not ok:
        return jsonify({"error": "Authentication failed", "message": err}), 401
    return jsonify(auth_payload), 200


@app.route("/api/v1/auth/logout", methods=["POST", "OPTIONS"])
def auth_logout():
    """Revokes current session token."""
    if request.method == "OPTIONS":
        return "", 200
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()
    if token:
        revoke_token(token)
    return jsonify({"message": "Successfully logged out"}), 200


@app.route("/api/v1/auth/me", methods=["GET", "OPTIONS"])
def auth_me():
    """Returns current user and active dietary profile."""
    if request.method == "OPTIONS":
        return "", 200
    user = _get_authenticated_user(request)
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401
    profile = get_user_profile(user["id"])
    return jsonify({"user": user, "dietary_profile": profile}), 200


# ---------------------------------------------------------------------------
# Dietary Profile & User Preferences Endpoints (Phase 5)
# ---------------------------------------------------------------------------

@app.route("/api/v1/profile", methods=["GET", "POST", "PUT", "OPTIONS"])
def user_profile_endpoint():
    """Retrieves or updates the authenticated user's dietary profile."""
    if request.method == "OPTIONS":
        return "", 200
    user = _get_authenticated_user(request)
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401

    if request.method == "GET":
        profile = get_user_profile(user["id"])
        return jsonify(profile), 200

    # POST or PUT — update full profile
    data = request.get_json(silent=True) or {}
    ok, updated_profile, err = update_user_profile(user["id"], data)
    if not ok:
        return jsonify({"error": "Update failed", "message": err}), 400
    return jsonify({"message": "Profile updated successfully", "dietary_profile": updated_profile}), 200


@app.route("/api/v1/profile/preferences", methods=["GET", "OPTIONS"])
def user_preferences_endpoint():
    """Retrieves granular dietary preferences for the authenticated user."""
    if request.method == "OPTIONS":
        return "", 200
    user = _get_authenticated_user(request)
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401

    prefs = get_user_preferences(user["id"])
    return jsonify(prefs), 200


@app.route("/api/v1/profile/preferences/categories", methods=["POST", "OPTIONS"])
def update_profile_categories_endpoint():
    """Updates additive category avoidance flags (e.g. avoid_synthetic_colors, avoid_preservatives)."""
    if request.method == "OPTIONS":
        return "", 200
    user = _get_authenticated_user(request)
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401

    data = request.get_json(silent=True) or {}
    ok, updated_profile, err = update_category_preferences(user["id"], data)
    if not ok:
        return jsonify({"error": "Category update failed", "message": err}), 400

    return jsonify({
        "message": "Category preferences updated successfully",
        "dietary_profile": updated_profile
    }), 200


@app.route("/api/v1/profile/preferences/additives", methods=["POST", "OPTIONS"])
def update_profile_additives_endpoint():
    """Adds or removes individual INS codes from the user's avoidance or caution list."""
    if request.method == "OPTIONS":
        return "", 200
    user = _get_authenticated_user(request)
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401

    data = request.get_json(silent=True) or {}
    action = data.get("action", "add")
    code = data.get("code") or data.get("ins_code", "")
    pref_type = data.get("type") or data.get("preference_type", "avoid")

    if not code:
        return jsonify({"error": "Missing required field: 'code' or 'ins_code'"}), 400

    ok, updated_profile, err = manage_additive_preference(
        user_id=user["id"],
        action=action,
        code=code,
        pref_type=pref_type
    )
    if not ok:
        return jsonify({"error": "Additive preference update failed", "message": err}), 400

    return jsonify({
        "message": f"Additive '{code}' successfully {'added to' if action == 'add' else 'removed from'} {pref_type} list",
        "dietary_profile": updated_profile
    }), 200


@app.route("/api/v1/profile/allergies", methods=["POST", "OPTIONS"])
def update_profile_allergies_endpoint():
    """Adds, removes, or sets user allergen flags."""
    if request.method == "OPTIONS":
        return "", 200
    user = _get_authenticated_user(request)
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401

    data = request.get_json(silent=True) or {}
    action = data.get("action", "set")
    allergens = data.get("allergens") or data.get("allergen", [])

    ok, updated_profile, err = manage_allergy_preferences(
        user_id=user["id"],
        action=action,
        allergens_input=allergens
    )
    if not ok:
        return jsonify({"error": "Allergy update failed", "message": err}), 400

    return jsonify({
        "message": f"Allergen preferences updated successfully",
        "dietary_profile": updated_profile
    }), 200


@app.route("/api/v1/profile/presets", methods=["GET", "OPTIONS"])
def get_profile_presets_endpoint():
    """Returns standard dietary presets (clean_label, vegan, vegetarian, etc.)."""
    if request.method == "OPTIONS":
        return "", 200
    return jsonify({"presets": DIETARY_PRESETS}), 200


@app.route("/api/v1/preferences/evaluate", methods=["POST", "OPTIONS"])
def evaluate_preferences_endpoint():
    """
    Evaluates raw ingredient text and detected additives against user dietary profile.
    Can be called by authenticated users or with an explicit dietary_profile in payload.
    """
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}
    raw_text = data.get("raw_text") or data.get("text") or ""
    parsed_additives = data.get("parsed_additives")

    if parsed_additives is None:
        parsed_additives, _, _ = parse_additives_and_audit(raw_text)

    auth_user = _get_authenticated_user(request)
    user_id = auth_user["id"] if auth_user else None

    active_profile = None
    if auth_user:
        active_profile = get_user_profile(user_id)

    req_profile = data.get("dietary_profile")
    if isinstance(req_profile, dict):
        if active_profile:
            active_profile = dict(active_profile)
            active_profile.update(req_profile)
        else:
            active_profile = req_profile

    result = evaluate_dietary_preferences(
        parsed_additives=parsed_additives,
        raw_text=raw_text,
        dietary_profile=active_profile or {}
    )

    return jsonify({
        "status": "success",
        "personal_evaluation": result
    }), 200


# ---------------------------------------------------------------------------
# OCR Image Preprocessing & Ingredient Section Extraction Endpoints
# ---------------------------------------------------------------------------

@app.route("/api/v1/ocr/preprocess", methods=["POST", "OPTIONS"])
def ocr_preprocess_endpoint():
    """
    Computer Vision Preprocessing Endpoint:
    Assesses image blur (Laplacian variance), lighting uniformity, and dimensions.
    Applies CLAHE contrast enhancement and unsharp masking.
    Accepts: multipart/form-data with 'image' OR JSON { 'image_base64': '...' }
    """
    if request.method == "OPTIONS":
        return "", 200

    img_bytes = None
    if "image" in request.files:
        img_bytes = request.files["image"].read()
    else:
        body = request.get_json(silent=True) or {}
        img_bytes = body.get("image_base64") or body.get("image")

    if not img_bytes:
        return jsonify({"error": "Bad Request", "message": "No image data provided"}), 400

    enhanced_img, metrics = preprocess_label_image(img_bytes)
    if enhanced_img is None:
        return jsonify({"error": "Processing Error", "message": metrics.get("error", "Failed to preprocess image")}), 400

    # Encode enhanced image as JPEG base64 for preview/debug
    import cv2
    _, buffer = cv2.imencode(".jpg", enhanced_img)
    enhanced_base64 = base64.b64encode(buffer).decode("utf-8")

    return jsonify({
        "status": "success",
        "quality_metrics": metrics,
        "enhanced_image_base64": f"data:image/jpeg;base64,{enhanced_base64}"
    }), 200


@app.route("/api/v1/ocr/extract-section", methods=["POST", "OPTIONS"])
def ocr_extract_section_endpoint():
    """
    Extracts and isolates the INGREDIENTS section from whole-package text or image,
    performs token separation into discrete clauses, and assesses OCR quality.
    """
    if request.method == "OPTIONS":
        return "", 200

    body = request.get_json(silent=True) or {}
    text = body.get("text") or body.get("raw_text") or ""
    ocr_confidence = float(body.get("ocr_confidence", 1.0))

    section_info = identify_ingredient_section(text)
    separated_ingredients = clean_and_separate_ingredients(section_info.get("ingredient_text") or text)
    ocr_safety = evaluate_ocr_quality_and_safety_gate(ocr_confidence, text)

    return jsonify({
        "status": "success",
        "section_info": section_info,
        "separated_ingredients": separated_ingredients,
        "separated_count": len(separated_ingredients),
        "ocr_safety": ocr_safety
    }), 200


# ---------------------------------------------------------------------------
# INS Detection & Additive Classification Endpoint
# ---------------------------------------------------------------------------

@app.route("/api/v1/parser/parse", methods=["POST", "OPTIONS"])
def parser_parse_endpoint():
    """
    Direct INS Detection & Additive Classification Endpoint:
    Extracts INS numbers, E-numbers, parenthetical category numbers, official names,
    and alternative synonyms. Groups into functional categories, isolates individual codes,
    handles duplicate mentions, and reports unmapped or ambiguous terms.
    """
    if request.method == "OPTIONS":
        return "", 200

    body = request.get_json(silent=True) or {}
    text = body.get("text") or body.get("raw_text") or ""
    ocr_confidence = float(body.get("ocr_confidence", 1.0))

    result = parse_additives_detailed(text, ocr_confidence=ocr_confidence)
    return jsonify({
        "status": "success",
        "result": result
    }), 200


# ---------------------------------------------------------------------------
# User History Endpoints (Phase 10: History & Audit Management)
# ---------------------------------------------------------------------------

@app.route("/api/v1/history", methods=["GET", "DELETE", "OPTIONS"])
def user_history_endpoint():
    """
    GET: Retrieves authenticated user scan history with search, verdict, and allergen filtering.
    DELETE: Clears all history records for the authenticated user.
    """
    if request.method == "OPTIONS":
        return "", 200
    user = _get_authenticated_user(request)
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401

    if request.method == "DELETE":
        deleted_count = clear_user_history(user["id"])
        return jsonify({
            "success": True,
            "message": f"Successfully cleared {deleted_count} scan records",
            "deleted_count": deleted_count
        }), 200

    try:
        limit = min(100, max(1, int(request.args.get("limit", 50))))
        offset = max(0, int(request.args.get("offset", 0)))
    except (ValueError, TypeError):
        limit, offset = 50, 0

    search = request.args.get("search")
    verdict = request.args.get("verdict")
    raw_has_allergens = request.args.get("has_allergens")
    has_allergens = None
    if raw_has_allergens is not None:
        has_allergens = raw_has_allergens.lower() in ("true", "1", "yes")

    history = get_user_history(
        user_id=user["id"],
        limit=limit,
        offset=offset,
        search=search,
        verdict=verdict,
        has_allergens=has_allergens
    )
    total_count = count_user_history(
        user_id=user["id"],
        search=search,
        verdict=verdict,
        has_allergens=has_allergens
    )

    return jsonify({
        "history": history,
        "count": len(history),
        "total_count": total_count,
        "limit": limit,
        "offset": offset
    }), 200


@app.route("/api/v1/history/<int:record_id>", methods=["GET", "DELETE", "OPTIONS"])
def single_history_record_endpoint(record_id):
    """
    GET: Retrieves complete details of a specific scan history record.
    DELETE: Removes a single scan history record.
    """
    if request.method == "OPTIONS":
        return "", 200
    user = _get_authenticated_user(request)
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401

    if request.method == "DELETE":
        deleted = delete_history_record(user["id"], record_id)
        if not deleted:
            return jsonify({"error": "Not Found", "message": f"Record {record_id} not found"}), 404
        return jsonify({"success": True, "message": f"Record {record_id} deleted successfully"}), 200

    record = get_history_record_by_id(user["id"], record_id)
    if not record:
        return jsonify({"error": "Not Found", "message": f"Record {record_id} not found"}), 404

    return jsonify({"record": record}), 200


@app.route("/api/v1/history/export", methods=["GET", "OPTIONS"])
def export_history_endpoint():
    """Exports authenticated user scan history in JSON or CSV format."""
    if request.method == "OPTIONS":
        return "", 200
    user = _get_authenticated_user(request)
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401

    export_format = request.args.get("format", "json").lower()
    data_str, mime_type = export_user_history(user["id"], export_format=export_format)

    from flask import Response
    ext = "csv" if export_format == "csv" else "json"
    filename = f"scan_history_{user['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"

    return Response(
        data_str,
        mimetype=mime_type,
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )



# ---------------------------------------------------------------------------
# Legacy backward-compatible endpoint
# ---------------------------------------------------------------------------

@app.route("/analyze", methods=["POST", "OPTIONS"])
def analyze_legacy():
    """Backward-compatible endpoint for legacy frontend clients."""
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    parsed_additives, unmapped_tokens, additive_conf = parse_additives_and_audit(text)
    scoring_res = compute_rule_based_score(parsed_additives, {})

    legacy_additives = []
    for a in parsed_additives:
        legacy_additives.append({
            "code":              a.get("code", "").replace("INS ", ""),
            "name":              a.get("name", ""),
            "category":          a.get("class", ""),
            "description":       a.get("class", ""),
            "risk_score":        int(a.get("hazard_weight", 0.5) * 100),
            "high_risk_flag":    a.get("hazard_level") in ["High", "Severe"],
            "risk_score_reason": f"Hazard level: {a.get('hazard_level')}"
        })

    legacy_risk_score = round(max(0.0, 100.0 - scoring_res["final_score"]), 1)
    legacy_level = "High" if legacy_risk_score >= 50 else ("Moderate" if legacy_risk_score >= 25 else "Low")

    return jsonify({
        "detected_additives": legacy_additives,
        "overall_risk_score": legacy_risk_score,
        "overall_risk_level": legacy_level,
        "overall_risk_reason": f"Rule-based indicator from {len(parsed_additives)} additives.",
        "xai_scoring": scoring_res  # New XAI payload for upgraded clients
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5005))
    app.run(host="0.0.0.0", port=port, debug=True)
