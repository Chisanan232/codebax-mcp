"""MCP tools for test discovery and generation.

Tools:
- test.locate_for_source - Find or suggest test files for source
- test.create_or_update_for_symbol - Create or update tests for symbols
"""

from codebax_mcp.mcp_server.models.input import (
    CreateOrUpdateForSymbolInput,
    LocateForSourceInput,
)
from codebax_mcp.mcp_server.models.output import (
    CreateOrUpdateForSymbolOutput,
    LocateForSourceOutput,
)
from codebax_mcp.mcp_server.tools.services.test.create_update import (
    create_or_update_for_symbol as _create_or_update_for_symbol,
)
from codebax_mcp.mcp_server.tools.services.test.locate import locate_for_source as _locate_for_source

# Import MCP server instance for tool registration
from ..app import get_mcp_instance

# Get the MCP instance when tools are imported
mcp = get_mcp_instance()


@mcp.tool(
    title="Locate Test File for Source",
    name="test.locate_for_source",
    description=(
        "Find existing test files for a source file or suggest where to create a new test. "
        "Searches for test files matching common patterns (test_*.py, *_test.py, etc.) "
        "in the tests directory. Detects test framework used (pytest, unittest, nose). "
        "If no existing test is found, suggests a path for creating a new test file. "
        "Useful for understanding test organization and finding where to add tests for a source file."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def test_locate_for_source(source_path: str, workspace_root: str = ".") -> LocateForSourceOutput:
    """Find existing test files for a source file or suggest test path.

    Searches for test files matching common naming patterns and detects the test framework.
    If no existing test is found, suggests where to create a new test file.

    Args:
        source_path: Path to the source file (relative to workspace_root)
        workspace_root: Path to the workspace root directory (default: ".")

    Returns:
        Dictionary with:
        - existing_tests: List of found test files with framework and confidence
        - suggested_new_test_path: Suggested path for new test if none found
        - notes: Additional information

    Examples:
        # Find tests for a source file
        result = await test_locate_for_source("codebax_mcp/core/parser.py")
        # Returns: {
        #   "source_path": "codebax_mcp/core/parser.py",
        #   "existing_tests": [
        #     {"path": "tests/test_parser.py", "framework": "pytest", "confidence": 0.9}
        #   ],
        #   "suggested_new_test_path": None
        # }

        # When no test exists
        result = await test_locate_for_source("codebax_mcp/new_module.py")
        # Returns: {
        #   "source_path": "codebax_mcp/new_module.py",
        #   "existing_tests": [],
        #   "suggested_new_test_path": "tests/test_new_module.py"
        # }

    """
    return _locate_for_source(LocateForSourceInput(source_path=source_path, workspace_root=workspace_root))


@mcp.tool(
    title="Create or Update Test for Symbol",
    name="test.create_or_update_for_symbol",
    description=(
        "Create or update test for a specific symbol (function, class, method). "
        "Generates test code based on behavior description and symbol type. "
        "Creates test file if it doesn't exist. Supports add/update/delete operations. "
        "Integrates with project structure and test framework conventions. "
        "Useful for generating test stubs and maintaining test coverage as code evolves."
    ),
    annotations={
        "destructiveHint": True,
        "openWorldHint": True,
    },
)
async def test_create_or_update_for_symbol(
    source_path: str,
    symbol: str,
    language: str,
    intent: str,
    behavior_description: str,
    workspace_root: str = ".",
) -> CreateOrUpdateForSymbolOutput:
    """Create or update test for a specific symbol.

    Generates test code for a function, class, or method based on the behavior description.
    Creates or updates the test file as needed.

    Args:
        source_path: Path to the source file containing the symbol
        symbol: Name of the symbol (function, class, or method)
        language: Programming language (python, typescript, java, etc.)
        intent: Operation intent - "add_or_update" or "delete"
        behavior_description: Description of what the symbol should do (for test generation)
        workspace_root: Path to the workspace root directory (default: ".")

    Returns:
        Dictionary with:
        - status: "ok" or "failed"
        - test_files_modified: List of modified test files with changes summary
        - error: Error message if failed
        - notes: Additional information

    Examples:
        # Create test for a new function
        result = await test_create_or_update_for_symbol(
            source_path="codebax_mcp/core/parser.py",
            symbol="parse_file",
            language="python",
            intent="add_or_update",
            behavior_description="Parse Python file and extract symbols"
        )
        # Returns: {
        #   "status": "ok",
        #   "test_files_modified": [
        #     {"path": "tests/test_parser.py", "changes_summary": "Added/updated test for parse_file"}
        #   ]
        # }

        # Delete test for a removed function
        result = await test_create_or_update_for_symbol(
            source_path="codebax_mcp/core/parser.py",
            symbol="deprecated_function",
            language="python",
            intent="delete",
            behavior_description=""
        )

    """
    return _create_or_update_for_symbol(
        CreateOrUpdateForSymbolInput(
            source_path=source_path,
            symbol=symbol,
            language=language,
            intent=intent,
            behavior_description=behavior_description,
            workspace_root=workspace_root,
        )
    )
