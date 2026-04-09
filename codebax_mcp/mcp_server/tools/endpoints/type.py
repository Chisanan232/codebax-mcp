"""MCP tools for type checking and validation.

Tools:
- type.get_symbol_info - Get function/method/class signature
- type.find_similar_usages - Find usages of similar symbols
- type.get_expected_at_position - Get expected type at position
- type.infer_expression - Infer expression type
- type.validate_changes - Validate code changes for type errors
- type.suggest_fix - Suggest type-related fixes
- type.get_tech_stack_preferences - Analyze tech stack preferences
"""

from typing import Optional, List
from codebax_mcp.mcp_server.tools.services.type.symbol_info import get_symbol_info as _get_symbol_info, find_similar_usages as _find_similar_usages
from codebax_mcp.mcp_server.tools.services.type.inference import get_expected_at_position as _get_expected_at_position, infer_expression as _infer_expression
from codebax_mcp.mcp_server.tools.services.type.validation import validate_changes as _validate_changes, suggest_fix as _suggest_fix
from codebax_mcp.mcp_server.tools.services.type.tech_stack import get_tech_stack_preferences as _get_tech_stack_preferences

from codebax_mcp.mcp_server.models.input import (
    GetSymbolInfoInput,
    ContextRange,
    FindSimilarUsagesInput,
    GetExpectedAtPositionInput,
    InferExpressionInput,
    ValidateChangesInput,
    Change,
    SuggestFixInput,
    GetTechStackPreferencesInput,
)
from codebax_mcp.mcp_server.models.output import (
    GetSymbolInfoOutput,
    FindSimilarUsagesOutput,
    GetExpectedAtPositionOutput,
    InferExpressionOutput,
    ValidateChangesOutput,
    SuggestFixOutput,
    GetTechStackPreferencesOutput,
)

# Import MCP server instance for tool registration
from ..app import get_mcp_instance

# Get the MCP instance when tools are imported
mcp = get_mcp_instance()


@mcp.tool(
    title="Get Symbol Type Information",
    name="type.get_symbol_info",
    description=(
        "Get function/method/class signature and type information. "
        "Retrieves symbol metadata including name, kind, language, definition location, "
        "function signature, and docstring. Requires Pyright integration for full type information (Phase 6). "
        "Useful for understanding what a symbol does and its interface."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def type_get_symbol_info(
    symbol: str,
    file: Optional[str] = None,
    language: str = "python",
    context_range: Optional[ContextRange] = None,
    workspace_root: str = ".",
) -> GetSymbolInfoOutput:
    """Get function/method/class signature and return type.
    
    Args:
        symbol: Symbol name to look up
        file: Optional file path for disambiguation
        language: Programming language
        context_range: Optional context range for disambiguation
        workspace_root: Path to the workspace root directory
    
    Returns:
        GetSymbolInfoOutput with signature and type information
    """
    return _get_symbol_info(GetSymbolInfoInput(symbol=symbol, file=file, language=language, context_range=context_range, workspace_root=workspace_root))


@mcp.tool(
    title="Find Similar Symbol Usages",
    name="type.find_similar_usages",
    description=(
        "Find usages of symbols similar to the given symbol. "
        "Searches for symbols with similar names or compatible types. "
        "Requires type information for full accuracy (Phase 6). "
        "Useful for finding related symbols and understanding type compatibility."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def type_find_similar_usages(
    symbol: str, language: str = "python", workspace_root: str = "."
) -> FindSimilarUsagesOutput:
    """Find usages of similar symbols.
    
    Args:
        symbol: Symbol name to find similar usages for
        language: Programming language (default: python)
        workspace_root: Path to the workspace root directory
    
    Returns:
        FindSimilarUsagesOutput with similar usage locations
    """
    return _find_similar_usages(FindSimilarUsagesInput(symbol=symbol, language=language, workspace_root=workspace_root))


@mcp.tool(
    title="Get Expected Type at Position",
    name="type.get_expected_at_position",
    description=(
        "Get the expected type at a specific code position. "
        "Analyzes the code context to determine what type is expected at a location. "
        "Requires Pyright LSP integration for full accuracy (Phase 6). "
        "Useful for understanding type requirements and catching type mismatches."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def type_get_expected_at_position(
    file: str, line: int, column: int, language: str = "python", workspace_root: str = "."
) -> GetExpectedAtPositionOutput:
    """Get expected type at a specific code position.
    
    Args:
        file: File path (relative to workspace_root)
        line: Line number (1-indexed)
        column: Column number (0-indexed)
        language: Programming language (default: python)
        workspace_root: Path to the workspace root directory
    
    Returns:
        GetExpectedAtPositionOutput with expected type information
    """
    return _get_expected_at_position(GetExpectedAtPositionInput(file=file, line=line, column=column, language=language, workspace_root=workspace_root))


@mcp.tool(
    title="Infer Expression Type",
    name="type.infer_expression",
    description=(
        "Infer the type of an expression. "
        "Analyzes an expression in context to determine its type. "
        "Requires Pyright LSP integration for full accuracy (Phase 6). "
        "Useful for understanding expression types and catching type errors."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def type_infer_expression(
    file: str,
    expression: str,
    language: str = "python",
    context_range: Optional[ContextRange] = None,
    workspace_root: str = ".",
) -> InferExpressionOutput:
    """Infer type of an expression.
    
    Args:
        file: Path to the file
        expression: Expression to infer type for
        language: Programming language
        context_range: Optional context range for analysis
        workspace_root: Path to the workspace root directory
    
    Returns:
        InferExpressionOutput with inferred type
    """
    return _infer_expression(InferExpressionInput(file=file, expression=expression, language=language, context_range=context_range, workspace_root=workspace_root))


@mcp.tool(
    title="Validate Code Changes",
    name="type.validate_changes",
    description=(
        "Validate code changes for type errors using Pyright. "
        "Runs Pyright type checker on modified files and returns diagnostics. "
        "Categorizes results as errors, warnings, or info. Supports dry-run mode. "
        "Useful for catching type errors before committing changes."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def type_validate_changes(
    file: str,
    changes: List[Change],
    language: str = "python",
    dry_run: bool = True,
    workspace_root: str = ".",
) -> ValidateChangesOutput:
    """Validate proposed code changes.
    
    Args:
        file: Path to the file
        changes: List of changes to validate
        language: Programming language
        dry_run: If True, only validate without applying
        workspace_root: Path to the workspace root directory
    
    Returns:
        ValidateChangesOutput with validation results
    """
    return _validate_changes(ValidateChangesInput(file=file, changes=changes, language=language, dry_run=dry_run, workspace_root=workspace_root))


@mcp.tool(
    title="Suggest Type Fix",
    name="type.suggest_fix",
    description=(
        "Suggest type-related fixes for errors. "
        "Analyzes type errors and suggests fixes like adding imports, type annotations, or casts. "
        "Uses heuristic-based suggestions for common error patterns. "
        "Requires advanced type analysis for full accuracy (Phase 6+). "
        "Useful for quickly fixing type errors."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def type_suggest_fix(
    file: str,
    line: int,
    column: int,
    error_message: str,
    language: str = "python",
    workspace_root: str = ".",
) -> SuggestFixOutput:
    """Suggest type-related fixes for errors.
    
    Args:
        file: File path containing the error (relative to workspace_root)
        line: Line number of the error (1-indexed)
        column: Column number of the error (0-indexed)
        error_message: Error message to suggest fixes for
        language: Programming language (default: python)
        workspace_root: Path to the workspace root directory
    
    Returns:
        SuggestFixOutput with suggested fixes
    """
    return _suggest_fix(SuggestFixInput(file=file, line=line, column=column, error_message=error_message, language=language, workspace_root=workspace_root))


@mcp.tool(
    title="Get Tech Stack Preferences",
    name="type.get_tech_stack_preferences",
    description=(
        "Analyze and return project technology preferences. "
        "Scans requirements.txt, pyproject.toml, and package.json to detect preferred packages "
        "and libraries. Identifies coding patterns in source files. Returns preferred packages "
        "for HTTP clients, configuration, ORM, logging, and dependency injection. "
        "Useful for understanding project conventions and making consistent choices."
    ),
    annotations={
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def type_get_tech_stack_preferences(
    workspace_root: str, language: Optional[str] = None
) -> GetTechStackPreferencesOutput:
    """Analyze and return project technology preferences.
    
    Args:
        workspace_root: Path to the workspace root directory
        language: Optional language hint (python, typescript, etc.)
    
    Returns:
        GetTechStackPreferencesOutput with detected tech stack preferences
    """
    return _get_tech_stack_preferences(GetTechStackPreferencesInput(workspace_root=workspace_root, language=language))


