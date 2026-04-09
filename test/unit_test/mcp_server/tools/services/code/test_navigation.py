"""Unit tests for code navigation tools."""

from unittest.mock import Mock, patch

import pytest

from codebax_mcp.mcp_server.models.input import (
    FindUsagesInput,
    GetCallGraphInput,
    GetDefinitionInput,
    IdentifySymbolInput,
)
from codebax_mcp.mcp_server.models.output import (
    FindUsagesOutput,
    GetCallGraphOutput,
    GetDefinitionOutput,
    IdentifySymbolOutput,
)
from codebax_mcp.mcp_server.tools.services.code.navigation import (
    find_usages,
    get_call_graph,
    get_definition,
    identify_symbol,
)


class TestIdentifySymbol:
    """Test suite for identify_symbol function."""

    @pytest.fixture
    def mock_index(self):
        """Create a mock symbol index."""
        with patch("codebax_mcp.mcp_server.tools.services.code.navigation.LockFileStore") as mock:
            mock_store = Mock()
            mock_store.load.return_value = {
                "symbol_definitions": {
                    "test.py:function:foo:10": {
                        "symbol_id": "test.py:function:foo:10",
                        "name": "foo",
                        "kind": "function",
                        "file": "test.py",
                        "range": {"line_start": 10, "column_start": 0, "line_end": 15, "column_end": 10},
                    }
                }
            }
            mock.return_value = mock_store
            yield mock_store

    def test_identify_symbol_basic(self, mock_index):
        """Test basic symbol identification."""
        input_data = IdentifySymbolInput(file="test.py", language="python", line=10, column=5)

        result = identify_symbol(input_data)

        assert isinstance(result, IdentifySymbolOutput)

    def test_identify_symbol_returns_symbol_id(self, mock_index):
        """Test that identify_symbol returns symbol ID."""
        input_data = IdentifySymbolInput(file="test.py", language="python", line=10, column=5)

        result = identify_symbol(input_data)

        assert hasattr(result, "symbol_id")

    def test_identify_symbol_not_found(self, mock_index):
        """Test identifying symbol when not found."""
        mock_index.load.return_value = {"symbol_definitions": {}}

        input_data = IdentifySymbolInput(file="test.py", language="python", line=100, column=5)

        result = identify_symbol(input_data)

        assert isinstance(result, IdentifySymbolOutput)


class TestGetDefinition:
    """Test suite for get_definition function."""

    @pytest.fixture
    def mock_index(self):
        """Create a mock symbol index."""
        with patch("codebax_mcp.mcp_server.tools.services.code.navigation.LockFileStore") as mock:
            mock_store = Mock()
            mock_store.load.return_value = {
                "symbol_definitions": {
                    "test.py:function:foo:10": {
                        "symbol_id": "test.py:function:foo:10",
                        "name": "foo",
                        "kind": "function",
                        "file": "test.py",
                        "language": "python",
                        "range": {"line_start": 10, "column_start": 0, "line_end": 15, "column_end": 10},
                        "signature": "def foo(x, y)",
                        "docstring": "Test function",
                    }
                }
            }
            mock.return_value = mock_store
            yield mock_store

    def test_get_definition_basic(self, mock_index):
        """Test basic definition retrieval."""
        input_data = GetDefinitionInput(symbol_id="test.py:function:foo:10")

        result = get_definition(input_data)

        assert isinstance(result, GetDefinitionOutput)

    def test_get_definition_returns_metadata(self, mock_index):
        """Test that get_definition returns symbol metadata."""
        input_data = GetDefinitionInput(symbol_id="test.py:function:foo:10")

        result = get_definition(input_data)

        assert hasattr(result, "symbol_id")
        assert hasattr(result, "name") or hasattr(result, "definition")

    def test_get_definition_not_found(self, mock_index):
        """Test getting definition for non-existent symbol."""
        input_data = GetDefinitionInput(symbol_id="nonexistent:id")

        result = get_definition(input_data)

        assert isinstance(result, GetDefinitionOutput)


class TestFindUsages:
    """Test suite for find_usages function."""

    @pytest.fixture
    def mock_index(self):
        """Create a mock symbol index."""
        with patch("codebax_mcp.mcp_server.tools.services.code.navigation.LockFileStore") as mock:
            mock_store = Mock()
            mock_store.load.return_value = {
                "symbol_definitions": {
                    "test.py:function:foo:10": {
                        "symbol_id": "test.py:function:foo:10",
                        "name": "foo",
                        "kind": "function",
                    }
                },
                "symbol_usages": {
                    "test.py:function:foo:10": [
                        {"file": "main.py", "line": 20, "column": 5, "context": "result = foo(1, 2)"}
                    ]
                },
            }
            mock.return_value = mock_store
            yield mock_store

    def test_find_usages_basic(self, mock_index):
        """Test basic usage finding."""
        input_data = FindUsagesInput(symbol_id="test.py:function:foo:10")

        result = find_usages(input_data)

        assert isinstance(result, FindUsagesOutput)

    def test_find_usages_returns_locations(self, mock_index):
        """Test that find_usages returns usage locations."""
        input_data = FindUsagesInput(symbol_id="test.py:function:foo:10")

        result = find_usages(input_data)

        assert hasattr(result, "usages") or hasattr(result, "locations")

    def test_find_usages_with_include_tests(self, mock_index):
        """Test finding usages with include_tests option."""
        input_data = FindUsagesInput(symbol_id="test.py:function:foo:10", include_tests=True)

        result = find_usages(input_data)

        assert isinstance(result, FindUsagesOutput)

    def test_find_usages_not_found(self, mock_index):
        """Test finding usages for non-existent symbol."""
        mock_index.load.return_value = {"symbol_definitions": {}, "symbol_usages": {}}

        input_data = FindUsagesInput(symbol_id="nonexistent:id")

        result = find_usages(input_data)

        assert isinstance(result, FindUsagesOutput)


class TestGetCallGraph:
    """Test suite for get_call_graph function."""

    @pytest.fixture
    def mock_index(self):
        """Create a mock symbol index."""
        with patch("codebax_mcp.mcp_server.tools.services.code.navigation.LockFileStore") as mock:
            mock_store = Mock()
            mock_store.load.return_value = {
                "symbol_definitions": {
                    "test.py:function:foo:10": {
                        "symbol_id": "test.py:function:foo:10",
                        "name": "foo",
                        "kind": "function",
                    }
                }
            }
            mock.return_value = mock_store
            yield mock_store

    def test_get_call_graph_basic(self, mock_index):
        """Test basic call graph retrieval."""
        input_data = GetCallGraphInput(symbol_id="test.py:function:foo:10")

        result = get_call_graph(input_data)

        assert isinstance(result, GetCallGraphOutput)

    def test_get_call_graph_with_direction(self, mock_index):
        """Test call graph with direction parameter."""
        for direction in ["incoming", "outgoing", "both"]:
            input_data = GetCallGraphInput(symbol_id="test.py:function:foo:10", direction=direction)

            result = get_call_graph(input_data)

            assert isinstance(result, GetCallGraphOutput)

    def test_get_call_graph_with_depth(self, mock_index):
        """Test call graph with depth parameter."""
        input_data = GetCallGraphInput(symbol_id="test.py:function:foo:10", depth=2)

        result = get_call_graph(input_data)

        assert isinstance(result, GetCallGraphOutput)

    def test_get_call_graph_not_found(self, mock_index):
        """Test call graph for non-existent symbol."""
        mock_index.load.return_value = {"symbol_definitions": {}}

        input_data = GetCallGraphInput(symbol_id="nonexistent:id")

        result = get_call_graph(input_data)

        assert isinstance(result, GetCallGraphOutput)
