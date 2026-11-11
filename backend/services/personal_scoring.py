"""
Module: Personalised Scoring & Dietary Analysis Orchestrator
============================================================
Coordinates between the universal baseline safety indicator
(compute_rule_based_score) and user-specific dietary preferences
(evaluate_dietary_preferences).

Provides unified analysis reporting:
  - Universal Safety Indicator: Public health baseline (INS hazard weights & nutrients)
  - Personalised Suitability: Individual profile matching (allergens, preferences, custom INS)
  - Independent Allergen Alerts: Zero-compromise critical warnings
  - Persistent Scan History Logging
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from services.scoring_engine import compute_rule_based_score
from services.preference_engine import evaluate_dietary_preferences
from models.database import get_db_connection

logger = logging.getLogger(__name__)


def compute_comprehensive_analysis(
    parsed_additives: List[Dict[str, Any]],
    nutriments: Dict[str, Any],
    raw_text: str,
    dietary_profile: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
    ean: str = "",
    product_name: str = "",
    ocr_confidence: float = 1.0,
    system_audit_summary: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes both universal baseline safety score and personalised dietary score,
    returning a structured, decoupled analysis payload.
    Logs record to SQLite analysis_history when user_id is provided or for history tracking.
    """
    # 1. Baseline Universal Safety Score
    baseline_result = compute_rule_based_score(parsed_additives, nutriments)

    # 2. Personalised Dietary Assessment
    pref_result = evaluate_dietary_preferences(
        parsed_additives=parsed_additives,
        raw_text=raw_text,
        dietary_profile=dietary_profile or {}
    )

    # 3. Log into analysis_history in SQLite if needed
    history_record_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO analysis_history (
                user_id, session_id, ean, product_name, raw_text, ocr_confidence,
                final_score, grade, personal_score, personal_verdict,
                allergen_alerts, additives_summary, system_audit_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                f"scan_{ean or 'text'}",
                ean or "N/A",
                product_name or "Scanned Product",
                raw_text[:2000] if raw_text else "",
                ocr_confidence,
                baseline_result.get("final_score", 100),
                baseline_result.get("grade", "A"),
                pref_result.get("personal_score", 100),
                pref_result.get("personal_verdict", "N/A"),
                json.dumps(pref_result.get("allergen_alerts", [])),
                json.dumps([a.get("code") for a in parsed_additives]),
                json.dumps(system_audit_summary or {})
            )
        )
        conn.commit()
        history_record_id = cursor.lastrowid
        conn.close()
    except Exception as e:
        logger.warning("Failed to record scan in analysis_history: %s", str(e))

    return {
        "safety_indicator": baseline_result,
        "personal_evaluation": pref_result,
        "history_record_id": history_record_id
    }


def get_user_history(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    verdict: Optional[str] = None,
    has_allergens: Optional[bool] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves past scan history records for a registered user with optional
    search, verdict filtering, and allergen filtering.
    """
    conn = get_db_connection()
    try:
        query = """
            SELECT id, user_id, session_id, ean, product_name, raw_text, ocr_confidence,
                   final_score, grade, personal_score, personal_verdict,
                   allergen_alerts, additives_summary, system_audit_summary, scanned_at
            FROM analysis_history
            WHERE user_id = ?
        """
        params: List[Any] = [user_id]

        if search and search.strip():
            term = f"%{search.strip()}%"
            query += " AND (product_name LIKE ? OR ean LIKE ? OR raw_text LIKE ?)"
            params.extend([term, term, term])

        if verdict and verdict.strip() and verdict.lower() != "all":
            query += " AND LOWER(personal_verdict) LIKE ?"
            params.append(f"%{verdict.strip().lower()}%")

        if has_allergens is True:
            query += " AND allergen_alerts IS NOT NULL AND allergen_alerts != '[]' AND allergen_alerts != ''"
        elif has_allergens is False:
            query += " AND (allergen_alerts IS NULL OR allergen_alerts = '[]' OR allergen_alerts = '')"

        query += " ORDER BY scanned_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, tuple(params)).fetchall()

        history = []
        for r in rows:
            allergens = json.loads(r["allergen_alerts"]) if r["allergen_alerts"] else []
            additives = json.loads(r["additives_summary"]) if r["additives_summary"] else []
            audit_summary = json.loads(r["system_audit_summary"]) if r["system_audit_summary"] else {}
            history.append({
                "id": r["id"],
                "session_id": r["session_id"],
                "ean": r["ean"],
                "product_name": r["product_name"],
                "ocr_confidence": r["ocr_confidence"],
                "final_score": r["final_score"],
                "grade": r["grade"],
                "personal_score": r["personal_score"],
                "personal_verdict": r["personal_verdict"],
                "allergen_alerts": allergens,
                "additives_count": len(additives),
                "additives": additives,
                "audit_summary": audit_summary,
                "raw_text": r["raw_text"],
                "scanned_at": r["scanned_at"]
            })
        return history
    except Exception as e:
        logger.error("Error fetching user history: %s", str(e))
        return []
    finally:
        conn.close()


def count_user_history(
    user_id: int,
    search: Optional[str] = None,
    verdict: Optional[str] = None,
    has_allergens: Optional[bool] = None
) -> int:
    """
    Returns the total count of history records matching given filters.
    """
    conn = get_db_connection()
    try:
        query = "SELECT COUNT(*) as count FROM analysis_history WHERE user_id = ?"
        params: List[Any] = [user_id]

        if search and search.strip():
            term = f"%{search.strip()}%"
            query += " AND (product_name LIKE ? OR ean LIKE ? OR raw_text LIKE ?)"
            params.extend([term, term, term])

        if verdict and verdict.strip() and verdict.lower() != "all":
            query += " AND LOWER(personal_verdict) LIKE ?"
            params.append(f"%{verdict.strip().lower()}%")

        if has_allergens is True:
            query += " AND allergen_alerts IS NOT NULL AND allergen_alerts != '[]' AND allergen_alerts != ''"
        elif has_allergens is False:
            query += " AND (allergen_alerts IS NULL OR allergen_alerts = '[]' OR allergen_alerts = '')"

        row = conn.execute(query, tuple(params)).fetchone()
        return int(row["count"]) if row else 0
    except Exception as e:
        logger.error("Error counting user history: %s", str(e))
        return 0
    finally:
        conn.close()


def get_history_record_by_id(user_id: int, record_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves full details of a specific scan history record for an authenticated user.
    """
    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT id, user_id, session_id, ean, product_name, raw_text, ocr_confidence,
                   final_score, grade, personal_score, personal_verdict,
                   allergen_alerts, additives_summary, system_audit_summary, scanned_at
            FROM analysis_history
            WHERE user_id = ? AND id = ?
            """,
            (user_id, record_id)
        ).fetchone()

        if not row:
            return None

        allergens = json.loads(row["allergen_alerts"]) if row["allergen_alerts"] else []
        additives = json.loads(row["additives_summary"]) if row["additives_summary"] else []
        audit_summary = json.loads(row["system_audit_summary"]) if row["system_audit_summary"] else {}

        return {
            "id": row["id"],
            "session_id": row["session_id"],
            "ean": row["ean"],
            "product_name": row["product_name"],
            "raw_text": row["raw_text"],
            "ocr_confidence": row["ocr_confidence"],
            "final_score": row["final_score"],
            "grade": row["grade"],
            "personal_score": row["personal_score"],
            "personal_verdict": row["personal_verdict"],
            "allergen_alerts": allergens,
            "additives_count": len(additives),
            "additives": additives,
            "system_audit_summary": audit_summary,
            "scanned_at": row["scanned_at"]
        }
    except Exception as e:
        logger.error("Error retrieving history record %s: %s", record_id, str(e))
        return None
    finally:
        conn.close()


def delete_history_record(user_id: int, record_id: int) -> bool:
    """
    Deletes an individual scan record belonging to the authenticated user.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM analysis_history WHERE user_id = ? AND id = ?",
            (user_id, record_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error("Error deleting history record %s: %s", record_id, str(e))
        return False
    finally:
        conn.close()


def clear_user_history(user_id: int) -> int:
    """
    Deletes all scan history records for an authenticated user.
    Returns count of deleted records.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analysis_history WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        logger.error("Error clearing user history for user %s: %s", user_id, str(e))
        return 0
    finally:
        conn.close()


def export_user_history(user_id: int, export_format: str = "json") -> Tuple[str, str]:
    """
    Exports user scan history in JSON or CSV format.
    Returns (data_string, mime_type).
    """
    history = get_user_history(user_id, limit=1000, offset=0)
    fmt = (export_format or "json").lower()

    if fmt == "csv":
        import io
        import csv

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "Scanned At", "Product Name", "EAN Barcode", "Safety Score", "Grade",
            "Personal Score", "Personal Verdict", "Allergens Count", "Allergens Detected",
            "Additives Count", "Additives Codes", "OCR Confidence"
        ])
        for r in history:
            allergens_str = "; ".join(
                [f"{a.get('allergen', '')}: {a.get('matched_term', '')}" for a in r.get("allergen_alerts", [])]
            )
            additives_str = ", ".join(r.get("additives", []))
            writer.writerow([
                r["id"],
                r["scanned_at"],
                r["product_name"],
                r["ean"],
                r["final_score"],
                r["grade"],
                r["personal_score"],
                r["personal_verdict"],
                len(r.get("allergen_alerts", [])),
                allergens_str,
                r.get("additives_count", 0),
                additives_str,
                r["ocr_confidence"]
            ])
        return output.getvalue(), "text/csv"

    # Default to formatted JSON
    return json.dumps({"exported_at": str(datetime.now()), "user_id": user_id, "history": history}, indent=2), "application/json"

