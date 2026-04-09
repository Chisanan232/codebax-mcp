"""code.analyze_python_patch_calls - Analyze mock.patch calls."""

import os

from codebax_mcp.core.utils import detect_mock_patch_calls, find_python_files
from codebax_mcp.mcp_server.models.input import AnalyzePythonPatchCallsInput
from codebax_mcp.mcp_server.models.output import AnalyzePythonPatchCallsOutput, PatchCall


def analyze_python_patch_calls(input: AnalyzePythonPatchCallsInput) -> AnalyzePythonPatchCallsOutput:
    """Find and analyze unittest.mock.patch() calls."""
    try:
        # Find all Python files
        python_files = find_python_files(input.workspace_root)

        patches = []
        by_target = {}

        # Analyze each file
        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                patch_calls = detect_mock_patch_calls(content, file_path)

                for patch in patch_calls:
                    patch_call = PatchCall(
                        file=os.path.relpath(patch.get("file"), input.workspace_root),
                        line=patch.get("line"),
                        target=patch.get("target"),
                        kind=patch.get("kind"),
                        confidence=patch.get("confidence"),
                    )
                    patches.append(patch_call)

                    # Group by target
                    target = patch.get("target")
                    if target not in by_target:
                        by_target[target] = []
                    by_target[target].append(os.path.relpath(file_path, input.workspace_root))

            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

        return AnalyzePythonPatchCallsOutput(patches=patches, total=len(patches), by_target=by_target)

    except Exception as e:
        return AnalyzePythonPatchCallsOutput(patches=[], total=0, by_target={}, notes=f"Error: {e!s}")
