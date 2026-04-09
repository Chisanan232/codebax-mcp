"""Domain models for code locations."""

from pydantic import BaseModel, Field


class CodeLocation(BaseModel):
    """Represents a location in source code."""

    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number (1-indexed)")
    column: int = Field(..., description="Column number (0-indexed)")

    class Config:
        frozen = True  # Immutable


class CodeRange(BaseModel):
    """Represents a range in source code."""

    start: CodeLocation = Field(..., description="Start location")
    end: CodeLocation = Field(..., description="End location")

    class Config:
        frozen = True  # Immutable
