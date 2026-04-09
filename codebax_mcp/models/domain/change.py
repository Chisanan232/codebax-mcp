"""Domain models for code changes."""

from typing import Optional
from pydantic import BaseModel, Field
from .location import CodeLocation, CodeRange


class CodeChange(BaseModel):
    """Represents a change to source code."""
    
    file: str = Field(..., description="File path")
    range: Optional[CodeRange] = Field(None, description="Range to modify")
    old_text: str = Field(..., description="Old text to replace")
    new_text: str = Field(..., description="New text to insert")
    description: Optional[str] = Field(None, description="Description of the change")
    
    class Config:
        frozen = True  # Immutable


class RefactoringOperation(BaseModel):
    """Represents a refactoring operation."""
    
    operation_type: str = Field(..., description="Type of operation (rename, extract, inline, etc.)")
    changes: list[CodeChange] = Field(default_factory=list, description="List of code changes")
    dry_run: bool = Field(default=True, description="Whether this is a dry run")
    status: str = Field(default="pending", description="Operation status")
