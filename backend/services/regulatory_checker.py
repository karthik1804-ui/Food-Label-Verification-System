"""
Regulatory Reference Checker — v2.0
=====================================
Looks up regulatory information for food additives from the local
regulatory_references.json database.

Sources referenced in regulatory_references.json:
  - FSSAI (Food Safety and Standards Authority of India)
  - EFSA (European Food Safety Authority)
  - Codex Alimentarius (international food standards)
  - FDA (US Food and Drug Administration)

IMPORTANT: This module provides regulatory reference information only.
It does NOT provide medical or health advice. Regulatory approval means
a substance is permitted at specified levels — not that it is harmless
at all doses or beneficial for all individuals.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

REGULATORY_DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "regulatory_references.json"
)

_REGULATORY_CACHE: Optional[Dict[str, Any]] = None


def load_regulatory_db() -> Dict[str, Any]:
    """Loads and caches the regulatory_references.json file."""
    global _REGULATORY_CACHE
    if _REGULATORY_CACHE is None:
        if os.path.exists(REGULATORY_DB_PATH):
            with open(REGULATORY_DB_PATH, "r", encoding="utf-8") as f:
                _REGULATORY_CACHE = json.load(f)
            logger.info("Regulatory DB loaded: %d entries", len(_REGULATORY_CACHE))
        else:
            logger.warning(
                "regulatory_references.json not found at %s. "
                "Regulatory lookups will return empty results.",
                REGULATORY_DB_PATH
            )
            _REGULATORY_CACHE = {}
    return _REGULATORY_CACHE


def get_regulatory_info(ins_code: str) -> Dict[str, Any]:
    """
    Returns regulatory reference information for a given INS code.

    Args:
        ins_code: e.g. 'INS 250', '250', 'E250'

    Returns:
        Regulatory info dict, or empty dict if not found.
        Fields (v2.1): ins_code, name, authority, source_url,
                fssai_status, efsa_adi, codex_status, fda_status,
                applicable_conditions, regulatory_notes, source_refs,
                last_verified, verified.
        All fields are read directly from regulatory_references.json —
        no values are invented or inferred.
    """
    db = load_regulatory_db()

    # Normalise lookup key
    clean = ins_code.strip().upper()
    clean_num = clean.replace("INS", "").replace("E", "").strip().lstrip("0") or clean

    return (
        db.get(clean) or
        db.get(f"INS {clean_num}") or
        db.get(clean_num) or
        {}
    )


def get_regulatory_info_batch(ins_codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Returns regulatory info for a list of INS codes.

    Returns:
        Dict mapping each INS code to its regulatory info (or {} if not found).
    """
    return {code: get_regulatory_info(code) for code in ins_codes}


def is_permitted_in_india(ins_code: str) -> Optional[bool]:
    """
    Returns True if the additive is permitted by FSSAI,
    False if prohibited, None if status is unknown.
    """
    info = get_regulatory_info(ins_code)
    status = info.get("fssai_status", "").lower()
    if "permitted" in status or "approved" in status:
        return True
    elif "prohibited" in status or "banned" in status or "not permitted" in status:
        return False
    return None  # Unknown
