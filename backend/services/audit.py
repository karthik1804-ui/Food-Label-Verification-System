"""
Module 4: Human-in-the-Loop (HITL) Audit Protocol — v2.0 (refined)
=====================================================================
Monitors additive parsing confidence, logs unmapped additive strings,
and supports reviewer actions (confirm / reject / correct).

Confidence design:
  - ocr_confidence: float 0.0-1.0 from Tesseract word-level scores
  - additive_match_confidence: float 0.0-1.0 from taxonomy match ratio
  - barcode_decode_status: string enum (not an invented float)
      Values: "valid_ean13" | "invalid_checksum" | "not_provided" | "lookup_failed"
      Rationale: EAN-13 manual entry provides no richer signal than pass/fail.
      A float confidence would be invented. We report the actual status instead.
  - product_identity_confidence: float 0.0-1.0
      Currently 1.0 if EAN valid + product found, 0.5 if no EAN, 0.0 if lookup failed.
      Stage 5 (multimodal verification) will refine this with OCR vs. database comparison.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

AUDIT_LOG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "unmapped_additives.json"
)

# Configurable confidence thresholds
ADDITIVE_MATCH_CONFIDENCE_THRESHOLD = 0.75
OCR_CONFIDENCE_THRESHOLD = 0.70

# Valid reviewer actions
VALID_REVIEW_ACTIONS = {"confirm", "reject", "correct"}

# Barcode status enum values — no invented floats
BARCODE_STATUS_VALID       = "valid_ean13"
BARCODE_STATUS_INVALID     = "invalid_checksum"
BARCODE_STATUS_NOT_PROVIDED = "not_provided"
BARCODE_STATUS_LOOKUP_FAILED = "lookup_failed"


def evaluate_system_audit(
    additive_match_confidence: float,
    unmapped_tokens: List[str],
    ocr_confidence: float = 1.0,
    barcode_decode_status: str = BARCODE_STATUS_NOT_PROVIDED,
    product_identity_confidence: float = 0.5,
    context_identifier: str = "",
    raw_text: str = ""
) -> Dict[str, Any]:
    """
    Evaluates system audit metrics and returns structured confidence report.

    Args:
        additive_match_confidence: Fraction of detected tokens resolved in taxonomy (0.0-1.0).
        unmapped_tokens: List of tokens not found in taxonomy.
        ocr_confidence: Mean Tesseract word-level confidence (0.0-1.0).
                        Pass 1.0 when text came from database, not OCR.
        barcode_decode_status: String status of EAN-13 decode attempt.
                        One of: "valid_ean13", "invalid_checksum", "not_provided",
                        "lookup_failed".
                        NOT a float — EAN-13 manual entry provides no richer signal
                        than pass/fail, so an invented float would be misleading.
        product_identity_confidence: Confidence product matches barcode record (0.0-1.0).
                        1.0 = valid EAN + product found in OFF. 0.5 = no EAN provided.
                        0.0 = barcode lookup failed. Stage 5 will add OCR comparison.
        context_identifier: Product EAN or scan name for audit log.
        raw_text: Raw ingredient text snippet for audit log (truncated to 300 chars).

    Returns:
        {
          "confidence": {
            "ocr_confidence": float,                  # Tesseract-derived
            "additive_match_confidence": float,       # Taxonomy match ratio
            "barcode_decode_status": str,             # String status, not a float
            "product_identity_confidence": float      # Based on EAN lookup outcome
          },
          "flagged_for_human_review": bool,
          "flag_reasons": list[str],
          "parser_confidence": float                  # Backward-compat alias
        }
    """
    flag_reasons: List[str] = []

    # Trigger 1: Unmapped additive tokens
    if unmapped_tokens:
        flag_reasons.append(
            "{n} unrecognised additive token(s): {tokens}{more}".format(
                n=len(unmapped_tokens),
                tokens=", ".join(unmapped_tokens[:3]),
                more=" ..." if len(unmapped_tokens) > 3 else ""
            )
        )

    # Trigger 2: Low additive matching confidence
    if additive_match_confidence < ADDITIVE_MATCH_CONFIDENCE_THRESHOLD:
        flag_reasons.append(
            "Low additive matching confidence: {pct:.0%} (threshold {thr:.0%})".format(
                pct=additive_match_confidence,
                thr=ADDITIVE_MATCH_CONFIDENCE_THRESHOLD
            )
        )

    # Trigger 3: Low OCR confidence (only meaningful when text came from OCR)
    if ocr_confidence < 1.0 and ocr_confidence < OCR_CONFIDENCE_THRESHOLD:
        flag_reasons.append(
            "Low OCR text confidence: {pct:.0%} (threshold {thr:.0%})".format(
                pct=ocr_confidence,
                thr=OCR_CONFIDENCE_THRESHOLD
            )
        )

    # Trigger 4: Invalid or failed barcode or missing product identity
    if barcode_decode_status in (BARCODE_STATUS_INVALID, BARCODE_STATUS_LOOKUP_FAILED):
        flag_reasons.append(
            "Barcode issue: {status}".format(status=barcode_decode_status)
        )
    elif product_identity_confidence == 0.0 and barcode_decode_status == BARCODE_STATUS_VALID:
        flag_reasons.append(
            "Product identity not found in database for valid EAN barcode"
        )

    is_flagged = len(flag_reasons) > 0

    # Persist flagged records (with deduplication)
    if is_flagged and unmapped_tokens:
        _append_to_audit_log_deduplicated(
            context_identifier=context_identifier,
            unmapped_tokens=unmapped_tokens,
            raw_text=raw_text,
            additive_match_confidence=additive_match_confidence,
            ocr_confidence=ocr_confidence,
            flag_reasons=flag_reasons
        )

    return {
        "confidence": {
            "ocr_confidence": round(float(ocr_confidence), 3),
            "additive_match_confidence": round(float(additive_match_confidence), 3),
            "barcode_decode_status": barcode_decode_status,
            "product_identity_confidence": round(float(product_identity_confidence), 3),
        },
        "flagged_for_human_review": is_flagged,
        "flag_reasons": flag_reasons,
        # Backward-compatible single value (additive match confidence)
        "parser_confidence": round(float(additive_match_confidence), 2),
    }


def _append_to_audit_log_deduplicated(
    context_identifier: str,
    unmapped_tokens: List[str],
    raw_text: str,
    additive_match_confidence: float,
    ocr_confidence: float,
    flag_reasons: List[str]
) -> None:
    """
    Appends an audit record to unmapped_additives.json.
    Deduplicates: skips if the exact same (context_identifier, unmapped_tokens set)
    pair already exists with status PENDING_EXPERT_REVIEW.
    """
    try:
        entries = _load_audit_records()
        token_set = set(unmapped_tokens)

        for existing in entries:
            if (
                existing.get("context_identifier") == context_identifier
                and set(existing.get("unmapped_tokens", [])) == token_set
                and existing.get("audit_status") == "PENDING_EXPERT_REVIEW"
            ):
                logger.debug(
                    "Skipping duplicate audit entry for context=%s", context_identifier
                )
                return

        record = {
            "id": "audit_{ts}".format(
                ts=int(datetime.now(timezone.utc).timestamp() * 1000)
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context_identifier": context_identifier,
            "unmapped_tokens": unmapped_tokens,
            "raw_text_snippet": raw_text[:300] if raw_text else "",
            "additive_match_confidence": round(float(additive_match_confidence), 3),
            "ocr_confidence": round(float(ocr_confidence), 3),
            "flag_reasons": flag_reasons,
            "audit_status": "PENDING_EXPERT_REVIEW",
            "review_history": []
        }

        entries.append(record)
        _save_audit_records(entries)

        logger.info(
            "Audit record logged: context=%s, unmapped=%s",
            context_identifier, unmapped_tokens
        )

    except Exception as e:
        logger.error("Failed to write audit record: %s", str(e))


def update_audit_record(
    record_id: str,
    action: str,
    corrected_tokens: Optional[List[str]] = None,
    reviewer_note: str = ""
) -> Dict[str, Any]:
    """
    Updates an audit record with a reviewer's decision.
    Changes are persisted immediately to unmapped_additives.json.

    Args:
        record_id: The 'id' field of the record to update.
        action: One of 'confirm', 'reject', 'correct'.
            - confirm: The unmapped string is genuinely not a food additive.
            - reject: The detection was a false positive.
            - correct: Provide the correct INS code(s) for the unmapped token.
        corrected_tokens: List of correct INS codes. Required when action='correct'.
        reviewer_note: Free-text explanation from the reviewer.

    Returns:
        {"success": bool, "message": str}
    """
    if action not in VALID_REVIEW_ACTIONS:
        return {
            "success": False,
            "message": "Invalid action '{a}'. Must be one of: {valid}".format(
                a=action, valid=sorted(VALID_REVIEW_ACTIONS)
            )
        }

    if action == "correct" and not corrected_tokens:
        return {
            "success": False,
            "message": "corrected_tokens is required when action is 'correct'"
        }

    try:
        entries = _load_audit_records()
        target_idx = next(
            (i for i, e in enumerate(entries) if e.get("id") == record_id),
            None
        )

        if target_idx is None:
            return {"success": False, "message": "Record ID '{id}' not found".format(id=record_id)}

        status_map = {
            "confirm": "CONFIRMED_BY_REVIEWER",
            "reject":  "REJECTED_BY_REVIEWER",
            "correct": "CORRECTED_BY_REVIEWER",
        }

        review_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "reviewer_note": reviewer_note,
        }
        if action == "correct":
            review_event["corrected_tokens"] = corrected_tokens
            entries[target_idx]["corrected_tokens"] = corrected_tokens

        entries[target_idx]["audit_status"] = status_map[action]
        if "review_history" not in entries[target_idx]:
            entries[target_idx]["review_history"] = []
        entries[target_idx]["review_history"].append(review_event)

        _save_audit_records(entries)

        return {
            "success": True,
            "message": "Record {id} updated to {status}".format(
                id=record_id, status=status_map[action]
            )
        }

    except Exception as e:
        logger.error("Failed to update audit record %s: %s", record_id, str(e))
        return {"success": False, "message": str(e)}


def get_audit_records(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns audit records, optionally filtered by status.

    Args:
        status_filter: Optional. Returns only records matching this status.
                       Supports standard constants like 'PENDING_EXPERT_REVIEW',
                       or shorthand filters like 'pending', 'confirmed', 'rejected', 'corrected'.
    """
    records = _load_audit_records()
    if not status_filter or status_filter.lower() == "all":
        return records

    sf = status_filter.strip().upper()
    shorthand_map = {
        "PENDING": "PENDING_EXPERT_REVIEW",
        "CONFIRMED": "CONFIRMED_BY_REVIEWER",
        "REJECTED": "REJECTED_BY_REVIEWER",
        "CORRECTED": "CORRECTED_BY_REVIEWER"
    }
    normalized_status = shorthand_map.get(sf, sf)
    return [r for r in records if r.get("audit_status") == normalized_status or r.get("audit_status") == status_filter]


def get_audit_statistics() -> Dict[str, Any]:
    """
    Returns aggregated counts and metrics across the audit queue.
    """
    records = _load_audit_records()
    total = len(records)
    pending = sum(1 for r in records if r.get("audit_status") == "PENDING_EXPERT_REVIEW")
    confirmed = sum(1 for r in records if r.get("audit_status") == "CONFIRMED_BY_REVIEWER")
    rejected = sum(1 for r in records if r.get("audit_status") == "REJECTED_BY_REVIEWER")
    corrected = sum(1 for r in records if r.get("audit_status") == "CORRECTED_BY_REVIEWER")

    all_unmapped = set()
    for r in records:
        for t in r.get("unmapped_tokens", []):
            all_unmapped.add(t)

    return {
        "total_records": total,
        "pending_count": pending,
        "confirmed_count": confirmed,
        "rejected_count": rejected,
        "corrected_count": corrected,
        "unique_unmapped_tokens": sorted(list(all_unmapped)),
        "unique_unmapped_count": len(all_unmapped)
    }


def delete_audit_record(record_id: str) -> bool:
    """
    Removes an audit record by ID from the persistent log.
    """
    entries = _load_audit_records()
    initial_len = len(entries)
    entries = [e for e in entries if e.get("id") != record_id]
    if len(entries) < initial_len:
        _save_audit_records(entries)
        return True
    return False



def _load_audit_records() -> List[Dict[str, Any]]:
    """Loads and returns all audit records from the JSON log file."""
    if not os.path.exists(AUDIT_LOG_PATH):
        return []
    try:
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not load audit records: %s", e)
        return []


def _save_audit_records(entries: List[Dict[str, Any]]) -> None:
    """Writes all audit records to the JSON log file."""
    with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
