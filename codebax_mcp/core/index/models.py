"""Index data models."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from codebax_mcp.core.parser.models import Symbol, Range


class IndexEntry(BaseModel):
    """Index entry for a symbol."""
    symbol: Symbol
    usages: List[Range] = []
    last_updated: float = 0.0


class SymbolReference(BaseModel):
    """Symbol reference with confidence."""
    symbol_id: str
    file: str
    line: int
    column: int
    kind: str  # "exact", "heuristic", "dynamic"
    confidence: float
    notes: Optional[str] = None
