"""Code refactoring tools - rename, extract function."""

from codebax_mcp.mcp_server.models.input import ExtractFunctionInput, RenameSymbolInput
from codebax_mcp.mcp_server.models.output import ExtractFunctionOutput, RenameSymbolOutput


def rename_symbol(input: RenameSymbolInput) -> RenameSymbolOutput:
    """Rename a symbol safely."""
    return RenameSymbolOutput(
        status="ok",
        symbol_id=input.symbol_id,
        new_name=input.new_name,
        changes=[],
        notes="Rename feature requires LSP integration for full accuracy (Phase 3+)",
    )


def extract_function(input: ExtractFunctionInput) -> ExtractFunctionOutput:
    """Extract code to a new function."""
    return ExtractFunctionOutput(
        status="ok",
        file=input.file,
        new_function_name=input.new_name,
        changes=[],
        notes="Extract function feature requires Tree-sitter integration (Phase 3+)",
    )
