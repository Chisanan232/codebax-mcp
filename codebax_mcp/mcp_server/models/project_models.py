"""Pydantic models for project tools input/output."""

from typing import Any

from pydantic import BaseModel


# Input Models
class GetConventionsInput(BaseModel):
    workspace_root: str
    language_hint: str | None = None


class DescribeLayoutInput(BaseModel):
    workspace_root: str


class ListSubprojectsInput(BaseModel):
    workspace_root: str


class GetExecutionProfileInput(BaseModel):
    workspace_root: str


# Output Models
class TestConfig(BaseModel):
    root: str
    framework: str | None = None
    file_patterns: list[str] = []
    naming_style: str | None = None


class SourceConfig(BaseModel):
    roots: list[str] = []
    module_layout: str | None = None


class Constraints(BaseModel):
    forbid_creating_dirs: list[str] = []
    prefer_existing_over_new: bool = True


class ConventionsOutput(BaseModel):
    test: TestConfig
    source: SourceConfig
    style: dict[str, Any]
    tooling: dict[str, Any]
    constraints: Constraints
    notes: str | None = None


class LayoutOutput(BaseModel):
    layers: list[dict[str, Any]] = []
    directories: dict[str, Any] = {}
    notes: str | None = None


class Subproject(BaseModel):
    name: str
    type: str
    path: str
    config: str


class SubprojectsOutput(BaseModel):
    workspace_root: str
    subprojects: list[Subproject] = []
    total: int = 0


class ExecutionProfile(BaseModel):
    profiles: list[dict[str, Any]] = []
    commands: dict[str, str] = {}
    entry_points: list[dict[str, Any]] = []
    notes: str | None = None
