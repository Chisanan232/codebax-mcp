"""Unit tests for domain models."""

import pytest
from pydantic import ValidationError

from codebax_mcp.models.domain import (
    CodeChange,
    CodeLocation,
    CodeRange,
    Diagnostic,
    RefactoringOperation,
    Symbol,
    SymbolReference,
    SymbolUsage,
)


class TestCodeLocation:
    """Test suite for CodeLocation model."""

    def test_code_location_creation(self):
        """Test creating a CodeLocation."""
        location = CodeLocation(file="test.py", line=10, column=5)

        assert location.file == "test.py"
        assert location.line == 10
        assert location.column == 5

    def test_code_location_missing_fields(self):
        """Test that CodeLocation requires all fields."""
        with pytest.raises(ValidationError):
            CodeLocation(file="test.py")

    def test_code_location_serialization(self):
        """Test CodeLocation serialization."""
        location = CodeLocation(file="test.py", line=10, column=5)
        data = location.model_dump()

        assert data["file"] == "test.py"
        assert data["line"] == 10
        assert data["column"] == 5


class TestCodeRange:
    """Test suite for CodeRange model."""

    def test_code_range_creation(self):
        """Test creating a CodeRange."""
        range_obj = CodeRange(
            start=CodeLocation(file="test.py", line=1, column=0), end=CodeLocation(file="test.py", line=5, column=10)
        )

        assert range_obj.start.line == 1
        assert range_obj.end.line == 5

    def test_code_range_single_line(self):
        """Test CodeRange for single line."""
        range_obj = CodeRange(
            start=CodeLocation(file="test.py", line=10, column=5), end=CodeLocation(file="test.py", line=10, column=20)
        )

        assert range_obj.start.line == range_obj.end.line

    def test_code_range_validation(self):
        """Test CodeRange validation."""
        with pytest.raises(ValidationError):
            CodeRange(start=CodeLocation(file="test.py", line=1, column=0))


class TestSymbol:
    """Test suite for Symbol domain model."""

    def test_symbol_creation(self):
        """Test creating a Symbol."""
        symbol = Symbol(
            id="test:func:foo:1",
            name="foo",
            kind="function",
            language="python",
            location=CodeLocation(file="test.py", line=10, column=0),
        )

        assert symbol.id == "test:func:foo:1"
        assert symbol.name == "foo"
        assert symbol.kind == "function"

    def test_symbol_with_optional_fields(self):
        """Test Symbol with optional fields."""
        symbol = Symbol(
            id="test:func:foo:1",
            name="foo",
            kind="function",
            language="python",
            location=CodeLocation(file="test.py", line=10, column=5),
            docstring="Test function",
            signature="def foo(x, y)",
        )

        assert symbol.location.line == 10
        assert symbol.docstring == "Test function"


class TestSymbolUsage:
    """Test suite for SymbolUsage model."""

    def test_symbol_usage_creation(self):
        """Test creating a SymbolUsage."""
        usage = SymbolUsage(
            symbol_id="test:func:foo:1",
            location=CodeLocation(file="test.py", line=20, column=10),
            kind="exact",
            confidence=1.0,
        )

        assert usage.symbol_id == "test:func:foo:1"
        assert usage.location.line == 20
        assert usage.kind == "exact"

    def test_symbol_usage_with_confidence(self):
        """Test SymbolUsage with confidence score."""
        usage = SymbolUsage(
            symbol_id="test:func:foo:1",
            location=CodeLocation(file="test.py", line=20, column=10),
            kind="heuristic",
            confidence=0.95,
        )

        assert usage.confidence == 0.95


class TestSymbolReference:
    """Test suite for SymbolReference model."""

    def test_symbol_reference_creation(self):
        """Test creating a SymbolReference."""
        symbol = Symbol(
            id="test:func:foo:1",
            name="foo",
            kind="function",
            language="python",
            location=CodeLocation(file="test.py", line=10, column=0),
        )
        ref = SymbolReference(symbol=symbol, usages=[])

        assert ref.symbol.id == "test:func:foo:1"
        assert ref.symbol.name == "foo"


class TestDiagnostic:
    """Test suite for Diagnostic model."""

    def test_diagnostic_creation(self):
        """Test creating a Diagnostic."""
        from codebax_mcp.models.domain.location import CodeLocation

        diagnostic = Diagnostic(
            location=CodeLocation(file="test.py", line=10, column=5), message="Undefined variable", severity="error"
        )

        assert diagnostic.location.file == "test.py"
        assert diagnostic.message == "Undefined variable"
        assert diagnostic.severity == "error"

    def test_diagnostic_with_code(self):
        """Test Diagnostic with error code."""
        from codebax_mcp.models.domain.location import CodeLocation

        diagnostic = Diagnostic(
            location=CodeLocation(file="test.py", line=10, column=5),
            message="Undefined variable",
            severity="error",
            code="E001",
        )

        assert diagnostic.code == "E001"

    def test_diagnostic_severity_types(self):
        """Test different severity types."""
        from codebax_mcp.models.domain.location import CodeLocation

        for severity in ["error", "warning", "info"]:
            diagnostic = Diagnostic(
                location=CodeLocation(file="test.py", line=10, column=5), message="Test message", severity=severity
            )
            assert diagnostic.severity == severity


class TestCodeChange:
    """Test suite for CodeChange model."""

    def test_code_change_creation(self):
        """Test creating a CodeChange."""
        change = CodeChange(file="test.py", old_text="old code", new_text="new code")

        assert change.file == "test.py"
        assert change.old_text == "old code"
        assert change.new_text == "new code"

    def test_code_change_with_description(self):
        """Test CodeChange with description."""
        change = CodeChange(file="test.py", old_text="old code", new_text="new code", description="Refactor function")

        assert change.description == "Refactor function"

    def test_code_change_serialization(self):
        """Test CodeChange serialization."""
        change = CodeChange(file="test.py", old_text="old code", new_text="new code")

        data = change.model_dump()
        assert data["file"] == "test.py"
        assert data["old_text"] == "old code"


class TestRefactoringOperation:
    """Test suite for RefactoringOperation model."""

    def test_refactoring_operation_creation(self):
        """Test creating a RefactoringOperation."""
        operation = RefactoringOperation(operation_type="rename")

        assert operation.operation_type == "rename"
        assert operation.dry_run is True
        assert operation.status == "pending"

    def test_refactoring_operation_with_changes(self):
        """Test RefactoringOperation with changes."""
        change = CodeChange(file="test.py", old_text="old", new_text="new")

        operation = RefactoringOperation(operation_type="extract", changes=[change])

        assert len(operation.changes) == 1
        assert operation.changes[0].file == "test.py"

    def test_refactoring_operation_types(self):
        """Test different refactoring operation types."""
        for op_type in ["rename", "extract", "inline", "move"]:
            operation = RefactoringOperation(operation_type=op_type)
            assert operation.operation_type == op_type
