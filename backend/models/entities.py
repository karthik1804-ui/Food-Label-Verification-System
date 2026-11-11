"""
Entities Aggregation Module
===========================
Exports all database entity classes for the Food Label Verification System.
"""

from .user import User
from .profile import DietaryProfile
from .analysis import AnalysisRecord

__all__ = ["User", "DietaryProfile", "AnalysisRecord"]
