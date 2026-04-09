"""MCP tools for project introspection and analysis.

Tools:
- project.get_conventions - Auto-detect project conventions
- project.describe_layout - Output project layer structure
- project.list_subprojects - List subprojects/workspaces
- project.get_execution_profile - Detect execution profiles and commands
"""

from typing import Optional
from codebax_mcp.mcp_server.tools.services.project.conventions import get_conventions as _get_conventions
from codebax_mcp.mcp_server.tools.services.project.layout import describe_layout as _describe_layout
from codebax_mcp.mcp_server.tools.services.project.subprojects import list_subprojects as _list_subprojects
from codebax_mcp.mcp_server.tools.services.project.execution import get_execution_profile as _get_execution_profile

from codebax_mcp.mcp_server.models.input import (
    GetConventionsInput,
    DescribeLayoutInput,
    ListSubprojectsInput,
    GetExecutionProfileInput,
)
from codebax_mcp.mcp_server.models.output import (
    ConventionsOutput,
    LayoutOutput,
    SubprojectsOutput,
    ExecutionProfileOutput,
)

# Import MCP server instance for tool registration
from ..app import get_mcp_instance

# Get the MCP instance when tools are imported
mcp = get_mcp_instance()


@mcp.tool(
    title="Get Project Conventions",
    name="project.get_conventions",
    description=(
        "Auto-detect project structure, test framework, tooling, and coding conventions. "
        "Analyzes pyproject.toml, setup.py, package.json, Makefile, and other config files "
        "to understand project structure, test framework (pytest/unittest), code formatters (black/ruff), "
        "type checkers (mypy/pyright), and package managers (uv/poetry/pip/npm). "
        "Returns detected conventions for test configuration, source layout, style preferences, "
        "tooling setup, and project constraints. Useful for understanding project setup before "
        "running other tools."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def project_get_conventions(workspace_root: str, language_hint: Optional[str] = None) -> ConventionsOutput:
    """
    Auto-detect project conventions and structure.

    Analyzes the workspace to detect:
    - Test framework (pytest, unittest, nose)
    - Source code roots and module layout
    - Code style preferences (formatters, type checkers)
    - Tooling (package managers, pre-commit hooks)
    - Project constraints

    Args:
        workspace_root: Path to the workspace root directory
        language_hint: Optional language hint (python, typescript, java, etc.)

    Returns:
        ConventionsOutput with detected conventions for test, source, style, tooling, and constraints

    Examples:
        # Detect conventions in current project
        result = await project_get_conventions(".")
        # Returns: {
        #   "test": {"framework": "pytest", "root": "tests", ...},
        #   "source": {"roots": ["src"], "module_layout": "pyproject", ...},
        #   "style": {"python": {"formatter": "ruff", "type_checker": "pyright"}, ...},
        #   "tooling": {"python": {"manager": "uv", "lock_files": ["uv.lock"]}, ...},
        #   "constraints": {"forbid_creating_dirs": [".git", "__pycache__"], ...}
        # }
    """
    return _get_conventions(GetConventionsInput(
        workspace_root=workspace_root,
        language_hint=language_hint
    ))


@mcp.tool(
    title="Describe Project Layout",
    name="project.describe_layout",
    description=(
        "Output project layer structure and responsibilities. "
        "Scans directory structure to identify project layers (src/, tests/, docs/, etc.) "
        "and their subdirectories. Returns hierarchical view of project organization. "
        "Useful for understanding project structure and identifying where different "
        "components are located."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def project_describe_layout(workspace_root: str) -> LayoutOutput:
    """
    Describe project layer structure and responsibilities.

    Scans the workspace directory structure to identify:
    - Project layers (src, tests, docs, etc.)
    - Subdirectories within each layer
    - Overall directory hierarchy

    Args:
        workspace_root: Path to the workspace root directory

    Returns:
        LayoutOutput with layers and directory structure

    Examples:
        # Get project layout
        result = await project_describe_layout(".")
        # Returns: {
        #   "layers": [
        #     {"name": "src", "purpose": "Source code", "subdirs": ["codebax_mcp", "utils"]},
        #     {"name": "tests", "purpose": "Test code", "subdirs": ["unit_test", "integration_test"]},
        #     {"name": "docs", "purpose": "Documentation", "subdirs": ["contents", "src"]}
        #   ],
        #   "directories": {...}
        # }
    """
    return _describe_layout(DescribeLayoutInput(workspace_root=workspace_root))


@mcp.tool(
    title="List Subprojects",
    name="project.list_subprojects",
    description=(
        "List subprojects and workspaces in the workspace. "
        "Detects Python subprojects (pyproject.toml), Node.js workspaces (package.json), "
        "and Gradle/Maven subprojects (settings.gradle). Returns list of subprojects with "
        "their types, paths, and configuration files. Useful for understanding monorepo "
        "structure and identifying individual projects."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def project_list_subprojects(workspace_root: str) -> SubprojectsOutput:
    """
    List subprojects and workspaces.

    Detects and lists all subprojects in the workspace:
    - Python subprojects (with pyproject.toml)
    - Node.js workspaces (from package.json)
    - Gradle/Maven subprojects (from settings.gradle)

    Args:
        workspace_root: Path to the workspace root directory

    Returns:
        SubprojectsOutput with list of detected subprojects

    Examples:
        # List subprojects
        result = await project_list_subprojects(".")
        # Returns: {
        #   "workspace_root": ".",
        #   "subprojects": [
        #     {"name": "codebax_mcp", "type": "python", "path": "codebax_mcp", "config": "pyproject.toml"},
        #     {"name": "web_app", "type": "node", "path": "web_app", "config": "package.json"}
        #   ],
        #   "total": 2
        # }
    """
    return _list_subprojects(ListSubprojectsInput(workspace_root=workspace_root))


@mcp.tool(
    title="Get Execution Profile",
    name="project.get_execution_profile",
    description=(
        "Detect execution profiles and available commands. "
        "Analyzes Makefile, package.json scripts, and pyproject.toml to identify "
        "available commands (test, lint, format, build, etc.). Detects execution "
        "profiles (development, test, production) with environment variables. "
        "Identifies Python entry points and module entry points. Useful for understanding "
        "how to run tests, lint code, build, and deploy the project."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def project_get_execution_profile(
    workspace_root: str,
    intent: str,
    language: Optional[str] = None,
    package_hint: Optional[str] = None
) -> ExecutionProfileOutput:
    """
    Detect execution profiles and available commands.

    Identifies:
    - Available commands (test, lint, format, build, etc.)
    - Execution profiles (development, test, production)
    - Entry points and how to run the project
    - Environment variables for each profile

    Args:
        workspace_root: Path to the workspace root directory

    Returns:
        ExecutionProfile with profiles, commands, and entry points

    Examples:
        # Get execution profile
        result = await project_get_execution_profile(".")
        # Returns: {
        #   "profiles": [
        #     {"name": "development", "env_vars": {"DEBUG": "true", "LOG_LEVEL": "debug"}},
        #     {"name": "test", "env_vars": {"TESTING": "true", "LOG_LEVEL": "info"}},
        #     {"name": "production", "env_vars": {"DEBUG": "false", "LOG_LEVEL": "warning"}}
        #   ],
        #   "commands": {
        #     "test": "pytest",
        #     "lint": "ruff check .",
        #     "format": "ruff format ."
        #   },
        #   "entry_points": [
        #     {"name": "codebax-mcp", "command": "python -m codebax_mcp.entry", "type": "module"}
        #   ]
        # }
    """
    return _get_execution_profile(GetExecutionProfileInput(
        workspace_root=workspace_root,
        intent=intent,
        language=language,
        package_hint=package_hint
    ))
