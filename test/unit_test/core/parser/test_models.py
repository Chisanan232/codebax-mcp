"""Unit tests for parser models."""

import pytest
from pydantic import ValidationError

from codebax_mcp.core.parser.models import Range, Symbol, SymbolKind


class TestRange:
    """Test suite for Range model."""

    def test_range_creation_valid(self):
        """Test creating a valid Range."""
        range_obj = Range(line_start=1, column_start=0, line_end=5, column_end=10)

        assert range_obj.line_start == 1
        assert range_obj.column_start == 0
        assert range_obj.line_end == 5
        assert range_obj.column_end == 10

    def test_range_single_line(self):
        """Test Range for single line."""
        range_obj = Range(line_start=10, column_start=5, line_end=10, column_end=20)

        assert range_obj.line_start == range_obj.line_end

    def test_range_missing_required_field(self):
        """Test that Range requires all fields."""
        with pytest.raises(ValidationError):
            Range(line_start=1, column_start=0)

    def test_range_serialization(self):
        """Test Range serialization to dict."""
        range_obj = Range(line_start=1, column_start=0, line_end=5, column_end=10)

        data = range_obj.model_dump()
        assert data["line_start"] == 1
        assert data["line_end"] == 5


class TestSymbolKind:
    """Test suite for SymbolKind enum."""

    def test_symbol_kind_values(self):
        """Test that all SymbolKind values are accessible."""
        assert SymbolKind.FUNCTION == "function"
        assert SymbolKind.CLASS == "class"
        assert SymbolKind.METHOD == "method"
        assert SymbolKind.VARIABLE == "variable"
        assert SymbolKind.IMPORT == "import"
        assert SymbolKind.MODULE == "module"
        assert SymbolKind.PARAMETER == "parameter"
        assert SymbolKind.PROPERTY == "property"

    def test_symbol_kind_from_string(self):
        """Test creating SymbolKind from string."""
        kind = SymbolKind("function")
        assert kind == SymbolKind.FUNCTION

    def test_symbol_kind_invalid_value(self):
        """Test that invalid SymbolKind raises error."""
        with pytest.raises(ValueError):
            SymbolKind("invalid_kind")


class TestSymbol:
    """Test suite for Symbol model."""

    @pytest.fixture
    def valid_range(self):
        """Create a valid Range for testing."""
        return Range(line_start=1, column_start=0, line_end=5, column_end=10)

    def test_symbol_creation_minimal(self, valid_range):
        """Test creating Symbol with minimal required fields."""
        symbol = Symbol(
            symbol_id="test:function:foo:1",
            name="foo",
            kind=SymbolKind.FUNCTION,
            language="python",
            file="test.py",
            range=valid_range,
        )

        assert symbol.symbol_id == "test:function:foo:1"
        assert symbol.name == "foo"
        assert symbol.kind == SymbolKind.FUNCTION
        assert symbol.language == "python"
        assert symbol.file == "test.py"
        assert symbol.parent_id is None
        assert symbol.docstring is None
        assert symbol.signature is None

    def test_symbol_creation_with_optional_fields(self, valid_range):
        """Test creating Symbol with all optional fields."""
        symbol = Symbol(
            symbol_id="test:method:bar:10",
            name="bar",
            kind=SymbolKind.METHOD,
            language="python",
            file="test.py",
            range=valid_range,
            parent_id="test:class:MyClass:5",
            docstring="This is a method.",
            signature="def bar(self, x)",
        )

        assert symbol.parent_id == "test:class:MyClass:5"
        assert symbol.docstring == "This is a method."
        assert symbol.signature == "def bar(self, x)"

    def test_symbol_missing_required_field(self, valid_range):
        """Test that Symbol requires all mandatory fields."""
        with pytest.raises(ValidationError):
            Symbol(
                symbol_id="test:function:foo:1",
                name="foo",
                kind=SymbolKind.FUNCTION,
                language="python",
                # Missing 'file' and 'range'
            )

    def test_symbol_serialization(self, valid_range):
        """Test Symbol serialization to dict."""
        symbol = Symbol(
            symbol_id="test:function:foo:1",
            name="foo",
            kind=SymbolKind.FUNCTION,
            language="python",
            file="test.py",
            range=valid_range,
            docstring="Test function",
        )

        data = symbol.model_dump()
        assert data["symbol_id"] == "test:function:foo:1"
        assert data["name"] == "foo"
        assert data["kind"] == "function"
        assert data["docstring"] == "Test function"

    def test_symbol_deserialization(self, valid_range):
        """Test Symbol deserialization from dict."""
        data = {
            "symbol_id": "test:function:foo:1",
            "name": "foo",
            "kind": "function",
            "language": "python",
            "file": "test.py",
            "range": {"line_start": 1, "column_start": 0, "line_end": 5, "column_end": 10},
        }

        symbol = Symbol(**data)
        assert symbol.name == "foo"
        assert symbol.kind == SymbolKind.FUNCTION

    def test_symbol_with_class_kind(self, valid_range):
        """Test Symbol with CLASS kind."""
        symbol = Symbol(
            symbol_id="test:class:MyClass:1",
            name="MyClass",
            kind=SymbolKind.CLASS,
            language="python",
            file="test.py",
            range=valid_range,
        )

        assert symbol.kind == SymbolKind.CLASS

    def test_symbol_with_method_has_parent(self, valid_range):
        """Test that method symbols can have parent_id."""
        symbol = Symbol(
            symbol_id="test:method:my_method:10",
            name="my_method",
            kind=SymbolKind.METHOD,
            language="python",
            file="test.py",
            range=valid_range,
            parent_id="test:class:MyClass:5",
        )

        assert symbol.parent_id is not None
        assert "MyClass" in symbol.parent_id

    def test_symbol_equality(self, valid_range):
        """Test Symbol equality comparison."""
        symbol1 = Symbol(
            symbol_id="test:function:foo:1",
            name="foo",
            kind=SymbolKind.FUNCTION,
            language="python",
            file="test.py",
            range=valid_range,
        )

        symbol2 = Symbol(
            symbol_id="test:function:foo:1",
            name="foo",
            kind=SymbolKind.FUNCTION,
            language="python",
            file="test.py",
            range=valid_range,
        )

        assert symbol1 == symbol2

    def test_symbol_with_multiline_docstring(self, valid_range):
        """Test Symbol with multiline docstring."""
        docstring = """This is a multiline docstring.

        It has multiple paragraphs.
        """

        symbol = Symbol(
            symbol_id="test:function:foo:1",
            name="foo",
            kind=SymbolKind.FUNCTION,
            language="python",
            file="test.py",
            range=valid_range,
            docstring=docstring,
        )

        assert "\n" in symbol.docstring
