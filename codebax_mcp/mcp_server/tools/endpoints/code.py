"""MCP tools for code analysis, navigation, refactoring, and search.

Tools:
- code.index - Build or update codebase index
- code.identify_symbol - Identify symbol at location
- code.get_definition - Get symbol definition
- code.find_usages - Find all usages of symbol
- code.get_call_graph - Build call graph
- code.rename_symbol - Rename symbol safely
- code.extract_function - Extract code to function
- code.semantic_search - Search by natural language
- code.analyze_python_patch_calls - Analyze mock.patch calls
"""

from typing import Optional, List, Dict, Any
from codebax_mcp.mcp_server.tools.services.code.index import index_codebase as _index_codebase
from codebax_mcp.mcp_server.tools.services.code.navigation import (
    identify_symbol as _identify_symbol,
    get_definition as _get_definition,
    find_usages as _find_usages,
    get_call_graph as _get_call_graph,
)
from codebax_mcp.mcp_server.tools.services.code.refactoring import (
    rename_symbol as _rename_symbol,
    extract_function as _extract_function,
)
from codebax_mcp.mcp_server.tools.services.code.search import semantic_search as _semantic_search
from codebax_mcp.mcp_server.tools.services.code.python_tools import analyze_python_patch_calls as _analyze_python_patch_calls

from codebax_mcp.mcp_server.models.input import (
    IndexCodebaseInput,
    IdentifySymbolInput,
    GetDefinitionInput,
    FindUsagesInput,
    GetCallGraphInput,
    RenameSymbolInput,
    ExtractFunctionInput,
    CodeRange,
    SemanticSearchInput,
    AnalyzePythonPatchCallsInput,
)
from codebax_mcp.mcp_server.models.output import (
    IndexCodebaseOutput,
    IdentifySymbolOutput,
    GetDefinitionOutput,
    FindUsagesOutput,
    GetCallGraphOutput,
    RenameSymbolOutput,
    ExtractFunctionOutput,
    SemanticSearchOutput,
    AnalyzePythonPatchCallsOutput,
)

# Import MCP server instance for tool registration
from ..app import get_mcp_instance

# Get the MCP instance when tools are imported
mcp = get_mcp_instance()


@mcp.tool(
    title="Index Codebase",
    name="code.index",
    description=(
        "Build or update codebase index for fast symbol lookup. "
        "Parses all Python files in the workspace using Python AST to extract symbols "
        "(functions, classes, methods, variables). Persists index to lock file with atomic writes "
        "and checksum verification. Supports full or incremental indexing. "
        "Required before using other code analysis tools. Typical latency: <5 seconds for 1000 files."
    ),
    annotations={
        "readOnlyHint": False,
        "openWorldHint": True,
    },
)
async def code_index(workspace_root: str, full: bool = False, paths: Optional[List[str]] = None) -> IndexCodebaseOutput:
    """Build or update codebase index.
    
    Args:
        workspace_root: Path to the workspace root directory
        full: Whether to do a full reindex (default: incremental)
        paths: Optional list of specific paths to index
    
    Returns:
        IndexCodebaseOutput with status, files indexed, and symbols found
    """
    return _index_codebase(IndexCodebaseInput(workspace_root=workspace_root, full=full, paths=paths))


@mcp.tool(
    title="Identify Symbol at Location",
    name="code.identify_symbol",
    description=(
        "Identify the symbol at a specific code location (file, line, column). "
        "Looks up the symbol in the index and returns its ID, name, kind (function/class/method), "
        "and definition location. Useful for understanding what symbol is at a cursor position. "
        "Requires index to be built first with code.index."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def code_identify_symbol(
    file: str, language: str, line: int, column: int, workspace_root: str = "."
) -> IdentifySymbolOutput:
    """Identify symbol at a specific location.
    
    Args:
        file: File path (relative to workspace_root)
        language: Programming language (default: python)
        line: Line number (1-indexed)
        column: Column number (0-indexed)
        workspace_root: Path to the workspace root directory
    
    Returns:
        IdentifySymbolOutput with symbol information
    """
    return _identify_symbol(IdentifySymbolInput(file=file, language=language, line=line, column=column, workspace_root=workspace_root))


@mcp.tool(
    title="Get Symbol Definition",
    name="code.get_definition",
    description=(
        "Get the definition of a symbol by its ID. Returns symbol metadata including name, kind, "
        "language, definition location, signature, and docstring. Useful for understanding what "
        "a symbol does and where it's defined."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def code_get_definition(symbol_id: str, workspace_root: str = ".") -> GetDefinitionOutput:
    """Get symbol definition.
    
    Args:
        symbol_id: Unique symbol identifier
        workspace_root: Path to the workspace root directory
    
    Returns:
        GetDefinitionOutput with definition location and details
    """
    return _get_definition(GetDefinitionInput(symbol_id=symbol_id, workspace_root=workspace_root))


@mcp.tool(
    title="Find Symbol Usages",
    name="code.find_usages",
    description=(
        "Find all usages of a symbol in the codebase. Searches the index for references to the symbol "
        "and returns their locations. Can filter to exclude test files. Returns usage locations with "
        "confidence scores (exact matches have higher confidence). Useful for understanding impact of "
        "changes and finding all places where a symbol is used."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def code_find_usages(
    symbol_id: str,
    include_tests: bool = False,
    max_results: Optional[int] = None,
    workspace_root: str = ".",
) -> FindUsagesOutput:
    """Find all usages of a symbol.
    
    Args:
        symbol_id: Unique symbol identifier
        include_tests: Whether to include test files in search
        max_results: Maximum number of results to return
        workspace_root: Path to the workspace root directory
    
    Returns:
        FindUsagesOutput with list of usage locations
    """
    return _find_usages(FindUsagesInput(symbol_id=symbol_id, include_tests=include_tests, max_results=max_results, workspace_root=workspace_root))


@mcp.tool(
    title="Get Call Graph",
    name="code.get_call_graph",
    description=(
        "Build call graph for a symbol showing what it calls and what calls it. "
        "Supports direction filtering (incoming, outgoing, both) and depth limiting. "
        "Requires LSP integration for full accuracy (Phase 3+). "
        "Useful for understanding function dependencies and impact analysis."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def code_get_call_graph(
    symbol_id: str, direction: str = "both", depth: int = 3, workspace_root: str = "."
) -> GetCallGraphOutput:
    """Build call graph for a symbol.
    
    Args:
        symbol_id: Unique symbol identifier
        direction: Direction to traverse (incoming, outgoing, both)
        depth: Maximum depth to traverse (default: 3)
        workspace_root: Path to the workspace root directory
    
    Returns:
        GetCallGraphOutput with calls and callers
    """
    return _get_call_graph(GetCallGraphInput(symbol_id=symbol_id, direction=direction, depth=depth, workspace_root=workspace_root))


@mcp.tool(
    title="Rename Symbol",
    name="code.rename_symbol",
    description=(
        "Rename a symbol safely across the codebase. Supports dry-run mode to preview changes "
        "before applying. Requires LSP integration for full accuracy (Phase 3+). "
        "Useful for refactoring and maintaining consistency across the codebase."
    ),
    annotations={
        "destructiveHint": True,
        "openWorldHint": True,
    },
)
async def code_rename_symbol(
    symbol_id: str, new_name: str, dry_run: bool = True, workspace_root: str = "."
) -> RenameSymbolOutput:
    """Rename a symbol safely.
    
    Args:
        symbol_id: Unique symbol identifier
        new_name: New name for the symbol
        dry_run: If True, only preview changes without applying them
        workspace_root: Path to the workspace root directory
    
    Returns:
        RenameSymbolOutput with list of changes
    """
    return _rename_symbol(RenameSymbolInput(symbol_id=symbol_id, new_name=new_name, dry_run=dry_run, workspace_root=workspace_root))


@mcp.tool(
    title="Extract Function",
    name="code.extract_function",
    description=(
        "Extract code range to a new function. Supports dry-run mode to preview changes. "
        "Requires Tree-sitter integration for full accuracy (Phase 3+). "
        "Analyzes variable dependencies and generates function signature automatically. "
        "Useful for refactoring and improving code organization."
    ),
    annotations={
        "destructiveHint": True,
        "openWorldHint": True,
    },
)
async def code_extract_function(
    file: str,
    language: str,
    range: CodeRange,
    new_name: str,
    dry_run: bool = True,
    workspace_root: str = ".",
) -> ExtractFunctionOutput:
    """Extract a code block into a new function.
    
    Args:
        file: Path to the file
        language: Programming language
        range: Code range to extract
        new_name: Name for the extracted function
        dry_run: If True, only return proposed changes
        workspace_root: Path to the workspace root directory
    
    Returns:
        ExtractFunctionOutput with proposed changes
    """
    return _extract_function(ExtractFunctionInput(file=file, language=language, range=range, new_name=new_name, dry_run=dry_run, workspace_root=workspace_root))


@mcp.tool(
    title="Semantic Search",
    name="code.semantic_search",
    description=(
        "Search code by natural language query. MVP uses keyword-based search on symbol names and docstrings. "
        "Scores results based on keyword matches. Supports filtering by language and file path. "
        "Returns top-k results sorted by relevance. Ready for embedding-based semantic search (Phase 5.5+). "
        "Useful for finding relevant code without knowing exact symbol names."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def code_semantic_search(
    query: str,
    top_k: int = 10,
    filter_language: Optional[str] = None,
    filter_path_prefix: Optional[str] = None,
    workspace_root: str = ".",
) -> SemanticSearchOutput:
    """Search code by natural language query.
    
    Args:
        query: Natural language search query
        top_k: Maximum number of results to return
        filter_language: Optional language filter (python, typescript, etc.)
        filter_path_prefix: Optional path prefix filter
        workspace_root: Path to the workspace root directory
    
    Returns:
        SemanticSearchOutput with ranked search results
    """
    return _semantic_search(SemanticSearchInput(query=query, top_k=top_k, filter_language=filter_language, filter_path_prefix=filter_path_prefix, workspace_root=workspace_root))


@mcp.tool(
    title="Analyze Python Patch Calls",
    name="code.analyze_python_patch_calls",
    description=(
        "Find and analyze all unittest.mock.patch() calls in Python codebase. "
        "Detects patch targets and groups results by target. Returns confidence scores "
        "indicating detection method (exact vs. heuristic). Useful for understanding test mocking "
        "patterns and identifying potential issues with mocked dependencies."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def code_analyze_python_patch_calls(workspace_root: str = ".") -> AnalyzePythonPatchCallsOutput:
    """Find and analyze unittest.mock.patch() calls.
    
    Args:
        workspace_root: Path to the workspace root directory
    
    Returns:
        AnalyzePythonPatchCallsOutput with patch analysis
    """
    return _analyze_python_patch_calls(AnalyzePythonPatchCallsInput(workspace_root=workspace_root))
