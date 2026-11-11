"""
User Entity Model
=================
Encapsulates user account entity and credential validation rules.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_-]{3,30}$")
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class User:
    """Represents a registered user account."""
    id: Optional[int]
    username: str
    email: str
    password_hash: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "User":
        """Instantiates User entity from a SQLite sqlite3.Row."""
        if not row:
            return None
        return cls(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"] if "password_hash" in row.keys() else "",
            created_at=str(row["created_at"]) if "created_at" in row.keys() else None,
            updated_at=str(row["updated_at"]) if "updated_at" in row.keys() else None,
        )

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Serializes user entity to dictionary, omitting password hash by default."""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if include_sensitive:
            data["password_hash"] = self.password_hash
        return data

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, Optional[str]]:
        """Validates username syntax."""
        clean = (username or "").strip()
        if not clean:
            return False, "Username is required."
        if not USERNAME_REGEX.match(clean):
            return False, "Username must be 3-30 characters (letters, numbers, underscores, hyphens only)."
        return True, None

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validates email format."""
        clean = (email or "").strip().lower()
        if not clean:
            return False, "Email address is required."
        if not EMAIL_REGEX.match(clean):
            return False, "A valid email address is required."
        return True, None

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """Validates password strength."""
        clean = (password or "").strip()
        if len(clean) < 6:
            return False, "Password must be at least 6 characters long."
        return True, None
