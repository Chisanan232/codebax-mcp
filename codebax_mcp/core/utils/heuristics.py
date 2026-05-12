"""Pattern detection heuristics."""

import ast
from typing import Any


def detect_mock_patch_calls(content: str, file_path: str) -> list[dict[str, Any]]:
    """Detect unittest.mock.patch() calls in Python code."""
    try:
        tree = ast.parse(content)
        patches = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check if this is a patch call
                if _is_patch_call(node):
                    patch_info = _extract_patch_info(node, content)
                    if patch_info:
                        patch_info["file"] = file_path
                        patch_info["line"] = node.lineno
                        patches.append(patch_info)

        return patches
    except SyntaxError:
        return []


def _is_patch_call(node: ast.Call) -> bool:
    """Check if a call node is a patch call."""
    func = node.func

    # Direct: patch(...)
    if isinstance(func, ast.Name) and func.id == "patch":
        return True

    # Attribute: unittest.mock.patch(...) or mock.patch(...)
    if isinstance(func, ast.Attribute):
        if func.attr == "patch":
            return True

    return False


def _extract_patch_info(node: ast.Call, content: str) -> dict[str, Any]:
    """Extract information from a patch call."""
    if not node.args:
        return {}

    first_arg = node.args[0]

    # Extract target string
    target = None
    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
        target = first_arg.value
    elif isinstance(first_arg, ast.Str):  # Python 3.7 compatibility
        target = first_arg.s

    if not target:
        return {}

    return {"target": target, "kind": "heuristic", "confidence": 0.7, "type": "mock_patch"}
