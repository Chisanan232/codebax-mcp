"""Type checking models."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class Parameter(BaseModel):
    """Function parameter."""
    name: str
    type: Optional[str] = None
    optional: Optional[bool] = None
    default: Optional[str] = None


class ReturnType(BaseModel):
    """Return type information."""
    raw: Optional[str] = None
    kind: Optional[str] = None


class Signature(BaseModel):
    """Function/method signature."""
    parameters: List[Parameter] = []
    return_type: Optional[ReturnType] = None
    async_: Optional[bool] = None


class TypeInfo(BaseModel):
    """Type information for a symbol."""
    symbol: str
    kind: str
    language: str
    signature: Optional[Signature] = None
    docstring: Optional[str] = None


class Diagnostic(BaseModel):
    """Type checking diagnostic."""
    file: str
    line: int
    column: int
    message: str
    severity: str  # "error", "warning", "information"
    code: Optional[str] = None
