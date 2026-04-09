"""Pydantic models for type tools input/output."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# Input Models
class GetSymbolInfoInput(BaseModel):
    symbol: str
    file: Optional[str] = None
    language: str = "python"
    context_range: Optional[Dict[str, int]] = None
    workspace_root: str = "."


class FindSimilarUsagesInput(BaseModel):
    symbol: str
    language: str = "python"
    workspace_root: str = "."


class GetExpectedAtPositionInput(BaseModel):
    file: str
    line: int
    column: int
    language: str = "python"
    workspace_root: str = "."


class InferExpressionInput(BaseModel):
    file: str
    expression: str
    language: str = "python"
    context_range: Optional[Dict[str, int]] = None
    workspace_root: str = "."


class ValidateChangesInput(BaseModel):
    file: str
    changes: List[Dict[str, Any]]
    language: str = "python"
    dry_run: bool = True
    workspace_root: str = "."


class SuggestFixInput(BaseModel):
    file: str
    line: int
    column: int
    error_message: str
    language: str = "python"
    workspace_root: str = "."


class GetTechStackPreferencesInput(BaseModel):
    workspace_root: str
    language: Optional[str] = None


# Output Models
class SymbolInfoOutput(BaseModel):
    symbol: str
    kind: Optional[str] = None
    language: str
    defined_in: Optional[Dict[str, Any]] = None
    signature: Optional[str] = None
    docstring: Optional[str] = None
    overloads: List[Dict[str, Any]] = []
    notes: Optional[str] = None


class SimilarSymbol(BaseModel):
    symbol_id: str
    name: str
    kind: str
    file: str


class FindSimilarUsagesOutput(BaseModel):
    symbol: str
    similar_symbols: List[SimilarSymbol] = []
    usages: List[Dict[str, Any]] = []
    total: int = 0
    notes: Optional[str] = None


class GetExpectedAtPositionOutput(BaseModel):
    file: str
    line: int
    column: int
    expected_type: Optional[str] = None
    possible_values: List[str] = []
    context: Optional[str] = None
    notes: Optional[str] = None


class InferExpressionOutput(BaseModel):
    expression: str
    inferred_type: Optional[str] = None
    confidence: float = 0.0
    notes: Optional[str] = None


class Diagnostic(BaseModel):
    file: str
    line: int
    column: int
    message: str
    severity: str
    code: Optional[str] = None


class ValidateChangesOutput(BaseModel):
    status: str
    file: str
    diagnostics: List[Diagnostic] = []
    errors: List[Diagnostic] = []
    warnings: List[Diagnostic] = []
    error: Optional[str] = None
    notes: Optional[str] = None


class SuggestFixOutput(BaseModel):
    file: str
    line: int
    column: int
    suggestions: List[str] = []
    patches: List[Dict[str, Any]] = []
    notes: Optional[str] = None


class PackageInfo(BaseModel):
    preferred: Optional[str] = None
    candidates: List[str] = []
    installed: bool = False
    notes: Optional[str] = None


class Pattern(BaseModel):
    name: str
    description: str
    example_path: Optional[str] = None


class Example(BaseModel):
    file: str
    language: str
    summary: str


class TechStackPreferencesOutput(BaseModel):
    language: str
    packages: Dict[str, PackageInfo] = {}
    patterns: List[Pattern] = []
    examples: List[Example] = []
    notes: Optional[str] = None
