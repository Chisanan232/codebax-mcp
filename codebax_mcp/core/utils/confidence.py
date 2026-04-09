"""Confidence scoring utilities."""

from enum import Enum
from typing import Literal


class ConfidenceLevel(str, Enum):
    """Confidence levels for results."""
    EXACT = "exact"
    HEURISTIC = "heuristic"
    DYNAMIC = "dynamic"


def calculate_confidence(kind: Literal["exact", "heuristic", "dynamic"]) -> float:
    """Calculate confidence score based on kind."""
    confidence_map = {
        "exact": 1.0,
        "heuristic": 0.7,
        "dynamic": 0.3
    }
    return confidence_map.get(kind, 0.5)
