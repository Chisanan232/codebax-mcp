"""code.semantic_search - Search code by natural language query."""

import os
from typing import Dict, Any, List
from codebax_mcp.core.index import LockFileStore
from codebax_mcp.mcp_server.models.input import SemanticSearchInput
from codebax_mcp.mcp_server.models.output import SemanticSearchOutput, SearchResult


def semantic_search(input: SemanticSearchInput) -> SemanticSearchOutput:
    """Search code by natural language query."""
    
    try:
        # Load index
        store = LockFileStore(os.path.join(input.workspace_root, ".codebax_index.lock"))
        index_data = store.load()
        
        if not index_data:
            return SemanticSearchOutput(
                query=input.query,
                results=[],
                total=0,
                notes="Index not found"
            )
        
        # Simple keyword search
        query_words = input.query.lower().split()
        matches = []
        
        for file_path, symbols in index_data.get("file_symbols", {}).items():
            if input.filter_path and input.filter_path not in file_path:
                continue
            
            for symbol in symbols:
                if input.filter_language and symbol.get("language") != input.filter_language:
                    continue
                
                # Score based on keyword matches
                name = symbol.get("name", "").lower()
                docstring = symbol.get("docstring", "").lower()
                
                score = 0
                for word in query_words:
                    if word in name:
                        score += 2
                    if word in docstring:
                        score += 1
                
                if score > 0:
                    matches.append(SearchResult(
                        symbol_id=symbol.get("symbol_id"),
                        name=symbol.get("name"),
                        file=file_path,
                        kind=symbol.get("kind"),
                        score=score,
                        docstring=symbol.get("docstring")
                    ))
        
        # Sort by score and limit
        matches.sort(key=lambda x: x.score, reverse=True)
        results = matches[:input.top_k]
        
        return SemanticSearchOutput(
            query=input.query,
            results=results,
            total=len(results),
            notes="MVP: Keyword-based search. Full semantic search requires embeddings (Phase 5.5+)"
        )
    
    except Exception as e:
        return SemanticSearchOutput(
            query=input.query,
            results=[],
            total=0,
            notes=f"Error: {str(e)}"
        )
