"""Output models for project introspection tools."""

from pydantic import BaseModel, Field


class TestConventions(BaseModel):
    """Test framework conventions."""

    root: str = Field(..., description="Test root directory")
    framework: str | None = Field(None, description="Test framework name")
    file_patterns: list[str] = Field(default_factory=list, description="Test file patterns")
    naming_style: str | None = Field(None, description="Test naming style")


class SourceConventions(BaseModel):
    """Source code conventions."""

    roots: list[str] = Field(default_factory=list, description="Source roots")
    module_layout: str | None = Field(None, description="Module layout style")


class PythonStyle(BaseModel):
    """Python style preferences."""

    formatter: str | None = Field(None, description="Code formatter")
    type_checker: str | None = Field(None, description="Type checker")


class TypeScriptStyle(BaseModel):
    """TypeScript style preferences."""

    formatter: str | None = Field(None, description="Code formatter")
    test_framework: str | None = Field(None, description="Test framework")


class StyleConventions(BaseModel):
    """Code style conventions."""

    python: PythonStyle = Field(default_factory=PythonStyle, description="Python style")
    typescript: TypeScriptStyle = Field(default_factory=TypeScriptStyle, description="TypeScript style")


class PreCommitConfig(BaseModel):
    """Pre-commit configuration."""

    enabled: bool = Field(..., description="Whether pre-commit is enabled")
    config: str | None = Field(None, description="Config file path")
    run_command: str | None = Field(None, description="Command to run pre-commit")


class PythonTooling(BaseModel):
    """Python tooling configuration."""

    manager: str | None = Field(None, description="Package manager")
    entry: str | None = Field(None, description="Entry point")
    lock_files: list[str] = Field(default_factory=list, description="Lock files")
    test_command: str | None = Field(None, description="Test command")
    lint_commands: list[str] = Field(default_factory=list, description="Lint commands")
    pre_commit: PreCommitConfig = Field(
        default_factory=lambda: PreCommitConfig(enabled=False), description="Pre-commit config"
    )


class NodeWorkspace(BaseModel):
    """Node workspace configuration."""

    enabled: bool = Field(..., description="Whether workspace is enabled")
    tool: str | None = Field(None, description="Workspace tool")
    config: str | None = Field(None, description="Config file path")


class NodeScripts(BaseModel):
    """Node scripts configuration."""

    test: str | None = Field(None, description="Test script")
    lint: str | None = Field(None, description="Lint script")
    build: str | None = Field(None, description="Build script")


class NodeTooling(BaseModel):
    """Node tooling configuration."""

    manager: str | None = Field(None, description="Package manager")
    root_package_json: str | None = Field(None, description="Root package.json path")
    workspace: NodeWorkspace = Field(
        default_factory=lambda: NodeWorkspace(enabled=False), description="Workspace config"
    )
    scripts: NodeScripts = Field(default_factory=NodeScripts, description="Scripts config")


class JvmTooling(BaseModel):
    """JVM tooling configuration."""

    build_tool: str | None = Field(None, description="Build tool")
    wrapper: str | None = Field(None, description="Wrapper script")
    subprojects: list[str] = Field(default_factory=list, description="Subprojects")
    test_command: str | None = Field(None, description="Test command")


class ToolingConventions(BaseModel):
    """Tooling conventions."""

    python: PythonTooling = Field(default_factory=PythonTooling, description="Python tooling")
    node: NodeTooling = Field(default_factory=NodeTooling, description="Node tooling")
    jvm: JvmTooling = Field(default_factory=JvmTooling, description="JVM tooling")


class ProjectConstraints(BaseModel):
    """Project constraints."""

    forbid_creating_dirs: list[str] = Field(default_factory=list, description="Directories that should not be created")
    prefer_existing_over_new: bool = Field(..., description="Prefer existing files over creating new ones")


class ConventionsOutput(BaseModel):
    """Output for project.get_conventions tool."""

    test: TestConventions = Field(..., description="Test framework configuration")
    source: SourceConventions = Field(..., description="Source code layout configuration")
    style: StyleConventions = Field(..., description="Code style preferences")
    tooling: ToolingConventions = Field(..., description="Tooling configuration")
    constraints: ProjectConstraints = Field(..., description="Project constraints")
    notes: str | None = Field(None, description="Additional information")


class ModuleInfo(BaseModel):
    """Information about a project module."""

    type: str = Field(..., description="Module type")
    path: str = Field(..., description="Module path")
    description: str | None = Field(None, description="Module description")


class LayoutOutput(BaseModel):
    """Output for project.describe_layout tool."""

    roots: list[str] = Field(default_factory=list, description="Source roots")
    modules: list[ModuleInfo] = Field(default_factory=list, description="Project modules")
    test_roots: list[str] = Field(default_factory=list, description="Test roots")
    notes: str | None = Field(None, description="Additional information")


class SubprojectInfo(BaseModel):
    """Information about a subproject."""

    name: str = Field(..., description="Subproject name")
    path: str = Field(..., description="Subproject path")
    language: str | None = Field(None, description="Programming language")
    kind: str | None = Field(None, description="Subproject kind")
    test_command: str | None = Field(None, description="Test command")
    build_command: str | None = Field(None, description="Build command")


class SubprojectsOutput(BaseModel):
    """Output for project.list_subprojects tool."""

    workspace_root: str = Field(..., description="Workspace root path")
    subprojects: list[SubprojectInfo] = Field(default_factory=list, description="List of detected subprojects")
    total: int = Field(0, description="Total number of subprojects")


class ExecutionProfileOutput(BaseModel):
    """Output for project.get_execution_profile tool."""

    command: str = Field(..., description="Command to execute")
    cwd: str = Field(..., description="Working directory")
    pre_steps: list[str] = Field(default_factory=list, description="Pre-execution steps")
    notes: str | None = Field(None, description="Additional information")
