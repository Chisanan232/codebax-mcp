"""project.get_execution_profile - Detect execution profiles and commands."""

import os

from codebax_mcp.mcp_server.models.input import GetExecutionProfileInput
from codebax_mcp.mcp_server.models.output import ExecutionProfileOutput


def get_execution_profile(input: GetExecutionProfileInput) -> ExecutionProfileOutput:
    """Detect execution profiles and commands."""
    # Detect the appropriate command based on intent
    command = _detect_command_for_intent(input.workspace_root, input.intent)
    cwd = input.workspace_root
    pre_steps = _detect_pre_steps(input.workspace_root, input.intent)

    return ExecutionProfileOutput(command=command, cwd=cwd, pre_steps=pre_steps)


def _detect_command_for_intent(workspace_root: str, intent: str) -> str:
    """Detect the appropriate command based on intent."""
    if intent == "test":
        return _detect_test_command(workspace_root)
    if intent == "lint":
        return _detect_lint_command(workspace_root)
    if intent == "build":
        return _detect_build_command(workspace_root)
    if intent == "format":
        return _detect_format_command(workspace_root)
    if intent == "install_deps":
        return _detect_install_command(workspace_root)
    return "echo 'Unknown intent'"


def _detect_test_command(workspace_root: str) -> str:
    """Detect test command."""
    if os.path.exists(os.path.join(workspace_root, "pytest.ini")):
        return "pytest"
    if os.path.exists(os.path.join(workspace_root, "package.json")):
        return "npm test"
    return "python -m pytest"


def _detect_lint_command(workspace_root: str) -> str:
    """Detect lint command."""
    if os.path.exists(os.path.join(workspace_root, "ruff.toml")):
        return "ruff check ."
    if os.path.exists(os.path.join(workspace_root, ".eslintrc.json")):
        return "npm run lint"
    return "echo 'No linter configured'"


def _detect_build_command(workspace_root: str) -> str:
    """Detect build command."""
    if os.path.exists(os.path.join(workspace_root, "package.json")):
        return "npm run build"
    if os.path.exists(os.path.join(workspace_root, "setup.py")):
        return "python setup.py build"
    return "echo 'No build configured'"


def _detect_format_command(workspace_root: str) -> str:
    """Detect format command."""
    if os.path.exists(os.path.join(workspace_root, "ruff.toml")):
        return "ruff format ."
    if os.path.exists(os.path.join(workspace_root, ".prettierrc")):
        return "npm run format"
    return "echo 'No formatter configured'"


def _detect_install_command(workspace_root: str) -> str:
    """Detect dependency installation command."""
    if os.path.exists(os.path.join(workspace_root, "uv.lock")):
        return "uv sync"
    if os.path.exists(os.path.join(workspace_root, "requirements.txt")):
        return "pip install -r requirements.txt"
    if os.path.exists(os.path.join(workspace_root, "package.json")):
        return "npm install"
    return "echo 'No dependency file found'"


def _detect_pre_steps(workspace_root: str, intent: str) -> list[str]:
    """Detect pre-execution steps."""
    pre_steps = []

    # Add virtual environment activation if needed
    if os.path.exists(os.path.join(workspace_root, ".venv")):
        pre_steps.append("source .venv/bin/activate")

    return pre_steps
