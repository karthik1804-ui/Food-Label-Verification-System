"""
Analysis Record Entity Model
============================
Encapsulates historical scan and verification records stored in SQLite.
"""

import json
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class AnalysisRecord:
    """Represents a persisted food label analysis record."""
    id: Optional[int]
    user_id: Optional[int]
    session_id: str
    ean: str
    product_name: str
    raw_text: str
    ocr_confidence: float = 1.0
    final_score: int = 100
    grade: str = "A"
    personal_score: int = 100
    personal_verdict: str = "N/A"
    allergen_alerts: List[Dict[str, Any]] = field(default_factory=list)
    additives_summary: List[str] = field(default_factory=list)
    system_audit_summary: Dict[str, Any] = field(default_factory=dict)
    scanned_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "AnalysisRecord":
        """Instantiates AnalysisRecord from a SQLite sqlite3.Row."""
        if not row:
            return None

        allergens = json.loads(row["allergen_alerts"]) if row["allergen_alerts"] else []
        additives = json.loads(row["additives_summary"]) if row["additives_summary"] else []
        audit = json.loads(row["system_audit_summary"]) if "system_audit_summary" in row.keys() and row["system_audit_summary"] else {}

        return cls(
            id=row["id"],
            user_id=row["user_id"],
            session_id=row["session_id"] if "session_id" in row.keys() else "",
            ean=row["ean"] if "ean" in row.keys() else "N/A",
            product_name=row["product_name"] if "product_name" in row.keys() else "Scanned Product",
            raw_text=row["raw_text"] if "raw_text" in row.keys() else "",
            ocr_confidence=float(row["ocr_confidence"]) if "ocr_confidence" in row.keys() and row["ocr_confidence"] is not None else 1.0,
            final_score=int(row["final_score"]) if "final_score" in row.keys() and row["final_score"] is not None else 100,
            grade=row["grade"] if "grade" in row.keys() else "A",
            personal_score=int(row["personal_score"]) if "personal_score" in row.keys() and row["personal_score"] is not None else 100,
            personal_verdict=row["personal_verdict"] if "personal_verdict" in row.keys() else "N/A",
            allergen_alerts=allergens,
            additives_summary=additives,
            system_audit_summary=audit,
            scanned_at=str(row["scanned_at"]) if "scanned_at" in row.keys() else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes analysis record to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "ean": self.ean,
            "product_name": self.product_name,
            "ocr_confidence": self.ocr_confidence,
            "final_score": self.final_score,
            "grade": self.grade,
            "personal_score": self.personal_score,
            "personal_verdict": self.personal_verdict,
            "allergen_alerts": self.allergen_alerts,
            "additives_summary": self.additives_summary,
            "additives_count": len(self.additives_summary),
            "system_audit_summary": self.system_audit_summary,
            "scanned_at": self.scanned_at,
        }
