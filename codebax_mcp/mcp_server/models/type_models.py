"""Pydantic models for type tools input/output."""

from typing import Any

from pydantic import BaseModel


# Input Models
class GetSymbolInfoInput(BaseModel):
    symbol: str
    file: str | None = None
    language: str = "python"
    context_range: dict[str, int] | None = None
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
    context_range: dict[str, int] | None = None
    workspace_root: str = "."


class ValidateChangesInput(BaseModel):
    file: str
    changes: list[dict[str, Any]]
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
    language: str | None = None


# Output Models
class SymbolInfoOutput(BaseModel):
    symbol: str
    kind: str | None = None
    language: str
    defined_in: dict[str, Any] | None = None
    signature: str | None = None
    docstring: str | None = None
    overloads: list[dict[str, Any]] = []
    notes: str | None = None


class SimilarSymbol(BaseModel):
    symbol_id: str
    name: str
    kind: str
    file: str


class FindSimilarUsagesOutput(BaseModel):
    symbol: str
    similar_symbols: list[SimilarSymbol] = []
    usages: list[dict[str, Any]] = []
    total: int = 0
    notes: str | None = None


class GetExpectedAtPositionOutput(BaseModel):
    file: str
    line: int
    column: int
    expected_type: str | None = None
    possible_values: list[str] = []
    context: str | None = None
    notes: str | None = None


class InferExpressionOutput(BaseModel):
    expression: str
    inferred_type: str | None = None
    confidence: float = 0.0
    notes: str | None = None


class Diagnostic(BaseModel):
    file: str
    line: int
    column: int
    message: str
    severity: str
    code: str | None = None


class ValidateChangesOutput(BaseModel):
    status: str
    file: str
    diagnostics: list[Diagnostic] = []
    errors: list[Diagnostic] = []
    warnings: list[Diagnostic] = []
    error: str | None = None
    notes: str | None = None


class SuggestFixOutput(BaseModel):
    file: str
    line: int
    column: int
    suggestions: list[str] = []
    patches: list[dict[str, Any]] = []
    notes: str | None = None


class PackageInfo(BaseModel):
    preferred: str | None = None
    candidates: list[str] = []
    installed: bool = False
    notes: str | None = None


class Pattern(BaseModel):
    name: str
    description: str
    example_path: str | None = None


class Example(BaseModel):
    file: str
    language: str
    summary: str


class TechStackPreferencesOutput(BaseModel):
    language: str
    packages: dict[str, PackageInfo] = {}
    patterns: list[Pattern] = []
    examples: list[Example] = []
    notes: str | None = None
