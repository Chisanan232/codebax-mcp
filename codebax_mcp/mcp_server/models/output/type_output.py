"""Output models for type checking and validation tools."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ParameterInfo(BaseModel):
    """Information about a function parameter."""
    
    name: str = Field(..., description="Parameter name")
    type: Optional[str] = Field(None, description="Parameter type")
    optional: Optional[bool] = Field(None, description="Whether parameter is optional")
    default: Optional[str] = Field(None, description="Default value")


class TypeInfo(BaseModel):
    """Type information."""
    
    kind: str = Field(..., description="Type kind")
    name: str = Field(..., description="Type name")


class NormalizedType(BaseModel):
    """Normalized type representation."""
    
    kind: str = Field(..., description="Type kind (union, optional, generic, etc.)")
    types: List[TypeInfo] = Field(
        default_factory=list,
        description="List of types"
    )


class ReturnType(BaseModel):
    """Return type information."""
    
    raw: Optional[str] = Field(None, description="Raw return type string")
    normalized: NormalizedType = Field(..., description="Normalized return type")


class SignatureInfo(BaseModel):
    """Function signature information."""
    
    parameters: List[ParameterInfo] = Field(
        default_factory=list,
        description="Function parameters"
    )
    return_type: ReturnType = Field(..., description="Return type")
    async_: Optional[bool] = Field(None, alias="async", description="Whether function is async")


class OverloadInfo(BaseModel):
    """Information about a function overload."""
    
    parameters: List[ParameterInfo] = Field(
        default_factory=list,
        description="Overload parameters"
    )
    return_type: ReturnType = Field(..., description="Overload return type")


class DefinedIn(BaseModel):
    """Definition location."""
    
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")
    column: int = Field(..., description="Column number")


class GetSymbolInfoOutput(BaseModel):
    """Output for type.get_symbol_info tool."""
    
    symbol: str = Field(..., description="The symbol name")
    kind: str = Field(..., description="Symbol kind (function, class, method, etc.)")
    language: str = Field(..., description="Programming language")
    defined_in: DefinedIn = Field(..., description="Definition location")
    signature: SignatureInfo = Field(..., description="Function/method signature")
    docstring: Optional[str] = Field(None, description="Documentation string")
    overloads: List[OverloadInfo] = Field(
        default_factory=list,
        description="List of overloaded signatures"
    )
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    notes: Optional[str] = Field(None, description="Additional information")


class SimilarSymbol(BaseModel):
    """Information about a similar symbol."""
    
    symbol_id: str = Field(..., description="Symbol ID")
    name: str = Field(..., description="Symbol name")
    kind: str = Field(..., description="Symbol kind")
    file: str = Field(..., description="File path")
    similarity_score: float = Field(..., description="Similarity score (0.0-1.0)")


class FindSimilarUsagesOutput(BaseModel):
    """Output for type.find_similar_usages tool."""
    
    symbol: str = Field(..., description="The original symbol")
    similar_symbols: List[SimilarSymbol] = Field(
        default_factory=list,
        description="List of similar symbols with metadata"
    )
    usages: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of usage locations"
    )
    total: int = Field(0, description="Total number of similar symbols found")
    notes: Optional[str] = Field(None, description="Additional information")


class SuggestedSymbol(BaseModel):
    """Suggested symbol information."""
    
    name: str = Field(..., description="Symbol name")
    symbol: str = Field(..., description="Symbol identifier")
    return_type_raw: Optional[str] = Field(None, description="Raw return type")


class ExpectedType(BaseModel):
    """Expected type information."""
    
    raw: Optional[str] = Field(None, description="Raw type string")
    normalized: NormalizedType = Field(..., description="Normalized type")


class Position(BaseModel):
    """Position information."""
    
    line: int = Field(..., description="Line number")
    column: int = Field(..., description="Column number")


class GetExpectedAtPositionOutput(BaseModel):
    """Output for type.get_expected_at_position tool."""
    
    file: str = Field(..., description="The file path")
    position: Position = Field(..., description="Position information")
    expected_type: ExpectedType = Field(..., description="Expected type at position")
    context: Optional[str] = Field(None, description="Context information")
    suggested_symbols: List[SuggestedSymbol] = Field(
        default_factory=list,
        description="Suggested symbols"
    )
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    notes: Optional[str] = Field(None, description="Additional information")


class InferredType(BaseModel):
    """Inferred type information."""
    
    raw: Optional[str] = Field(None, description="Raw type string")
    normalized: NormalizedType = Field(..., description="Normalized type")


class InferExpressionOutput(BaseModel):
    """Output for type.infer_expression tool."""
    
    file: str = Field(..., description="The file path")
    expression: str = Field(..., description="The expression")
    inferred_type: InferredType = Field(..., description="Inferred type")
    source: str = Field(..., description="Type inference source")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    notes: Optional[str] = Field(None, description="Additional information")


class RelatedInformation(BaseModel):
    """Related diagnostic information."""
    
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")
    message: str = Field(..., description="Related message")


class Diagnostic(BaseModel):
    """Type checking diagnostic."""
    
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")
    column: int = Field(..., description="Column number")
    kind: str = Field(..., description="Diagnostic kind")
    message: str = Field(..., description="Diagnostic message")
    related_information: List[RelatedInformation] = Field(
        default_factory=list,
        description="Related information"
    )
    notes: Optional[str] = Field(None, description="Additional information")


class ValidateChangesOutput(BaseModel):
    """Output for type.validate_changes tool."""
    
    status: str = Field(..., description="Status: 'ok' or 'failed'")
    errors: List[Diagnostic] = Field(
        default_factory=list,
        description="List of error diagnostics"
    )


class EditRange(BaseModel):
    """Edit range information."""
    
    line_start: int = Field(..., description="Start line")
    column_start: int = Field(..., description="Start column")
    line_end: int = Field(..., description="End line")
    column_end: int = Field(..., description="End column")


class Edit(BaseModel):
    """Edit information."""
    
    range: EditRange = Field(..., description="Edit range")
    new_text: str = Field(..., description="New text")


class FixSuggestion(BaseModel):
    """A suggested fix for a type error."""
    
    description: str = Field(..., description="Description of the fix")
    edit: Edit = Field(..., description="Edit to apply")


class SuggestFixOutput(BaseModel):
    """Output for type.suggest_fix tool."""
    
    fix_kind: str = Field(..., description="Fix kind")
    suggestions: List[FixSuggestion] = Field(
        default_factory=list,
        description="List of suggested fixes"
    )
    notes: Optional[str] = Field(None, description="Additional information")


class PackagePreference(BaseModel):
    """Information about a package preference."""
    
    preferred: str = Field(..., description="Preferred package")
    candidates: List[str] = Field(default_factory=list, description="Candidate packages")
    installed: bool = Field(..., description="Whether preferred package is installed")
    notes: Optional[str] = Field(None, description="Additional information")


class CodingPattern(BaseModel):
    """Information about a coding pattern."""
    
    name: str = Field(..., description="Pattern name")
    description: str = Field(..., description="Pattern description")
    example_path: Optional[str] = Field(None, description="Example file path")


class ExampleFile(BaseModel):
    """Example file information."""
    
    file: str = Field(..., description="File path")
    language: str = Field(..., description="Programming language")
    summary: str = Field(..., description="File summary")


class GetTechStackPreferencesOutput(BaseModel):
    """Output for type.get_tech_stack_preferences tool."""
    
    language: str = Field(..., description="The language analyzed")
    packages: Dict[str, PackagePreference] = Field(
        default_factory=dict,
        description="Detected package preferences with installation status"
    )
    patterns: List[CodingPattern] = Field(
        default_factory=list,
        description="Identified coding patterns"
    )
    examples: List[ExampleFile] = Field(
        default_factory=list,
        description="Example files showing patterns"
    )
    notes: Optional[str] = Field(None, description="Additional information")
