"""Pydantic models for code tools input/output."""

from pydantic import BaseModel


# Input Models
class IndexCodebaseInput(BaseModel):
    workspace_root: str
    full: bool = False
    paths: list[str] | None = None


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
    range_start: dict[str, int]
    range_end: dict[str, int]
    new_name: str
    dry_run: bool = True
    workspace_root: str = "."


class SemanticSearchInput(BaseModel):
    query: str
    workspace_root: str = "."
    top_k: int = 10
    filter_language: str | None = None
    filter_path: str | None = None


class AnalyzePythonPatchCallsInput(BaseModel):
    workspace_root: str = "."


# Output Models
class IndexCodebaseOutput(BaseModel):
    status: str
    indexed_files: int
    skipped_files: int
    error: str | None = None
    notes: str | None = None


class SymbolLocation(BaseModel):
    file: str
    line: int
    column: int


class IdentifySymbolOutput(BaseModel):
    symbol_id: str | None = None
    name: str | None = None
    kind: str | None = None
    language: str
    defined_in: SymbolLocation | None = None
    notes: str | None = None


class GetDefinitionOutput(BaseModel):
    symbol_id: str
    name: str | None = None
    kind: str | None = None
    language: str | None = None
    defined_in: SymbolLocation | None = None
    signature: str | None = None
    docstring: str | None = None
    notes: str | None = None


class Usage(BaseModel):
    file: str
    line: int
    column: int
    kind: str
    confidence: float


class FindUsagesOutput(BaseModel):
    symbol_id: str
    usages: list[Usage] = []
    total: int = 0
    notes: str | None = None


class SearchResult(BaseModel):
    symbol_id: str
    name: str
    file: str
    kind: str
    score: float
    docstring: str | None = None


class SemanticSearchOutput(BaseModel):
    query: str
    results: list[SearchResult] = []
    total: int = 0
    notes: str | None = None


class PatchCall(BaseModel):
    file: str
    line: int
    target: str
    kind: str
    confidence: float


class AnalyzePythonPatchCallsOutput(BaseModel):
    patches: list[PatchCall] = []
    total: int = 0
    by_target: dict[str, list[str]] = {}
    notes: str | None = None
