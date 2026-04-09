"""Input models for project introspection tools."""

from typing import Optional
from pydantic import BaseModel, Field


class GetConventionsInput(BaseModel):
    """Input for project.get_conventions tool."""
    
    workspace_root: str = Field(
        ...,
        description="Path to the workspace root directory"
    )
    language_hint: Optional[str] = Field(
        None,
        description="Optional language hint (python, typescript, java, etc.)"
    )


class DescribeLayoutInput(BaseModel):
    """Input for project.describe_layout tool."""
    
    workspace_root: str = Field(
        ...,
        description="Path to the workspace root directory"
    )


class ListSubprojectsInput(BaseModel):
    """Input for project.list_subprojects tool."""
    
    workspace_root: str = Field(
        ...,
        description="Path to the workspace root directory"
    )


class GetExecutionProfileInput(BaseModel):
    """Input for project.get_execution_profile tool."""
    
    workspace_root: str = Field(
        ...,
        description="Path to the workspace root directory"
    )
    intent: str = Field(
        ...,
        description="Intent: 'test', 'lint', 'build', 'run_app', 'format', or 'install_deps'"
    )
    language: Optional[str] = Field(
        None,
        description="Optional language hint (python, typescript, java, etc.)"
    )
    package_hint: Optional[str] = Field(
        None,
        description="Optional subproject name or path keyword"
    )
