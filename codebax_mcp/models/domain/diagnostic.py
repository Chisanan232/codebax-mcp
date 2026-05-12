"""Domain models for type checking diagnostics."""

from pydantic import BaseModel, Field

from .location import CodeLocation


class Diagnostic(BaseModel):
    """Represents a type checking diagnostic."""

    location: CodeLocation = Field(..., description="Diagnostic location")
    severity: str = Field(..., description="Severity (error, warning, info)")
    message: str = Field(..., description="Diagnostic message")
    code: str | None = Field(None, description="Diagnostic code")
    source: str = Field(default="pyright", description="Diagnostic source")

    class Config:
        frozen = True  # Immutable
