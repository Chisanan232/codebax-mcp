"""Output models for code analysis, navigation, refactoring, and search tools."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class IndexCodebaseOutput(BaseModel):
    """Output for code.index tool."""
    
    status: str = Field(..., description="Status: 'ok' or 'failed'")
    indexed_files: int = Field(0, description="Number of successfully indexed files")
    skipped_files: int = Field(0, description="Number of files that failed to parse")
    error: Optional[str] = Field(None, description="Error message if failed")
    notes: Optional[str] = Field(None, description="Additional information")


class DefinitionLocation(BaseModel):
    """Location information for a symbol definition."""
    
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")
    column: int = Field(..., description="Column number")


class IdentifySymbolOutput(BaseModel):
    """Output for code.identify_symbol tool."""
    
    symbol_id: str = Field(..., description="Unique identifier for the symbol")
    name: str = Field(..., description="Symbol name")
    kind: str = Field(..., description="Symbol kind (function, class, method, variable, etc.)")
    language: str = Field(..., description="Programming language")
    defined_in: DefinitionLocation = Field(..., description="Definition location")
    notes: Optional[str] = Field(None, description="Additional information")


class GetDefinitionOutput(BaseModel):
    """Output for code.get_definition tool."""
    
    symbol_id: str = Field(..., description="The symbol ID")
    name: str = Field(..., description="Symbol name")
    kind: str = Field(..., description="Symbol kind (function, class, method, etc.)")
    language: str = Field(..., description="Programming language")
    defined_in: DefinitionLocation = Field(..., description="Definition location")
    signature: Optional[str] = Field(None, description="Function/method signature")
    docstring: Optional[str] = Field(None, description="Documentation string")
    notes: Optional[str] = Field(None, description="Additional information")


class UsageLocation(BaseModel):
    """Location information for a symbol usage."""
    
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")
    column: int = Field(..., description="Column number")
    kind: str = Field(..., description="Usage kind (exact, heuristic, dynamic)")
    snippet: str = Field(..., description="Code snippet")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    notes: Optional[str] = Field(None, description="Additional information")


class FindUsagesOutput(BaseModel):
    """Output for code.find_usages tool."""
    
    symbol_id: str = Field(..., description="The symbol ID")
    usages: List[UsageLocation] = Field(
        default_factory=list,
        description="List of usage locations"
    )
    total: int = Field(0, description="Total number of usages found")
    notes: Optional[str] = Field(None, description="Additional information")


class CallGraphNode(BaseModel):
    """Node in the call graph."""
    
    symbol_id: str = Field(..., description="Symbol ID")
    name: str = Field(..., description="Symbol name")


class CallGraphEdge(BaseModel):
    """Edge in the call graph."""
    
    from_: str = Field(..., alias="from", description="Source symbol ID")
    to: str = Field(..., description="Target symbol ID")
    kind: str = Field(..., description="Edge kind")


class GetCallGraphOutput(BaseModel):
    """Output for code.get_call_graph tool."""
    
    symbol_id: str = Field(..., description="The symbol ID")
    direction: str = Field(..., description="Direction traversed")
    nodes: List[CallGraphNode] = Field(
        default_factory=list,
        description="Nodes in the call graph"
    )
    edges: List[CallGraphEdge] = Field(
        default_factory=list,
        description="Edges in the call graph"
    )
    notes: Optional[str] = Field(None, description="Additional information")


class CodeChange(BaseModel):
    """Information about a proposed code change."""
    
    file: str = Field(..., description="File path")
    old_text: str = Field(..., description="Old text")
    new_text: str = Field(..., description="New text")
    line: int = Field(..., description="Line number")


class RenameSymbolOutput(BaseModel):
    """Output for code.rename_symbol tool."""
    
    status: str = Field(..., description="Status: 'ok' or 'failed'")
    symbol_id: str = Field(..., description="The symbol ID")
    new_name: str = Field(..., description="The new name")
    changes: List[CodeChange] = Field(
        default_factory=list,
        description="List of proposed changes"
    )
    error: Optional[str] = Field(None, description="Error message if failed")


class ExtractFunctionOutput(BaseModel):
    """Output for code.extract_function tool."""
    
    status: str = Field(..., description="Status: 'ok' or 'failed'")
    file: str = Field(..., description="The file path")
    new_function_name: str = Field(..., description="Name of the new function")
    changes: List[CodeChange] = Field(
        default_factory=list,
        description="List of proposed changes"
    )
    error: Optional[str] = Field(None, description="Error message if failed")


class SearchResult(BaseModel):
    """A search result."""
    
    file: str = Field(..., description="File path")
    line_start: int = Field(..., description="Start line number")
    line_end: int = Field(..., description="End line number")
    snippet: str = Field(..., description="Code snippet")
    score: float = Field(..., description="Relevance score")
    language: str = Field(..., description="Programming language")


class SemanticSearchOutput(BaseModel):
    """Output for code.semantic_search tool."""
    
    query: str = Field(..., description="The search query")
    results: List[SearchResult] = Field(
        default_factory=list,
        description="List of matching symbols with scores"
    )
    total: int = Field(0, description="Total number of results")
    notes: Optional[str] = Field(None, description="Information about search method")


class PatchCall(BaseModel):
    """Information about a mock.patch call."""
    
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")
    target: str = Field(..., description="Patch target string")
    kind: str = Field(..., description="Detection kind (exact, heuristic)")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")


class AnalyzePythonPatchCallsOutput(BaseModel):
    """Output for code.analyze_python_patch_calls tool."""
    
    patches: List[PatchCall] = Field(
        default_factory=list,
        description="List of patch calls with target, location, and confidence"
    )
    total: int = Field(0, description="Total number of patches found")
    by_target: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Patches grouped by target string"
    )
    notes: Optional[str] = Field(None, description="Additional information")
