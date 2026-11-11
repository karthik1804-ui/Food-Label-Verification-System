"""
Dietary Profile Entity Model
============================
Encapsulates user dietary restrictions, functional category avoidance,
and allergen preferences.
"""

import json
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class DietaryProfile:
    """Represents user-specific dietary preferences."""
    id: Optional[int]
    user_id: int
    preset_name: str = "custom"
    custom_override: bool = False
    avoid_synthetic_colors: bool = False
    avoid_preservatives: bool = False
    avoid_artificial_sweeteners: bool = False
    avoid_msg_flavor_enhancers: bool = False
    avoid_animal_derivatives: bool = False
    custom_allergens: List[str] = field(default_factory=list)
    custom_avoid_ins: List[str] = field(default_factory=list)
    custom_caution_ins: List[str] = field(default_factory=list)
    updated_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "DietaryProfile":
        """Instantiates DietaryProfile from a SQLite sqlite3.Row."""
        if not row:
            return None

        allergens = json.loads(row["custom_allergens"]) if row["custom_allergens"] else []
        avoid_ins = json.loads(row["custom_avoid_ins"]) if row["custom_avoid_ins"] else []
        caution_ins = json.loads(row["custom_caution_ins"]) if row["custom_caution_ins"] else []

        return cls(
            id=row["id"],
            user_id=row["user_id"],
            preset_name=row["preset_name"] or "custom",
            custom_override=bool(row["custom_override"]) if "custom_override" in row.keys() and row["custom_override"] is not None else False,
            avoid_synthetic_colors=bool(row["avoid_synthetic_colors"]),
            avoid_preservatives=bool(row["avoid_preservatives"]),
            avoid_artificial_sweeteners=bool(row["avoid_artificial_sweeteners"]),
            avoid_msg_flavor_enhancers=bool(row["avoid_msg_flavor_enhancers"]),
            avoid_animal_derivatives=bool(row["avoid_animal_derivatives"]),
            custom_allergens=allergens,
            custom_avoid_ins=avoid_ins,
            custom_caution_ins=caution_ins,
            updated_at=str(row["updated_at"]) if "updated_at" in row.keys() else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes dietary profile to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "preset_name": self.preset_name,
            "custom_override": self.custom_override,
            "avoid_synthetic_colors": self.avoid_synthetic_colors,
            "avoid_preservatives": self.avoid_preservatives,
            "avoid_artificial_sweeteners": self.avoid_artificial_sweeteners,
            "avoid_msg_flavor_enhancers": self.avoid_msg_flavor_enhancers,
            "avoid_animal_derivatives": self.avoid_animal_derivatives,
            "custom_allergens": self.custom_allergens,
            "custom_avoid_ins": self.custom_avoid_ins,
            "custom_caution_ins": self.custom_caution_ins,
            "updated_at": self.updated_at,
        }
