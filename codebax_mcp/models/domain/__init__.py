"""Domain models for CodeBax MCP server.

These models represent core domain concepts used across the application.
They are shared between tool implementations and provide type-safe data structures.
"""

from .location import CodeLocation, CodeRange
from .symbol import Symbol, SymbolUsage, SymbolReference
from .diagnostic import Diagnostic
from .change import CodeChange, RefactoringOperation

__all__ = [
    # Location models
    "CodeLocation",
    "CodeRange",
    # Symbol models
    "Symbol",
    "SymbolUsage",
    "SymbolReference",
    # Diagnostic models
    "Diagnostic",
    # Change models
    "CodeChange",
    "RefactoringOperation",
]
