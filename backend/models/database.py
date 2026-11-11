"""
Database Models & SQLite Initialization
=======================================
Database layer for Food Label Verification System.
Manages user accounts, authentication tokens, dietary profiles,
and persistent analysis scan history.
"""

import os
import sqlite3
import logging
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "app.db")
)


def get_db_path() -> str:
    """Returns absolute path to the SQLite database."""
    return DB_PATH


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Creates and returns a SQLite connection configured with:
      - row_factory = sqlite3.Row for dict-like access
      - PRAGMA foreign_keys = ON for relational integrity
    """
    path = db_path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """
    Initializes database schema with all required tables and indexes:
      - users
      - auth_tokens
      - dietary_profiles
      - analysis_history
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # 1. Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Auth tokens table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    # 3. Dietary profiles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dietary_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            preset_name TEXT DEFAULT 'custom',
            custom_override INTEGER DEFAULT 0,
            avoid_synthetic_colors INTEGER DEFAULT 0,
            avoid_preservatives INTEGER DEFAULT 0,
            avoid_artificial_sweeteners INTEGER DEFAULT 0,
            avoid_msg_flavor_enhancers INTEGER DEFAULT 0,
            avoid_animal_derivatives INTEGER DEFAULT 0,
            custom_allergens TEXT DEFAULT '[]',
            custom_avoid_ins TEXT DEFAULT '[]',
            custom_caution_ins TEXT DEFAULT '[]',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    # Automated schema migrations for existing databases
    try:
        existing_profile_cols = [
            c[1] for c in cursor.execute("PRAGMA table_info(dietary_profiles);").fetchall()
        ]
        if existing_profile_cols and "custom_override" not in existing_profile_cols:
            cursor.execute("ALTER TABLE dietary_profiles ADD COLUMN custom_override INTEGER DEFAULT 0;")
            logger.info("Database migration: Added 'custom_override' column to dietary_profiles.")
    except Exception as mig_err:
        logger.warning("Database migration check error: %s", str(mig_err))

    # 4. Analysis history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id TEXT,
            ean TEXT,
            product_name TEXT,
            raw_text TEXT,
            ocr_confidence REAL DEFAULT 1.0,
            final_score INTEGER,
            grade TEXT,
            personal_score INTEGER,
            personal_verdict TEXT,
            allergen_alerts TEXT DEFAULT '[]',
            additives_summary TEXT DEFAULT '[]',
            system_audit_summary TEXT DEFAULT '{}',
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );
    """)

    # Create indexes for performant lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_token ON auth_tokens(token);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_user ON auth_tokens(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_user ON dietary_profiles(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_user ON analysis_history(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_ean ON analysis_history(ean);")

    conn.commit()
    conn.close()
    logger.info("Initialized database schema at %s", db_path or DB_PATH)
