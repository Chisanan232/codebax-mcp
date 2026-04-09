"""test.locate_for_source - Find or suggest test file for source file."""

import os
from typing import Dict, Any, List, Optional
from codebax_mcp.mcp_server.models.input import LocateForSourceInput
from codebax_mcp.mcp_server.models.output import LocateForSourceOutput, ExistingTest


def locate_for_source(input: LocateForSourceInput) -> LocateForSourceOutput:
    """Find existing test files for a source file or suggest test path."""
    
    # Find existing tests
    existing_tests = _find_existing_tests(input.source_path, input.workspace_root)
    
    # Suggest new test path if none found
    suggested_path = None
    if not existing_tests:
        suggested_path = _suggest_test_path(input.source_path, input.workspace_root)
    
    return LocateForSourceOutput(
        source_path=input.source_path,
        existing_tests=existing_tests,
        suggested_new_test_path=suggested_path
    )


def _find_existing_tests(source_path: str, workspace_root: str) -> List[ExistingTest]:
    """Find existing test files for a source file."""
    tests = []
    
    # Get source file name without extension
    source_name = os.path.splitext(os.path.basename(source_path))[0]
    
    # Common test patterns
    test_patterns = [
        f"test_{source_name}.py",
        f"{source_name}_test.py",
        f"test{source_name.capitalize()}.py",
    ]
    
    # Search in tests directory
    tests_dir = os.path.join(workspace_root, "tests")
    if os.path.isdir(tests_dir):
        for root, dirs, files in os.walk(tests_dir):
            for file in files:
                if file in test_patterns or file.startswith(f"test_{source_name}"):
                    test_path = os.path.join(root, file)
                    tests.append(ExistingTest(
                        path=os.path.relpath(test_path, workspace_root),
                        framework=_detect_test_framework(test_path) or "unknown",
                        confidence=0.9
                    ))
    
    return tests


def _suggest_test_path(source_path: str, workspace_root: str) -> Optional[str]:
    """Suggest a test path for a source file."""
    source_name = os.path.splitext(os.path.basename(source_path))[0]
    
    # Suggest test path based on source location
    if "src" in source_path:
        suggested = os.path.join(workspace_root, "tests", f"test_{source_name}.py")
    else:
        suggested = os.path.join(workspace_root, "tests", f"test_{source_name}.py")
    
    return os.path.relpath(suggested, workspace_root)


def _detect_test_framework(test_file: str) -> Optional[str]:
    """Detect test framework from test file."""
    try:
        with open(test_file, 'r') as f:
            content = f.read()
        
        if "import pytest" in content or "from pytest" in content:
            return "pytest"
        elif "import unittest" in content or "from unittest" in content:
            return "unittest"
        elif "import nose" in content:
            return "nose"
    except Exception:
        pass
    
    return None
