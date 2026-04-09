"""Unit tests for symbol index implementation."""

import pytest

from codebax_mcp.core.index.symbol_index import SymbolIndex
from codebax_mcp.core.parser.models import Range, Symbol, SymbolKind


class TestSymbolIndex:
    """Test suite for SymbolIndex class."""

    @pytest.fixture
    def index(self):
        """Create a SymbolIndex instance."""
        return SymbolIndex()

    @pytest.fixture
    def sample_symbol(self):
        """Create a sample symbol for testing."""
        return Symbol(
            symbol_id="test.py:function:foo:1",
            name="foo",
            kind=SymbolKind.FUNCTION,
            language="python",
            file="test.py",
            range=Range(line_start=1, column_start=0, line_end=5, column_end=10),
            docstring="Test function",
        )

    def test_add_symbol(self, index, sample_symbol):
        """Test adding a symbol to the index."""
        index.add_symbol(sample_symbol)

        retrieved = index.get_symbol(sample_symbol.symbol_id)
        assert retrieved is not None
        assert retrieved.name == "foo"

    def test_get_symbol_nonexistent(self, index):
        """Test getting a non-existent symbol returns None."""
        result = index.get_symbol("nonexistent:id")

        assert result is None

    def test_add_multiple_symbols(self, index):
        """Test adding multiple symbols."""
        symbols = [
            Symbol(
                symbol_id=f"test.py:function:func{i}:{i}",
                name=f"func{i}",
                kind=SymbolKind.FUNCTION,
                language="python",
                file="test.py",
                range=Range(line_start=i, column_start=0, line_end=i + 1, column_end=10),
            )
            for i in range(1, 4)
        ]

        for symbol in symbols:
            index.add_symbol(symbol)

        assert index.get_symbol("test.py:function:func1:1") is not None
        assert index.get_symbol("test.py:function:func2:2") is not None
        assert index.get_symbol("test.py:function:func3:3") is not None

    def test_search_by_name(self, index, sample_symbol):
        """Test searching symbols by name."""
        index.add_symbol(sample_symbol)

        results = index.search_by_name("foo")

        assert len(results) > 0
        assert results[0].name == "foo"

    def test_search_by_name_partial_match(self, index):
        """Test searching with partial name match."""
        symbols = [
            Symbol(
                symbol_id="test.py:function:test_foo:1",
                name="test_foo",
                kind=SymbolKind.FUNCTION,
                language="python",
                file="test.py",
                range=Range(line_start=1, column_start=0, line_end=2, column_end=10),
            ),
            Symbol(
                symbol_id="test.py:function:test_bar:5",
                name="test_bar",
                kind=SymbolKind.FUNCTION,
                language="python",
                file="test.py",
                range=Range(line_start=5, column_start=0, line_end=6, column_end=10),
            ),
        ]

        for symbol in symbols:
            index.add_symbol(symbol)

        results = index.search_by_name("test")

        assert len(results) >= 2

    def test_get_symbols_by_file(self, index):
        """Test getting all symbols from a specific file."""
        symbols = [
            Symbol(
                symbol_id=f"test.py:function:func{i}:{i}",
                name=f"func{i}",
                kind=SymbolKind.FUNCTION,
                language="python",
                file="test.py",
                range=Range(line_start=i, column_start=0, line_end=i + 1, column_end=10),
            )
            for i in range(1, 4)
        ]

        for symbol in symbols:
            index.add_symbol(symbol)

        file_symbols = index.get_file_symbols("test.py")

        assert len(file_symbols) == 3

    def test_clear_file_removes_symbols(self, index, sample_symbol):
        """Test that clear_file removes symbols for a specific file."""
        index.add_symbol(sample_symbol)
        assert index.get_symbol(sample_symbol.symbol_id) is not None

        index.clear_file("test.py")

        assert index.get_symbol(sample_symbol.symbol_id) is None

    def test_get_all_symbols(self, index):
        """Test getting all symbols from index."""
        symbols = [
            Symbol(
                symbol_id=f"test.py:function:func{i}:{i}",
                name=f"func{i}",
                kind=SymbolKind.FUNCTION,
                language="python",
                file="test.py",
                range=Range(line_start=i, column_start=0, line_end=i + 1, column_end=10),
            )
            for i in range(1, 4)
        ]

        for symbol in symbols:
            index.add_symbol(symbol)

        all_symbols = list(index.symbol_definitions.values())

        assert len(all_symbols) == 3

    def test_symbol_count(self, index):
        """Test getting symbol count."""
        symbols = [
            Symbol(
                symbol_id=f"test.py:function:func{i}:{i}",
                name=f"func{i}",
                kind=SymbolKind.FUNCTION,
                language="python",
                file="test.py",
                range=Range(line_start=i, column_start=0, line_end=i + 1, column_end=10),
            )
            for i in range(1, 6)
        ]

        for symbol in symbols:
            index.add_symbol(symbol)

        count = len(index.symbol_definitions)

        assert count == 5

    def test_mark_dirty(self, index):
        """Test marking a file as dirty."""
        index.mark_dirty("test.py")

        assert "test.py" in index.dirty_files

    def test_clear_dirty(self, index):
        """Test clearing dirty flag for a file."""
        index.mark_dirty("test.py")
        assert "test.py" in index.dirty_files

        index.clear_dirty("test.py")

        assert "test.py" not in index.dirty_files

    def test_get_dirty_files(self, index):
        """Test getting list of dirty files."""
        index.mark_dirty("file1.py")
        index.mark_dirty("file2.py")

        dirty_files = index.get_dirty_files()

        assert len(dirty_files) == 2
        assert "file1.py" in dirty_files
        assert "file2.py" in dirty_files

    def test_update_symbol(self, index, sample_symbol):
        """Test updating an existing symbol."""
        index.add_symbol(sample_symbol)

        updated_symbol = Symbol(
            symbol_id=sample_symbol.symbol_id,
            name="foo_updated",
            kind=SymbolKind.FUNCTION,
            language="python",
            file="test.py",
            range=sample_symbol.range,
            docstring="Updated docstring",
        )

        index.add_symbol(updated_symbol)
        retrieved = index.get_symbol(sample_symbol.symbol_id)

        assert retrieved.name == "foo_updated"
        assert retrieved.docstring == "Updated docstring"

    def test_search_by_kind(self, index):
        """Test searching symbols by kind using manual filtering."""
        symbols = [
            Symbol(
                symbol_id="test.py:function:func1:1",
                name="func1",
                kind=SymbolKind.FUNCTION,
                language="python",
                file="test.py",
                range=Range(line_start=1, column_start=0, line_end=2, column_end=10),
            ),
            Symbol(
                symbol_id="test.py:class:MyClass:5",
                name="MyClass",
                kind=SymbolKind.CLASS,
                language="python",
                file="test.py",
                range=Range(line_start=5, column_start=0, line_end=10, column_end=10),
            ),
        ]

        for symbol in symbols:
            index.add_symbol(symbol)

        # Manual filtering by kind
        functions = [s for s in index.symbol_definitions.values() if s.kind == SymbolKind.FUNCTION]
        classes = [s for s in index.symbol_definitions.values() if s.kind == SymbolKind.CLASS]

        assert len(functions) == 1
        assert len(classes) == 1
        assert functions[0].name == "func1"
        assert classes[0].name == "MyClass"
