"""type.get_symbol_info and type.find_similar_usages - Type information tools."""

import os
from typing import Dict, Any, List, Optional
from codebax_mcp.core.index import LockFileStore
from codebax_mcp.mcp_server.models.input import GetSymbolInfoInput, FindSimilarUsagesInput
from codebax_mcp.mcp_server.models.output import (
    GetSymbolInfoOutput, 
    FindSimilarUsagesOutput, 
    OverloadInfo, 
    SimilarSymbol,
    SignatureInfo,
    ParameterInfo,
    ReturnType,
    NormalizedType,
    DefinedIn
)


def get_symbol_info(input: GetSymbolInfoInput) -> GetSymbolInfoOutput:
    """Get function/method/class signature and return type."""
    
    try:
        # Load index
        store = LockFileStore(os.path.join(input.workspace_root, ".codebax_index.lock"))
        index_data = store.load()
        
        if not index_data:
            return GetSymbolInfoOutput(
                symbol=input.symbol,
                kind="unknown",
                language=input.language,
                defined_in=DefinedIn(file="", line=0, column=0),
                signature=SignatureInfo(
                    parameters=[],
                    return_type=ReturnType(
                        raw=None,
                        normalized=NormalizedType(kind="unknown", types=[])
                    )
                ),
                confidence=0.0,
                overloads=[],
                notes="Index not found"
            )
        
        # Search for symbol
        for symbol_data in index_data.get("symbol_definitions", {}).values():
            if symbol_data.get("name") == input.symbol:
                range_data = symbol_data.get("range", {})
                return GetSymbolInfoOutput(
                    symbol=input.symbol,
                    kind=symbol_data.get("kind", "unknown"),
                    language=input.language,
                    defined_in=DefinedIn(
                        file=symbol_data.get("file", ""),
                        line=range_data.get("line_start", 0),
                        column=range_data.get("column_start", 0)
                    ),
                    signature=SignatureInfo(
                        parameters=[],
                        return_type=ReturnType(
                            raw=symbol_data.get("signature"),
                            normalized=NormalizedType(kind="unknown", types=[])
                        )
                    ),
                    confidence=0.7,
                    docstring=symbol_data.get("docstring"),
                    overloads=[],
                    notes="Type information requires Pyright integration (Phase 6)"
                )
        
        return GetSymbolInfoOutput(
            symbol=input.symbol,
            kind="unknown",
            language=input.language,
            defined_in=DefinedIn(file="", line=0, column=0),
            signature=SignatureInfo(
                parameters=[],
                return_type=ReturnType(
                    raw=None,
                    normalized=NormalizedType(kind="unknown", types=[])
                )
            ),
            confidence=0.0,
            overloads=[],
            notes="Symbol not found. Type information requires Pyright integration (Phase 6)"
        )
    
    except Exception as e:
        return GetSymbolInfoOutput(
            symbol=input.symbol,
            kind="unknown",
            language=input.language,
            defined_in=DefinedIn(file="", line=0, column=0),
            signature=SignatureInfo(
                parameters=[],
                return_type=ReturnType(
                    raw=None,
                    normalized=NormalizedType(kind="unknown", types=[])
                )
            ),
            confidence=0.0,
            overloads=[],
            notes=f"Error: {str(e)}"
        )


def find_similar_usages(input: FindSimilarUsagesInput) -> FindSimilarUsagesOutput:
    """Find usages of similar symbols."""
    
    try:
        # Load index
        store = LockFileStore(os.path.join(input.workspace_root, ".codebax_index.lock"))
        index_data = store.load()
        
        if not index_data:
            return FindSimilarUsagesOutput(
                symbol=input.symbol,
                similar_symbols=[],
                usages=[],
                total=0,
                notes="Index not found"
            )
        
        # Find symbols with similar names
        similar_symbols = []
        for symbol_data in index_data.get("symbol_definitions", {}).values():
            if symbol_data.get("language") == input.language:
                name = symbol_data.get("name", "")
                if name.lower() == input.symbol.lower() or name.endswith(input.symbol):
                    similar_symbols.append(SimilarSymbol(
                        symbol_id=symbol_data.get("symbol_id"),
                        name=name,
                        kind=symbol_data.get("kind"),
                        file=symbol_data.get("file"),
                        similarity_score=1.0 if name.lower() == input.symbol.lower() else 0.8
                    ))
        
        return FindSimilarUsagesOutput(
            symbol=input.symbol,
            similar_symbols=similar_symbols,
            usages=[],
            total=len(similar_symbols),
            notes="Similar symbol detection requires type information (Phase 6)"
        )
    
    except Exception as e:
        return FindSimilarUsagesOutput(
            symbol=input.symbol,
            similar_symbols=[],
            usages=[],
            total=0,
            notes=f"Error: {str(e)}"
        )
