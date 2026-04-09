"""Type checking models."""

from pydantic import BaseModel


class Parameter(BaseModel):
    """Function parameter."""

    name: str
    type: str | None = None
    optional: bool | None = None
    default: str | None = None


class ReturnType(BaseModel):
    """Return type information."""

    raw: str | None = None
    kind: str | None = None


class Signature(BaseModel):
    """Function/method signature."""

    parameters: list[Parameter] = []
    return_type: ReturnType | None = None
    async_: bool | None = None


class TypeInfo(BaseModel):
    """Type information for a symbol."""

    symbol: str
    kind: str
    language: str
    signature: Signature | None = None
    docstring: str | None = None


class Diagnostic(BaseModel):
    """Type checking diagnostic."""

    file: str
    line: int
    column: int
    message: str
    severity: str  # "error", "warning", "information"
    code: str | None = None
