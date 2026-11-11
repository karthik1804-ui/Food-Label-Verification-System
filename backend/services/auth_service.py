"""
Authentication and Dietary Profile Service
==========================================
Handles user registration, credential verification via pbkdf2:sha256,
session tokens, and persistent user dietary profiles in SQLite.
"""

import re
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash

from models.database import get_db_connection

logger = logging.getLogger(__name__)

# Token lifetime: 30 days
TOKEN_LIFETIME_DAYS = 30

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]{3,30}$")

# Preset definitions for dietary profiles
DIETARY_PRESETS: Dict[str, Dict[str, Any]] = {
    "custom": {
        "avoid_synthetic_colors": 0,
        "avoid_preservatives": 0,
        "avoid_artificial_sweeteners": 0,
        "avoid_msg_flavor_enhancers": 0,
        "avoid_animal_derivatives": 0,
        "custom_allergens": [],
        "custom_avoid_ins": [],
        "custom_caution_ins": [],
    },
    "clean_label": {
        "avoid_synthetic_colors": 1,
        "avoid_preservatives": 1,
        "avoid_artificial_sweeteners": 1,
        "avoid_msg_flavor_enhancers": 1,
        "avoid_animal_derivatives": 0,
        "custom_allergens": [],
        "custom_avoid_ins": ["INS 102", "INS 110", "INS 122", "INS 124", "INS 127", "INS 129", "INS 133", "INS 150d", "INS 211", "INS 250"],
        "custom_caution_ins": ["INS 621"],
    },
    "vegan": {
        "avoid_synthetic_colors": 0,
        "avoid_preservatives": 0,
        "avoid_artificial_sweeteners": 0,
        "avoid_msg_flavor_enhancers": 0,
        "avoid_animal_derivatives": 1,
        "custom_allergens": ["dairy", "egg", "fish", "shellfish"],
        "custom_avoid_ins": ["INS 120", "INS 428", "INS 901", "INS 904", "INS 542"],
        "custom_caution_ins": ["INS 322", "INS 471"],
    },
    "vegetarian": {
        "avoid_synthetic_colors": 0,
        "avoid_preservatives": 0,
        "avoid_artificial_sweeteners": 0,
        "avoid_msg_flavor_enhancers": 0,
        "avoid_animal_derivatives": 1,
        "custom_allergens": ["fish", "shellfish"],
        "custom_avoid_ins": ["INS 120", "INS 428", "INS 542"],
        "custom_caution_ins": ["INS 471"],
    },
    "low_sodium": {
        "avoid_synthetic_colors": 0,
        "avoid_preservatives": 0,
        "avoid_artificial_sweeteners": 0,
        "avoid_msg_flavor_enhancers": 1,
        "avoid_animal_derivatives": 0,
        "custom_allergens": [],
        "custom_avoid_ins": ["INS 621", "INS 211", "INS 250", "INS 251", "INS 500(i)", "INS 500(ii)"],
        "custom_caution_ins": ["INS 331", "INS 451", "INS 452"],
    },
    "child_safe": {
        "avoid_synthetic_colors": 1,
        "avoid_preservatives": 1,
        "avoid_artificial_sweeteners": 1,
        "avoid_msg_flavor_enhancers": 1,
        "avoid_animal_derivatives": 0,
        "custom_allergens": [],
        "custom_avoid_ins": ["INS 102", "INS 104", "INS 110", "INS 122", "INS 124", "INS 129", "INS 211", "INS 951", "INS 950"],
        "custom_caution_ins": ["INS 150d", "INS 621"],
    }
}


def register_user(
    username: str,
    email: str,
    password: str,
    db_path: Optional[str] = None
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Registers a new user account and creates an associated default dietary profile.
    Returns: (success: bool, user_data: dict, error_message: str | None)
    """
    clean_username = (username or "").strip()
    clean_email = (email or "").strip().lower()
    clean_password = (password or "").strip()

    if not USERNAME_REGEX.match(clean_username):
        return False, {}, "Username must be 3-30 characters (letters, numbers, underscores, hyphens only)."

    if not EMAIL_REGEX.match(clean_email):
        return False, {}, "A valid email address is required."

    if len(clean_password) < 6:
        return False, {}, "Password must be at least 6 characters long."

    pwd_hash = generate_password_hash(clean_password, method="pbkdf2:sha256")

    conn = get_db_connection(db_path)
    try:
        # Check uniqueness
        existing = conn.execute(
            "SELECT id, username, email FROM users WHERE username = ? OR email = ?",
            (clean_username, clean_email)
        ).fetchone()

        if existing:
            if existing["username"].lower() == clean_username.lower():
                return False, {}, "Username is already registered."
            else:
                return False, {}, "Email is already registered."

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (clean_username, clean_email, pwd_hash)
        )
        user_id = cursor.lastrowid

        # Create default dietary profile
        import json
        cursor.execute(
            """
            INSERT INTO dietary_profiles (
                user_id, preset_name, custom_override, avoid_synthetic_colors, avoid_preservatives,
                avoid_artificial_sweeteners, avoid_msg_flavor_enhancers, avoid_animal_derivatives,
                custom_allergens, custom_avoid_ins, custom_caution_ins
            ) VALUES (?, 'custom', 0, 0, 0, 0, 0, 0, '[]', '[]', '[]')
            """,
            (user_id,)
        )

        conn.commit()
        logger.info("Successfully registered user id=%d (%s)", user_id, clean_username)
        return True, {"id": user_id, "username": clean_username, "email": clean_email}, None

    except Exception as e:
        conn.rollback()
        logger.error("Failed to register user: %s", str(e))
        return False, {}, f"Database error during registration: {str(e)}"
    finally:
        conn.close()


def authenticate_user(
    identifier: str,
    password: str,
    db_path: Optional[str] = None
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Authenticates user with username or email + password.
    Creates a new auth token valid for 30 days.
    Returns: (success: bool, auth_payload: dict, error_message: str | None)
    """
    clean_id = (identifier or "").strip()
    clean_pwd = (password or "").strip()

    if not clean_id or not clean_pwd:
        return False, {}, "Identifier (username/email) and password are required."

    conn = get_db_connection(db_path)
    try:
        row = conn.execute(
            "SELECT id, username, email, password_hash FROM users WHERE username = ? OR email = ?",
            (clean_id, clean_id.lower())
        ).fetchone()

        if not row:
            return False, {}, "Invalid username or password."

        if not check_password_hash(row["password_hash"], clean_pwd):
            return False, {}, "Invalid username or password."

        user_id = row["id"]
        token = secrets.token_hex(32)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=TOKEN_LIFETIME_DAYS)).strftime("%Y-%m-%d %H:%M:%S")

        conn.execute(
            "INSERT INTO auth_tokens (token, user_id, expires_at) VALUES (?, ?, ?)",
            (token, user_id, expires_at)
        )
        conn.commit()

        # Fetch profile
        profile = get_user_profile(user_id, db_path=db_path)

        user_payload = {
            "token": token,
            "user": {
                "id": user_id,
                "username": row["username"],
                "email": row["email"],
            },
            "dietary_profile": profile
        }
        return True, user_payload, None

    except Exception as e:
        logger.error("Authentication error: %s", str(e))
        return False, {}, f"Internal authentication error: {str(e)}"
    finally:
        conn.close()


def verify_token(token: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Validates a Bearer token. Returns user dict if valid and unexpired, None otherwise.
    """
    if not token or not isinstance(token, str):
        return None

    clean_token = token.replace("Bearer ", "").strip()
    if not clean_token:
        return None

    conn = get_db_connection(db_path)
    try:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        row = conn.execute(
            """
            SELECT u.id, u.username, u.email, t.expires_at
            FROM auth_tokens t
            JOIN users u ON t.user_id = u.id
            WHERE t.token = ? AND t.expires_at > ?
            """,
            (clean_token, now_str)
        ).fetchone()

        if row:
            return {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"]
            }
        return None
    except Exception as e:
        logger.error("Token verification error: %s", str(e))
        return None
    finally:
        conn.close()


def revoke_token(token: str, db_path: Optional[str] = None) -> bool:
    """Logs out user by removing token from auth_tokens table."""
    if not token:
        return False
    clean_token = token.replace("Bearer ", "").strip()
    conn = get_db_connection(db_path)
    try:
        conn.execute("DELETE FROM auth_tokens WHERE token = ?", (clean_token,))
        conn.commit()
        return True
    except Exception as e:
        logger.error("Token revocation error: %s", str(e))
        return False
    finally:
        conn.close()


def get_user_profile(user_id: int, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves dietary profile for user_id."""
    import json
    conn = get_db_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM dietary_profiles WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if not row:
            # Create default profile if not exists
            conn.execute(
                """
                INSERT OR IGNORE INTO dietary_profiles (
                    user_id, preset_name, avoid_synthetic_colors, avoid_preservatives,
                    avoid_artificial_sweeteners, avoid_msg_flavor_enhancers, avoid_animal_derivatives,
                    custom_allergens, custom_avoid_ins, custom_caution_ins
                ) VALUES (?, 'custom', 0, 0, 0, 0, 0, '[]', '[]', '[]')
                """,
                (user_id,)
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM dietary_profiles WHERE user_id = ?",
                (user_id,)
            ).fetchone()

        allergens = json.loads(row["custom_allergens"]) if row["custom_allergens"] else []
        avoid_ins = json.loads(row["custom_avoid_ins"]) if row["custom_avoid_ins"] else []
        caution_ins = json.loads(row["custom_caution_ins"]) if row["custom_caution_ins"] else []

        return {
            "user_id": user_id,
            "preset_name": row["preset_name"] or "custom",
            "avoid_synthetic_colors": bool(row["avoid_synthetic_colors"]),
            "avoid_preservatives": bool(row["avoid_preservatives"]),
            "avoid_artificial_sweeteners": bool(row["avoid_artificial_sweeteners"]),
            "avoid_msg_flavor_enhancers": bool(row["avoid_msg_flavor_enhancers"]),
            "avoid_animal_derivatives": bool(row["avoid_animal_derivatives"]),
            "custom_allergens": allergens,
            "custom_avoid_ins": avoid_ins,
            "custom_caution_ins": caution_ins,
        }
    except Exception as e:
        logger.error("Error retrieving user profile for user %d: %s", user_id, str(e))
        return {
            "user_id": user_id,
            "preset_name": "custom",
            "avoid_synthetic_colors": False,
            "avoid_preservatives": False,
            "avoid_artificial_sweeteners": False,
            "avoid_msg_flavor_enhancers": False,
            "avoid_animal_derivatives": False,
            "custom_allergens": [],
            "custom_avoid_ins": [],
            "custom_caution_ins": [],
        }
    finally:
        conn.close()


def update_user_profile(
    user_id: int,
    profile_data: Dict[str, Any],
    db_path: Optional[str] = None
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Updates the dietary preferences for user_id.
    """
    import json
    conn = get_db_connection(db_path)
    try:
        preset_name = str(profile_data.get("preset_name", "custom")).lower()
        if preset_name in DIETARY_PRESETS and preset_name != "custom" and not profile_data.get("custom_override", False):
            # Apply preset values
            p = DIETARY_PRESETS[preset_name]
            avoid_colors = p["avoid_synthetic_colors"]
            avoid_preserv = p["avoid_preservatives"]
            avoid_sweeteners = p["avoid_artificial_sweeteners"]
            avoid_msg = p["avoid_msg_flavor_enhancers"]
            avoid_animal = p["avoid_animal_derivatives"]
            allergens = p["custom_allergens"]
            avoid_ins = p["custom_avoid_ins"]
            caution_ins = p["custom_caution_ins"]
        else:
            avoid_colors = 1 if profile_data.get("avoid_synthetic_colors") else 0
            avoid_preserv = 1 if profile_data.get("avoid_preservatives") else 0
            avoid_sweeteners = 1 if profile_data.get("avoid_artificial_sweeteners") else 0
            avoid_msg = 1 if profile_data.get("avoid_msg_flavor_enhancers") else 0
            avoid_animal = 1 if profile_data.get("avoid_animal_derivatives") else 0
            allergens = list(profile_data.get("custom_allergens") or [])
            avoid_ins = list(profile_data.get("custom_avoid_ins") or [])
            caution_ins = list(profile_data.get("custom_caution_ins") or [])

        custom_override = 1 if profile_data.get("custom_override", False) else 0

        conn.execute(
            """
            INSERT INTO dietary_profiles (
                user_id, preset_name, custom_override, avoid_synthetic_colors, avoid_preservatives,
                avoid_artificial_sweeteners, avoid_msg_flavor_enhancers, avoid_animal_derivatives,
                custom_allergens, custom_avoid_ins, custom_caution_ins, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                preset_name = excluded.preset_name,
                custom_override = excluded.custom_override,
                avoid_synthetic_colors = excluded.avoid_synthetic_colors,
                avoid_preservatives = excluded.avoid_preservatives,
                avoid_artificial_sweeteners = excluded.avoid_artificial_sweeteners,
                avoid_msg_flavor_enhancers = excluded.avoid_msg_flavor_enhancers,
                avoid_animal_derivatives = excluded.avoid_animal_derivatives,
                custom_allergens = excluded.custom_allergens,
                custom_avoid_ins = excluded.custom_avoid_ins,
                custom_caution_ins = excluded.custom_caution_ins,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                user_id, preset_name, custom_override, avoid_colors, avoid_preserv, avoid_sweeteners,
                avoid_msg, avoid_animal, json.dumps(allergens), json.dumps(avoid_ins), json.dumps(caution_ins)
            )
        )
        conn.commit()

        updated_profile = get_user_profile(user_id, db_path=db_path)
        return True, updated_profile, None

    except Exception as e:
        logger.error("Error updating user profile: %s", str(e))
        return False, {}, f"Database error updating profile: {str(e)}"
    finally:
        conn.close()


def get_user_preferences(
    user_id: int,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Returns structured dietary preferences dictionary for user_id.
    """
    profile = get_user_profile(user_id, db_path=db_path)
    return {
        "user_id": user_id,
        "preset_name": profile.get("preset_name", "custom"),
        "custom_override": profile.get("custom_override", False),
        "categories": {
            "avoid_synthetic_colors": profile.get("avoid_synthetic_colors", False),
            "avoid_preservatives": profile.get("avoid_preservatives", False),
            "avoid_artificial_sweeteners": profile.get("avoid_artificial_sweeteners", False),
            "avoid_msg_flavor_enhancers": profile.get("avoid_msg_flavor_enhancers", False),
            "avoid_animal_derivatives": profile.get("avoid_animal_derivatives", False),
        },
        "custom_allergens": profile.get("custom_allergens", []),
        "custom_avoid_ins": profile.get("custom_avoid_ins", []),
        "custom_caution_ins": profile.get("custom_caution_ins", []),
    }


def update_category_preferences(
    user_id: int,
    categories_data: Dict[str, Any],
    db_path: Optional[str] = None
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Granularly updates category avoidance flags for user_id.
    """
    profile = get_user_profile(user_id, db_path=db_path)

    # Allow passing {"categories": {...}} or direct dict
    data = categories_data.get("categories", categories_data)

    for key in [
        "avoid_synthetic_colors",
        "avoid_preservatives",
        "avoid_artificial_sweeteners",
        "avoid_msg_flavor_enhancers",
        "avoid_animal_derivatives"
    ]:
        if key in data:
            profile[key] = bool(data[key])

    profile["custom_override"] = True
    profile["preset_name"] = "custom"
    return update_user_profile(user_id, profile, db_path=db_path)


def manage_additive_preference(
    user_id: int,
    action: str,
    code: str,
    pref_type: str = "avoid",
    db_path: Optional[str] = None
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Adds or removes an individual INS code from the user's avoidance or caution list.
    """
    clean_code = (code or "").strip().upper()
    if not clean_code:
        return False, {}, "Additive code is required."

    if not clean_code.startswith("INS ") and not clean_code.startswith("E"):
        clean_code = f"INS {clean_code}"

    clean_action = (action or "add").strip().lower()
    target_type = "custom_caution_ins" if pref_type.lower() == "caution" else "custom_avoid_ins"

    profile = get_user_profile(user_id, db_path=db_path)
    current_list = list(profile.get(target_type, []))

    if clean_action == "add":
        if clean_code not in current_list:
            current_list.append(clean_code)
    elif clean_action == "remove":
        current_list = [c for c in current_list if c != clean_code]
    else:
        return False, {}, f"Unsupported action: '{action}'. Use 'add' or 'remove'."

    profile[target_type] = current_list
    profile["custom_override"] = True
    profile["preset_name"] = "custom"
    return update_user_profile(user_id, profile, db_path=db_path)


def manage_allergy_preferences(
    user_id: int,
    action: str,
    allergens_input: Any,
    db_path: Optional[str] = None
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Adds, removes, or sets user allergen flags.
    """
    profile = get_user_profile(user_id, db_path=db_path)
    current_allergens = set(profile.get("custom_allergens", []))

    if isinstance(allergens_input, str):
        incoming = [s.strip().lower() for s in allergens_input.split(",") if s.strip()]
    elif isinstance(allergens_input, (list, tuple, set)):
        incoming = [str(s).strip().lower() for s in allergens_input if str(s).strip()]
    else:
        incoming = []

    clean_action = (action or "set").strip().lower()
    if clean_action == "add":
        current_allergens.update(incoming)
    elif clean_action == "remove":
        current_allergens.difference_update(incoming)
    elif clean_action == "set":
        current_allergens = set(incoming)
    else:
        return False, {}, f"Unsupported action: '{action}'. Use 'add', 'remove', or 'set'."

    profile["custom_allergens"] = sorted(list(current_allergens))
    profile["custom_override"] = True
    profile["preset_name"] = "custom"
    return update_user_profile(user_id, profile, db_path=db_path)

