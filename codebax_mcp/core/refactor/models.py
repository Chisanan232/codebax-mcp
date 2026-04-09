"""Refactoring models."""

from pydantic import BaseModel

from codebax_mcp.core.parser.models import Range


class TextEdit(BaseModel):
    """Text edit for refactoring."""

    range: Range
    new_text: str


class RefactoringResult(BaseModel):
    """Result of a refactoring operation."""

    status: str  # "ok" or "failed"
    file: str
    edits: list[TextEdit] = []
    error: str = ""
    notes: str = ""
