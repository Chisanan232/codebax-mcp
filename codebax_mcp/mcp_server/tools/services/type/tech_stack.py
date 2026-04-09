"""type.get_tech_stack_preferences - Analyze project technology preferences."""

import json
import os

from codebax_mcp.mcp_server.models.input import GetTechStackPreferencesInput
from codebax_mcp.mcp_server.models.output import CodingPattern, GetTechStackPreferencesOutput, PackagePreference


def get_tech_stack_preferences(input: GetTechStackPreferencesInput) -> GetTechStackPreferencesOutput:
    """Analyze and return project technology preferences."""
    packages = {}
    patterns = []

    # Detect Python preferences
    if input.language is None or input.language == "python":
        packages = _detect_python_packages(input.workspace_root)
        patterns = _detect_python_patterns(input.workspace_root)

    # Detect Node.js preferences
    if input.language is None or input.language == "typescript" or input.language == "javascript":
        packages.update(_detect_node_packages(input.workspace_root))

    return GetTechStackPreferencesOutput(
        language=input.language or "python", packages=packages, patterns=patterns, examples=[]
    )


def _detect_python_packages(workspace_root: str) -> dict[str, PackagePreference]:
    """Detect Python package preferences."""
    package_configs = {
        "http_client": {
            "preferred": None,
            "candidates": ["httpx", "requests", "aiohttp"],
            "installed": False,
            "notes": None,
        },
        "config": {
            "preferred": None,
            "candidates": ["pydantic-settings", "python-dotenv", "dynaconf"],
            "installed": False,
            "notes": None,
        },
        "orm": {"preferred": None, "candidates": ["SQLModel", "SQLAlchemy"], "installed": False, "notes": None},
        "logging": {"preferred": None, "candidates": ["logging", "structlog"], "installed": False, "notes": None},
        "di": {"preferred": None, "candidates": ["fastapi.Depends", "injector"], "installed": False, "notes": None},
    }

    # Check requirements.txt or pyproject.toml
    requirements = _read_requirements(workspace_root)

    for pkg_name, pkg_info in package_configs.items():
        for candidate in pkg_info["candidates"]:
            if candidate.lower() in requirements:
                pkg_info["preferred"] = candidate
                pkg_info["installed"] = True
                break

    # Convert to PackagePreference models
    packages = {}
    for pkg_name, pkg_info in package_configs.items():
        packages[pkg_name] = PackagePreference(
            preferred=pkg_info["preferred"],
            candidates=pkg_info["candidates"],
            installed=pkg_info["installed"],
            notes=pkg_info["notes"],
        )

    return packages


def _detect_node_packages(workspace_root: str) -> dict[str, PackagePreference]:
    """Detect Node.js package preferences."""
    packages = {}

    package_json_path = os.path.join(workspace_root, "package.json")
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path) as f:
                pkg = json.load(f)

            deps = pkg.get("dependencies", {})
            dev_deps = pkg.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}

            # Detect common packages
            if "react" in all_deps:
                packages["framework"] = PackagePreference(
                    preferred="react", candidates=["react", "vue", "angular"], installed=True
                )
            if "typescript" in all_deps:
                packages["language"] = PackagePreference(
                    preferred="typescript", candidates=["typescript", "javascript"], installed=True
                )
        except json.JSONDecodeError:
            pass

    return packages


def _detect_python_patterns(workspace_root: str) -> list[CodingPattern]:
    """Detect Python coding patterns."""
    patterns = []

    # Look for common patterns in source files
    for root, dirs, files in os.walk(workspace_root):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".venv", "venv"}]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()

                    # Detect patterns
                    if "from pydantic import" in content:
                        patterns.append(
                            CodingPattern(
                                name="use_pydantic_models",
                                description="Use Pydantic for data validation",
                                example_path=os.path.relpath(file_path, workspace_root),
                            )
                        )

                    if "from fastapi import" in content:
                        patterns.append(
                            CodingPattern(
                                name="use_fastapi",
                                description="Use FastAPI for web framework",
                                example_path=os.path.relpath(file_path, workspace_root),
                            )
                        )

                    if "import httpx" in content:
                        patterns.append(
                            CodingPattern(
                                name="use_httpx",
                                description="Use httpx for HTTP client",
                                example_path=os.path.relpath(file_path, workspace_root),
                            )
                        )

                    break  # Just check first file for now
                except Exception:
                    pass

    return patterns


def _read_requirements(workspace_root: str) -> list[str]:
    """Read requirements from requirements.txt or pyproject.toml."""
    requirements = []

    # Check requirements.txt
    req_file = os.path.join(workspace_root, "requirements.txt")
    if os.path.exists(req_file):
        try:
            with open(req_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        pkg_name = line.split("==")[0].split(">=")[0].split("<=")[0].lower()
                        requirements.append(pkg_name)
        except Exception:
            pass

    # Check pyproject.toml
    pyproject_file = os.path.join(workspace_root, "pyproject.toml")
    if os.path.exists(pyproject_file):
        try:
            with open(pyproject_file) as f:
                content = f.read()

            # Simple parsing for dependencies
            in_deps = False
            for line in content.split("\n"):
                if "dependencies" in line:
                    in_deps = True
                elif in_deps and line.startswith("["):
                    break
                elif in_deps and "=" in line:
                    pkg_name = line.split("=")[0].strip().strip("\"'").lower()
                    if pkg_name:
                        requirements.append(pkg_name)
        except Exception:
            pass

    return requirements
