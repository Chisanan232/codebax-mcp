"""Input models for test discovery and generation tools."""

from pydantic import BaseModel, Field


class LocateForSourceInput(BaseModel):
    """Input for test.locate_for_source tool."""

    source_path: str = Field(..., description="Path to the source file (relative to workspace_root)")
    workspace_root: str = Field(default=".", description="Path to the workspace root directory")


class CreateOrUpdateForSymbolInput(BaseModel):
    """Input for test.create_or_update_for_symbol tool."""

    source_path: str = Field(..., description="Path to the source file containing the symbol")
    symbol: str = Field(..., description="Name of the symbol (function, class, or method)")
    language: str = Field(..., description="Programming language (python, typescript, java, etc.)")
    intent: str = Field(..., description="Operation intent - 'add_or_update' or 'delete'")
    behavior_description: str = Field(..., description="Description of what the symbol should do (for test generation)")
    workspace_root: str = Field(default=".", description="Path to the workspace root directory")
