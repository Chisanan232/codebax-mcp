"""project.get_conventions - Auto-detect project conventions."""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from codebax_mcp.mcp_server.models.input import GetConventionsInput
from codebax_mcp.mcp_server.models.output import ConventionsOutput


def get_conventions(input: GetConventionsInput) -> ConventionsOutput:
    """Analyze project directory and auto-detect conventions."""
    
    return ConventionsOutput(
        test=_detect_test_config(input.workspace_root),
        source=_detect_source_config(input.workspace_root),
        style=_detect_style_config(input.workspace_root),
        tooling=_detect_tooling_config(input.workspace_root),
        constraints=_detect_constraints(input.workspace_root)
    )


def _detect_test_config(workspace_root: str) -> Dict[str, Any]:
    """Detect test configuration."""
    test_config = {
        "root": "tests",
        "framework": None,
        "file_patterns": [],
        "naming_style": None
    }
    
    # Check for pytest
    if os.path.exists(os.path.join(workspace_root, "pytest.ini")):
        test_config["framework"] = "pytest"
        test_config["file_patterns"] = ["test_*.py", "*_test.py"]
        test_config["naming_style"] = "test_*"
    
    # Check for unittest
    elif os.path.exists(os.path.join(workspace_root, "tests")):
        test_config["framework"] = "unittest"
        test_config["file_patterns"] = ["test_*.py"]
        test_config["naming_style"] = "test_*"
    
    return test_config


def _detect_source_config(workspace_root: str) -> Dict[str, Any]:
    """Detect source code configuration."""
    source_config = {
        "roots": [],
        "module_layout": None
    }
    
    # Check for common source directories
    for dir_name in ["src", "lib", "codebax_mcp", "app"]:
        if os.path.isdir(os.path.join(workspace_root, dir_name)):
            source_config["roots"].append(dir_name)
    
    if not source_config["roots"]:
        source_config["roots"] = ["."]
    
    # Detect module layout
    if os.path.exists(os.path.join(workspace_root, "pyproject.toml")):
        source_config["module_layout"] = "pyproject"
    elif os.path.exists(os.path.join(workspace_root, "setup.py")):
        source_config["module_layout"] = "setup.py"
    
    return source_config


def _detect_style_config(workspace_root: str) -> Dict[str, Any]:
    """Detect code style configuration."""
    style_config = {
        "python": {
            "formatter": None,
            "type_checker": None
        },
        "typescript": {
            "formatter": None,
            "test_framework": None
        }
    }
    
    # Check for Python formatters
    if os.path.exists(os.path.join(workspace_root, ".black")):
        style_config["python"]["formatter"] = "black"
    elif os.path.exists(os.path.join(workspace_root, "pyproject.toml")):
        style_config["python"]["formatter"] = "ruff"
    
    # Check for type checkers
    if os.path.exists(os.path.join(workspace_root, "mypy.ini")):
        style_config["python"]["type_checker"] = "mypy"
    elif os.path.exists(os.path.join(workspace_root, "pyrightconfig.json")):
        style_config["python"]["type_checker"] = "pyright"
    
    return style_config


def _detect_tooling_config(workspace_root: str) -> Dict[str, Any]:
    """Detect project tooling configuration."""
    tooling_config = {
        "python": {
            "manager": None,
            "entry": None,
            "lock_files": [],
            "test_command": None,
            "lint_commands": [],
            "pre_commit": {
                "enabled": False,
                "config": None,
                "run_command": None
            }
        },
        "node": {
            "manager": None,
            "root_package_json": None,
            "workspace": {
                "enabled": False,
                "tool": None,
                "config": None
            },
            "scripts": {
                "test": None,
                "lint": None,
                "build": None
            }
        },
        "jvm": {
            "build_tool": None,
            "wrapper": None,
            "subprojects": [],
            "test_command": None
        }
    }
    
    # Detect Python package manager
    if os.path.exists(os.path.join(workspace_root, "uv.lock")):
        tooling_config["python"]["manager"] = "uv"
        tooling_config["python"]["lock_files"] = ["uv.lock"]
    elif os.path.exists(os.path.join(workspace_root, "poetry.lock")):
        tooling_config["python"]["manager"] = "poetry"
        tooling_config["python"]["lock_files"] = ["poetry.lock"]
    elif os.path.exists(os.path.join(workspace_root, "requirements.txt")):
        tooling_config["python"]["manager"] = "pip"
        tooling_config["python"]["lock_files"] = ["requirements.txt"]
    
    # Detect pre-commit
    if os.path.exists(os.path.join(workspace_root, ".pre-commit-config.yaml")):
        tooling_config["python"]["pre_commit"]["enabled"] = True
        tooling_config["python"]["pre_commit"]["config"] = ".pre-commit-config.yaml"
    
    return tooling_config


def _detect_constraints(workspace_root: str) -> Dict[str, Any]:
    """Detect project constraints."""
    return {
        "forbid_creating_dirs": [".git", "__pycache__", ".venv"],
        "prefer_existing_over_new": True
    }
