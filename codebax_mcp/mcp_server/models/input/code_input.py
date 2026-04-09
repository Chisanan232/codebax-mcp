"""Input models for code analysis, navigation, refactoring, and search tools."""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class IndexCodebaseInput(BaseModel):
    """Input for code.index tool."""
    
    workspace_root: str = Field(
        ...,
        description="Path to the workspace root directory"
    )
    full: bool = Field(
        default=False,
        description="If True, rebuild entire index. If False, update only changed files"
    )
    paths: Optional[List[str]] = Field(
        default=None,
        description="Optional list of specific file paths to index"
    )


class IdentifySymbolInput(BaseModel):
    """Input for code.identify_symbol tool."""
    
    file: str = Field(
        ...,
        description="Path to the file (relative to workspace_root)"
    )
    language: str = Field(
        ...,
        description="Programming language (python, typescript, java, etc.)"
    )
    line: int = Field(
        ...,
        description="Line number (1-indexed)"
    )
    column: int = Field(
        ...,
        description="Column number (0-indexed)"
    )
    workspace_root: str = Field(
        default=".",
        description="Path to the workspace root directory"
    )


class GetDefinitionInput(BaseModel):
    """Input for code.get_definition tool."""
    
    symbol_id: str = Field(
        ...,
        description="Unique identifier of the symbol"
    )
    workspace_root: str = Field(
        default=".",
        description="Path to the workspace root directory"
    )


class FindUsagesInput(BaseModel):
    """Input for code.find_usages tool."""
    
    symbol_id: str = Field(
        ...,
        description="Unique identifier of the symbol"
    )
    include_tests: bool = Field(
        default=False,
        description="If True, include usages in test files"
    )
    max_results: Optional[int] = Field(
        None,
        description="Maximum number of results to return"
    )
    workspace_root: str = Field(
        default=".",
        description="Path to the workspace root directory"
    )


class GetCallGraphInput(BaseModel):
    """Input for code.get_call_graph tool."""
    
    symbol_id: str = Field(
        ...,
        description="Unique identifier of the symbol"
    )
    direction: str = Field(
        default="both",
        description="Direction to trace - 'incoming' (callers), 'outgoing' (callees), or 'both'"
    )
    depth: int = Field(
        default=3,
        description="Maximum depth to traverse"
    )
    workspace_root: str = Field(
        default=".",
        description="Path to the workspace root directory"
    )


class RenameSymbolInput(BaseModel):
    """Input for code.rename_symbol tool."""
    
    symbol_id: str = Field(
        ...,
        description="Unique identifier of the symbol"
    )
    new_name: str = Field(
        ...,
        description="New name for the symbol"
    )
    dry_run: bool = Field(
        default=True,
        description="If True, preview changes without applying"
    )
    workspace_root: str = Field(
        default=".",
        description="Path to the workspace root directory"
    )


class Position(BaseModel):
    """Position in source code."""
    
    line: int = Field(..., description="Line number")
    column: int = Field(..., description="Column number")


class CodeRange(BaseModel):
    """Code range with start and end positions."""
    
    start: Position = Field(..., description="Start position")
    end: Position = Field(..., description="End position")


class ExtractFunctionInput(BaseModel):
    """Input for code.extract_function tool."""
    
    file: str = Field(
        ...,
        description="Path to the file (relative to workspace_root)"
    )
    language: str = Field(
        ...,
        description="Programming language (python, typescript, java, etc.)"
    )
    range: CodeRange = Field(
        ...,
        description="Code range to extract"
    )
    new_name: str = Field(
        ...,
        description="Name for the extracted function"
    )
    dry_run: bool = Field(
        default=True,
        description="If True, only return proposed changes without applying"
    )
    workspace_root: str = Field(
        default=".",
        description="Path to the workspace root directory"
    )


class SemanticSearchInput(BaseModel):
    """Input for code.semantic_search tool."""
    
    query: str = Field(
        ...,
        description="Natural language search query"
    )
    top_k: int = Field(
        default=10,
        description="Maximum number of results to return"
    )
    filter_language: Optional[str] = Field(
        default=None,
        description="Optional language filter (python, typescript, java, etc.)"
    )
    filter_path_prefix: Optional[str] = Field(
        default=None,
        description="Optional path prefix filter"
    )
    workspace_root: str = Field(
        default=".",
        description="Path to the workspace root directory"
    )


class AnalyzePythonPatchCallsInput(BaseModel):
    """Input for code.analyze_python_patch_calls tool."""
    
    workspace_root: str = Field(
        default=".",
        description="Path to the workspace root directory"
    )
