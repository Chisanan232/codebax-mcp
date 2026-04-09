"""Index data models."""

from pydantic import BaseModel

from codebax_mcp.core.parser.models import Range, Symbol


class IndexEntry(BaseModel):
    """Index entry for a symbol."""

    symbol: Symbol
    usages: list[Range] = []
    last_updated: float = 0.0


class SymbolReference(BaseModel):
    """Symbol reference with confidence."""

    symbol_id: str
    file: str
    line: int
    column: int
    kind: str  # "exact", "heuristic", "dynamic"
    confidence: float
    notes: str | None = None
