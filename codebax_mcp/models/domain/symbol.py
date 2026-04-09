"""Domain models for code symbols."""

from pydantic import BaseModel, Field

from .location import CodeLocation


class Symbol(BaseModel):
    """Represents a code symbol (function, class, method, variable)."""

    id: str = Field(..., description="Unique identifier for the symbol")
    name: str = Field(..., description="Symbol name")
    kind: str = Field(..., description="Symbol kind (function, class, method, variable, etc.)")
    language: str = Field(..., description="Programming language")
    location: CodeLocation = Field(..., description="Definition location")
    signature: str | None = Field(None, description="Function/method signature")
    docstring: str | None = Field(None, description="Documentation string")

    class Config:
        frozen = True  # Immutable


class SymbolUsage(BaseModel):
    """Represents a usage of a symbol."""

    symbol_id: str = Field(..., description="Symbol identifier")
    location: CodeLocation = Field(..., description="Usage location")
    kind: str = Field(..., description="Usage kind (exact, heuristic, dynamic)")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)", ge=0.0, le=1.0)

    class Config:
        frozen = True  # Immutable


class SymbolReference(BaseModel):
    """Represents a reference to a symbol."""

    symbol: Symbol = Field(..., description="Referenced symbol")
    usages: list[SymbolUsage] = Field(default_factory=list, description="List of usages")
