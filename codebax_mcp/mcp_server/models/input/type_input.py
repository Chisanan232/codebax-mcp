"""Input models for type checking and validation tools."""

from pydantic import BaseModel, Field


class ContextRange(BaseModel):
    """Context range for disambiguation."""

    line_start: int = Field(..., description="Start line number")
    line_end: int = Field(..., description="End line number")


class Position(BaseModel):
    """Position in source code."""

    line: int = Field(..., description="Line number")
    column: int = Field(..., description="Column number")


class EditRange(BaseModel):
    """Edit range with start and end positions."""

    start: Position = Field(..., description="Start position")
    end: Position = Field(..., description="End position")


class ChangeEdit(BaseModel):
    """Edit within a change."""

    range: EditRange = Field(..., description="Edit range")
    new_text: str = Field(..., description="New text")


class Change(BaseModel):
    """A change to validate."""

    file: str = Field(..., description="File path")
    edits: list[ChangeEdit] = Field(default_factory=list, description="List of edits")


class GetSymbolInfoInput(BaseModel):
    """Input for type.get_symbol_info tool."""

    symbol: str = Field(..., description="Symbol name to look up")
    file: str | None = Field(default=None, description="Optional file path to narrow search")
    language: str = Field(default="python", description="Programming language")
    context_range: ContextRange | None = Field(default=None, description="Optional context range for disambiguation")
    workspace_root: str = Field(default=".", description="Path to the workspace root directory")


class FindSimilarUsagesInput(BaseModel):
    """Input for type.find_similar_usages tool."""

    symbol: str = Field(..., description="Symbol name to search for similar symbols")
    language: str = Field(default="python", description="Programming language")
    workspace_root: str = Field(default=".", description="Path to the workspace root directory")


class GetExpectedAtPositionInput(BaseModel):
    """Input for type.get_expected_at_position tool."""

    file: str = Field(..., description="Path to the file (relative to workspace_root)")
    line: int = Field(..., description="Line number (1-indexed)")
    column: int = Field(..., description="Column number (0-indexed)")
    language: str = Field(default="python", description="Programming language")
    workspace_root: str = Field(default=".", description="Path to the workspace root directory")


class InferExpressionInput(BaseModel):
    """Input for type.infer_expression tool."""

    file: str = Field(..., description="Path to the file (relative to workspace_root)")
    expression: str = Field(..., description="Expression to analyze")
    language: str = Field(default="python", description="Programming language")
    context_range: ContextRange | None = Field(default=None, description="Optional context range for analysis")
    workspace_root: str = Field(default=".", description="Path to the workspace root directory")


class ValidateChangesInput(BaseModel):
    """Input for type.validate_changes tool."""

    file: str = Field(..., description="Path to the file (relative to workspace_root)")
    changes: list[Change] = Field(..., description="List of changes to validate")
    language: str = Field(default="python", description="Programming language")
    dry_run: bool = Field(default=True, description="If True, don't apply changes")
    workspace_root: str = Field(default=".", description="Path to the workspace root directory")


class SuggestFixInput(BaseModel):
    """Input for type.suggest_fix tool."""

    file: str = Field(..., description="Path to the file (relative to workspace_root)")
    line: int = Field(..., description="Line number of the error (1-indexed)")
    column: int = Field(..., description="Column number of the error (0-indexed)")
    error_message: str = Field(..., description="Error message from type checker")
    language: str = Field(default="python", description="Programming language")
    workspace_root: str = Field(default=".", description="Path to the workspace root directory")


class GetTechStackPreferencesInput(BaseModel):
    """Input for type.get_tech_stack_preferences tool."""

    workspace_root: str = Field(..., description="Path to the workspace root directory")
    language: str | None = Field(default=None, description="Optional language filter (python, typescript, java, etc.)")
