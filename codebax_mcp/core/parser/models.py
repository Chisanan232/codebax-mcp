"""Shared AST and Symbol models."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class SymbolKind(str, Enum):
    """Symbol kinds."""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    MODULE = "module"
    PARAMETER = "parameter"
    PROPERTY = "property"


class Range(BaseModel):
    """Code range."""
    line_start: int
    column_start: int
    line_end: int
    column_end: int


class Symbol(BaseModel):
    """Symbol definition."""
    symbol_id: str
    name: str
    kind: SymbolKind
    language: str
    file: str
    range: Range
    parent_id: Optional[str] = None
    docstring: Optional[str] = None
    signature: Optional[str] = None
