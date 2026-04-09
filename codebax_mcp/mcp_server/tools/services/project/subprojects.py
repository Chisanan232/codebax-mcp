"""project.list_subprojects - List subprojects/workspaces."""

import json
import os

from codebax_mcp.mcp_server.models.input import ListSubprojectsInput
from codebax_mcp.mcp_server.models.output import SubprojectInfo, SubprojectsOutput


def list_subprojects(input: ListSubprojectsInput) -> SubprojectsOutput:
    """List subprojects and workspaces."""
    subprojects = []

    # Check for Python workspaces (pyproject.toml with tool.poetry.packages or similar)
    if os.path.exists(os.path.join(input.workspace_root, "pyproject.toml")):
        subprojects.extend(_detect_python_subprojects(input.workspace_root))

    # Check for Node.js workspaces
    if os.path.exists(os.path.join(input.workspace_root, "package.json")):
        subprojects.extend(_detect_node_subprojects(input.workspace_root))

    # Check for Gradle/Maven subprojects
    if os.path.exists(os.path.join(input.workspace_root, "settings.gradle")):
        subprojects.extend(_detect_gradle_subprojects(input.workspace_root))

    return SubprojectsOutput(workspace_root=input.workspace_root, subprojects=subprojects, total=len(subprojects))


def _detect_python_subprojects(workspace_root: str) -> list[SubprojectInfo]:
    """Detect Python subprojects."""
    subprojects = []

    # Look for subdirectories with pyproject.toml
    for item in os.listdir(workspace_root):
        path = os.path.join(workspace_root, item)
        if os.path.isdir(path) and not item.startswith("."):
            if os.path.exists(os.path.join(path, "pyproject.toml")):
                subprojects.append(SubprojectInfo(name=item, type="python", path=item, config="pyproject.toml"))

    return subprojects


def _detect_node_subprojects(workspace_root: str) -> list[SubprojectInfo]:
    """Detect Node.js subprojects."""
    subprojects = []

    try:
        with open(os.path.join(workspace_root, "package.json")) as f:
            pkg = json.load(f)

        # Check for workspaces
        workspaces = pkg.get("workspaces", [])
        for ws in workspaces:
            subprojects.append(SubprojectInfo(name=ws, type="node", path=ws, config="package.json"))
    except (json.JSONDecodeError, FileNotFoundError):
        pass

    return subprojects


def _detect_gradle_subprojects(workspace_root: str) -> list[SubprojectInfo]:
    """Detect Gradle subprojects."""
    subprojects = []

    try:
        with open(os.path.join(workspace_root, "settings.gradle")) as f:
            content = f.read()

        # Simple parsing for include statements
        for line in content.split("\n"):
            if line.strip().startswith("include"):
                # Extract project names
                parts = line.split("'")
                if len(parts) >= 2:
                    project_name = parts[1]
                    subprojects.append(
                        SubprojectInfo(
                            name=project_name, type="gradle", path=project_name.replace(":", "/"), config="build.gradle"
                        )
                    )
    except FileNotFoundError:
        pass

    return subprojects
