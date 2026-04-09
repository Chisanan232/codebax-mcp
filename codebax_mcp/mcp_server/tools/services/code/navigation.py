"""Code navigation tools - identify, definition, usages, call graph."""

import os
from typing import Dict, Any, List, Optional
from codebax_mcp.core.parser import PythonParser
from codebax_mcp.core.index import SymbolIndex, LockFileStore
from codebax_mcp.core.utils import calculate_confidence
from codebax_mcp.mcp_server.models.input import (
    IdentifySymbolInput,
    GetDefinitionInput,
    FindUsagesInput,
    GetCallGraphInput,
)
from codebax_mcp.mcp_server.models.output import (
    IdentifySymbolOutput,
    GetDefinitionOutput,
    FindUsagesOutput,
    GetCallGraphOutput,
    DefinitionLocation,
    UsageLocation,
    CallGraphNode,
)


def identify_symbol(input: IdentifySymbolInput) -> IdentifySymbolOutput:
    """Identify symbol at a specific location."""
    
    try:
        # Load index
        store = LockFileStore(os.path.join(input.workspace_root, ".codebax_index.lock"))
        index_data = store.load()
        
        if not index_data:
            return IdentifySymbolOutput(
                symbol_id="",
                name="",
                kind="unknown",
                language=input.language,
                defined_in=DefinitionLocation(file="", line=0, column=0),
                notes="Index not found, rebuilding..."
            )
        
        # Find symbol at location
        file_symbols = index_data.get("file_symbols", {}).get(input.file, [])
        
        for symbol_data in file_symbols:
            range_data = symbol_data.get("range", {})
            if (range_data.get("line_start") <= input.line <= range_data.get("line_end")):
                return IdentifySymbolOutput(
                    symbol_id=symbol_data.get("symbol_id"),
                    name=symbol_data.get("name"),
                    kind=symbol_data.get("kind"),
                    language=input.language,
                    defined_in=DefinitionLocation(
                        file=symbol_data.get("file"),
                        line=range_data.get("line_start"),
                        column=range_data.get("column_start")
                    )
                )
        
        return IdentifySymbolOutput(
            symbol_id="",
            name="",
            kind="unknown",
            language=input.language,
            defined_in=DefinitionLocation(file="", line=0, column=0),
            notes="Symbol not found at specified location"
        )
    
    except Exception as e:
        return IdentifySymbolOutput(
            symbol_id="",
            name="",
            kind="unknown",
            language=input.language,
            defined_in=DefinitionLocation(file="", line=0, column=0),
            notes=f"Error: {str(e)}"
        )


def get_definition(input: GetDefinitionInput) -> GetDefinitionOutput:
    """Get symbol definition."""
    
    try:
        # Load index
        store = LockFileStore(os.path.join(input.workspace_root, ".codebax_index.lock"))
        index_data = store.load()
        
        if not index_data:
            return GetDefinitionOutput(
                symbol_id=input.symbol_id,
                name="",
                kind="unknown",
                language="",
                defined_in=DefinitionLocation(file="", line=0, column=0),
                notes="Index not found"
            )
        
        # Find symbol
        symbol_data = index_data.get("symbol_definitions", {}).get(input.symbol_id)
        
        if symbol_data:
            range_data = symbol_data.get("range", {})
            return GetDefinitionOutput(
                symbol_id=input.symbol_id,
                name=symbol_data.get("name"),
                kind=symbol_data.get("kind"),
                language=symbol_data.get("language"),
                defined_in=DefinitionLocation(
                    file=symbol_data.get("file"),
                    line=range_data.get("line_start"),
                    column=range_data.get("column_start")
                ),
                signature=symbol_data.get("signature"),
                docstring=symbol_data.get("docstring")
            )
        
        return GetDefinitionOutput(
            symbol_id=input.symbol_id,
            name="",
            kind="unknown",
            language="",
            defined_in=DefinitionLocation(file="", line=0, column=0),
            notes="Symbol not found in index"
        )
    
    except Exception as e:
        return GetDefinitionOutput(
            symbol_id=input.symbol_id,
            name="",
            kind="unknown",
            language="",
            defined_in=DefinitionLocation(file="", line=0, column=0),
            notes=f"Error: {str(e)}"
        )


def find_usages(input: FindUsagesInput) -> FindUsagesOutput:
    """Find all usages of a symbol."""
    
    try:
        # Load index
        store = LockFileStore(os.path.join(input.workspace_root, ".codebax_index.lock"))
        index_data = store.load()
        
        if not index_data:
            return FindUsagesOutput(
                symbol_id=input.symbol_id,
                usages=[],
                total=0,
                notes="Index not found"
            )
        
        # Search for usages (simplified - just find matching names)
        symbol_data = index_data.get("symbol_definitions", {}).get(input.symbol_id)
        if not symbol_data:
            return FindUsagesOutput(
                symbol_id=input.symbol_id,
                usages=[],
                total=0
            )
        
        symbol_name = symbol_data.get("name")
        usages = []
        
        # Search in all files
        for file_path, symbols in index_data.get("file_symbols", {}).items():
            if not input.include_tests and "test" in file_path:
                continue
            
            for sym in symbols:
                if sym.get("name") == symbol_name and sym.get("symbol_id") != input.symbol_id:
                    range_data = sym.get("range", {})
                    usages.append(UsageLocation(
                        file=file_path,
                        line=range_data.get("line_start"),
                        column=range_data.get("column_start"),
                        kind="exact",
                        confidence=1.0
                    ))
        
        return FindUsagesOutput(
            symbol_id=input.symbol_id,
            usages=usages,
            total=len(usages)
        )
    
    except Exception as e:
        return FindUsagesOutput(
            symbol_id=input.symbol_id,
            usages=[],
            total=0,
            notes=f"Error: {str(e)}"
        )


def get_call_graph(input: GetCallGraphInput) -> GetCallGraphOutput:
    """Build call graph for a symbol."""
    
    return GetCallGraphOutput(
        symbol_id=input.symbol_id,
        nodes=[],
        edges=[],
        direction=input.direction,
        notes="Call graph feature requires LSP integration (Phase 3+)"
    )
