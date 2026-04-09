"""Pydantic models for code tools input/output."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# Input Models
class IndexCodebaseInput(BaseModel):
    workspace_root: str
    full: bool = False
    paths: Optional[List[str]] = None


class IdentifySymbolInput(BaseModel):
    file: str
    language: str
    line: int
    column: int
    workspace_root: str = "."


class GetDefinitionInput(BaseModel):
    symbol_id: str
    workspace_root: str = "."


class FindUsagesInput(BaseModel):
    symbol_id: str
    include_tests: bool = False
    trust_level: str = "exact"
    workspace_root: str = "."


class GetCallGraphInput(BaseModel):
    symbol_id: str
    direction: str = "both"
    depth: int = 3
    workspace_root: str = "."


class RenameSymbolInput(BaseModel):
    symbol_id: str
    new_name: str
    dry_run: bool = True
    workspace_root: str = "."


class ExtractFunctionInput(BaseModel):
    file: str
    language: str
    range_start: Dict[str, int]
    range_end: Dict[str, int]
    new_name: str
    dry_run: bool = True
    workspace_root: str = "."


class SemanticSearchInput(BaseModel):
    query: str
    workspace_root: str = "."
    top_k: int = 10
    filter_language: Optional[str] = None
    filter_path: Optional[str] = None


class AnalyzePythonPatchCallsInput(BaseModel):
    workspace_root: str = "."


# Output Models
class IndexCodebaseOutput(BaseModel):
    status: str
    indexed_files: int
    skipped_files: int
    error: Optional[str] = None
    notes: Optional[str] = None


class SymbolLocation(BaseModel):
    file: str
    line: int
    column: int


class IdentifySymbolOutput(BaseModel):
    symbol_id: Optional[str] = None
    name: Optional[str] = None
    kind: Optional[str] = None
    language: str
    defined_in: Optional[SymbolLocation] = None
    notes: Optional[str] = None


class GetDefinitionOutput(BaseModel):
    symbol_id: str
    name: Optional[str] = None
    kind: Optional[str] = None
    language: Optional[str] = None
    defined_in: Optional[SymbolLocation] = None
    signature: Optional[str] = None
    docstring: Optional[str] = None
    notes: Optional[str] = None


class Usage(BaseModel):
    file: str
    line: int
    column: int
    kind: str
    confidence: float


class FindUsagesOutput(BaseModel):
    symbol_id: str
    usages: List[Usage] = []
    total: int = 0
    notes: Optional[str] = None


class SearchResult(BaseModel):
    symbol_id: str
    name: str
    file: str
    kind: str
    score: float
    docstring: Optional[str] = None


class SemanticSearchOutput(BaseModel):
    query: str
    results: List[SearchResult] = []
    total: int = 0
    notes: Optional[str] = None


class PatchCall(BaseModel):
    file: str
    line: int
    target: str
    kind: str
    confidence: float


class AnalyzePythonPatchCallsOutput(BaseModel):
    patches: List[PatchCall] = []
    total: int = 0
    by_target: Dict[str, List[str]] = {}
    notes: Optional[str] = None
