"""Pydantic models for project tools input/output."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# Input Models
class GetConventionsInput(BaseModel):
    workspace_root: str
    language_hint: Optional[str] = None


class DescribeLayoutInput(BaseModel):
    workspace_root: str


class ListSubprojectsInput(BaseModel):
    workspace_root: str


class GetExecutionProfileInput(BaseModel):
    workspace_root: str


# Output Models
class TestConfig(BaseModel):
    root: str
    framework: Optional[str] = None
    file_patterns: List[str] = []
    naming_style: Optional[str] = None


class SourceConfig(BaseModel):
    roots: List[str] = []
    module_layout: Optional[str] = None


class Constraints(BaseModel):
    forbid_creating_dirs: List[str] = []
    prefer_existing_over_new: bool = True


class ConventionsOutput(BaseModel):
    test: TestConfig
    source: SourceConfig
    style: Dict[str, Any]
    tooling: Dict[str, Any]
    constraints: Constraints
    notes: Optional[str] = None


class LayoutOutput(BaseModel):
    layers: List[Dict[str, Any]] = []
    directories: Dict[str, Any] = {}
    notes: Optional[str] = None


class Subproject(BaseModel):
    name: str
    type: str
    path: str
    config: str


class SubprojectsOutput(BaseModel):
    workspace_root: str
    subprojects: List[Subproject] = []
    total: int = 0


class ExecutionProfile(BaseModel):
    profiles: List[Dict[str, Any]] = []
    commands: Dict[str, str] = {}
    entry_points: List[Dict[str, Any]] = []
    notes: Optional[str] = None
