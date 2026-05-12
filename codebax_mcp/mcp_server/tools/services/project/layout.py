"""project.describe_layout - Output project layer structure."""

import os
from typing import Any

from codebax_mcp.mcp_server.models.input import DescribeLayoutInput
from codebax_mcp.mcp_server.models.output import LayoutOutput, ModuleInfo


def describe_layout(input: DescribeLayoutInput) -> LayoutOutput:
    """Describe project layer structure and responsibilities."""
    # Detect common modules
    modules = []
    roots = []
    test_roots = []

    if os.path.isdir(os.path.join(input.workspace_root, "src")):
        roots.append("src")
        modules.append(ModuleInfo(type="source", path="src", description="Source code"))

    if os.path.isdir(os.path.join(input.workspace_root, "tests")):
        test_roots.append("tests")
        modules.append(ModuleInfo(type="test", path="tests", description="Test code"))

    if os.path.isdir(os.path.join(input.workspace_root, "docs")):
        modules.append(ModuleInfo(type="documentation", path="docs", description="Documentation"))

    return LayoutOutput(
        roots=roots, modules=modules, test_roots=test_roots, directories=_scan_directories(input.workspace_root)
    )


def _scan_directories(workspace_root: str, max_depth: int = 2, current_depth: int = 0) -> dict[str, Any]:
    """Scan directory structure."""
    if current_depth >= max_depth:
        return {}

    result = {}

    try:
        for item in os.listdir(workspace_root):
            if item.startswith("."):
                continue

            path = os.path.join(workspace_root, item)
            if os.path.isdir(path):
                result[item] = {"type": "directory", "subdirs": _scan_directories(path, max_depth, current_depth + 1)}
    except PermissionError:
        pass

    return result


def _list_subdirs(directory: str) -> list[str]:
    """List subdirectories."""
    try:
        return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d)) and not d.startswith(".")]
    except (PermissionError, FileNotFoundError):
        return []
