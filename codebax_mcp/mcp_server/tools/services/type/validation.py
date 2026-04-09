"""type.validate_changes and type.suggest_fix - Type validation tools."""

import os
from typing import Dict, Any, List, Optional
from codebax_mcp.core.type_checker import PyrightClient
from codebax_mcp.mcp_server.models.input import ValidateChangesInput, SuggestFixInput
from codebax_mcp.mcp_server.models.output import ValidateChangesOutput, SuggestFixOutput, Diagnostic, FixSuggestion


def validate_changes(input: ValidateChangesInput) -> ValidateChangesOutput:
    """Validate code changes for type errors."""
    
    try:
        # Use Pyright to validate
        pyright = PyrightClient(input.workspace_root)
        diagnostics_raw = pyright.validate(input.file)
        
        diagnostics = [
            Diagnostic(
                file=d.file,
                line=d.line,
                column=d.column,
                message=d.message,
                severity=d.severity,
                code=d.code
            )
            for d in diagnostics_raw
        ]
        
        # Categorize
        errors = [d for d in diagnostics if d.severity == "error"]
        warnings = [d for d in diagnostics if d.severity == "warning"]
        
        status = "failed" if errors else "ok"
        
        return ValidateChangesOutput(
            status=status,
            file=input.file,
            diagnostics=diagnostics,
            errors=errors,
            warnings=warnings
        )
    
    except Exception as e:
        return ValidateChangesOutput(
            status="failed",
            file=input.file,
            diagnostics=[],
            errors=[],
            warnings=[],
            error=str(e)
        )


def suggest_fix(input: SuggestFixInput) -> SuggestFixOutput:
    """Suggest type-related fixes for errors."""
    
    suggestions = []
    
    # Simple heuristic-based suggestions
    if "is not defined" in input.error_message:
        suggestions.append(FixSuggestion(
            description="Add import statement for undefined symbol",
            patch=None
        ))
    elif "missing positional argument" in input.error_message:
        suggestions.append(FixSuggestion(
            description="Add missing function argument",
            patch=None
        ))
    elif "unexpected keyword argument" in input.error_message:
        suggestions.append(FixSuggestion(
            description="Remove unexpected keyword argument",
            patch=None
        ))
    elif "incompatible types" in input.error_message:
        suggestions.append(FixSuggestion(
            description="Add type annotation or cast",
            patch=None
        ))
    
    return SuggestFixOutput(
        file=input.file,
        line=input.line,
        column=input.column,
        suggestions=suggestions,
        patches=[],
        notes="Fix suggestions require advanced type analysis (Phase 6+)"
    )
