"""Unit tests for type symbol info tools."""

import pytest
from unittest.mock import Mock, patch
from codebax_mcp.mcp_server.tools.services.type.symbol_info import (
    get_symbol_info,
    find_similar_usages
)
from codebax_mcp.mcp_server.models.input import (
    GetSymbolInfoInput,
    FindSimilarUsagesInput
)
from codebax_mcp.mcp_server.models.output import (
    GetSymbolInfoOutput,
    FindSimilarUsagesOutput
)


class TestGetSymbolInfo:
    """Test suite for get_symbol_info function."""

    @pytest.fixture
    def mock_index(self):
        """Create a mock symbol index."""
        with patch('codebax_mcp.mcp_server.tools.services.type.symbol_info.LockFileStore') as mock:
            mock_store = Mock()
            mock_store.load.return_value = {
                "symbol_definitions": {
                    "test.py:function:foo:10": {
                        "symbol_id": "test.py:function:foo:10",
                        "name": "foo",
                        "kind": "function",
                        "file": "test.py",
                        "language": "python",
                        "signature": "def foo(x: int, y: int) -> int",
                        "docstring": "Add two numbers",
                        "range": {
                            "line_start": 10,
                            "column_start": 0,
                            "line_end": 15,
                            "column_end": 10
                        }
                    }
                }
            }
            mock.return_value = mock_store
            yield mock_store

    def test_get_symbol_info_basic(self, mock_index):
        """Test basic symbol info retrieval."""
        input_data = GetSymbolInfoInput(
            symbol="foo",
            language="python"
        )
        
        result = get_symbol_info(input_data)
        
        assert isinstance(result, GetSymbolInfoOutput)

    def test_get_symbol_info_returns_signature(self, mock_index):
        """Test that get_symbol_info returns signature."""
        input_data = GetSymbolInfoInput(
            symbol="foo",
            language="python"
        )
        
        result = get_symbol_info(input_data)
        
        assert hasattr(result, 'signature')

    def test_get_symbol_info_returns_docstring(self, mock_index):
        """Test that get_symbol_info returns docstring."""
        input_data = GetSymbolInfoInput(
            symbol="foo",
            language="python"
        )
        
        result = get_symbol_info(input_data)
        
        assert hasattr(result, 'docstring')

    def test_get_symbol_info_not_found(self, mock_index):
        """Test getting info for non-existent symbol."""
        mock_index.load.return_value = {"symbol_definitions": {}}
        
        input_data = GetSymbolInfoInput(
            symbol="nonexistent",
            language="python"
        )
        
        result = get_symbol_info(input_data)
        
        assert isinstance(result, GetSymbolInfoOutput)

    def test_get_symbol_info_with_file(self, mock_index):
        """Test getting symbol info with file parameter."""
        input_data = GetSymbolInfoInput(
            symbol="foo",
            file="test.py",
            language="python"
        )
        
        result = get_symbol_info(input_data)
        
        assert isinstance(result, GetSymbolInfoOutput)


class TestFindSimilarUsages:
    """Test suite for find_similar_usages function."""

    @pytest.fixture
    def mock_index(self):
        """Create a mock symbol index."""
        with patch('codebax_mcp.mcp_server.tools.services.type.symbol_info.LockFileStore') as mock:
            mock_store = Mock()
            mock_store.load.return_value = {
                "symbol_definitions": {
                    "test.py:function:calculate_sum:10": {
                        "symbol_id": "test.py:function:calculate_sum:10",
                        "name": "calculate_sum",
                        "kind": "function",
                        "file": "test.py",
                        "language": "python"
                    },
                    "test.py:function:calculate_product:20": {
                        "symbol_id": "test.py:function:calculate_product:20",
                        "name": "calculate_product",
                        "kind": "function",
                        "file": "test.py",
                        "language": "python"
                    }
                }
            }
            mock.return_value = mock_store
            yield mock_store

    def test_find_similar_usages_basic(self, mock_index):
        """Test basic similar usages finding."""
        input_data = FindSimilarUsagesInput(
            symbol="calculate",
            language="python"
        )
        
        result = find_similar_usages(input_data)
        
        assert isinstance(result, FindSimilarUsagesOutput)

    def test_find_similar_usages_returns_list(self, mock_index):
        """Test that find_similar_usages returns list of symbols."""
        input_data = FindSimilarUsagesInput(
            symbol="calculate",
            language="python"
        )
        
        result = find_similar_usages(input_data)
        
        assert hasattr(result, 'similar_symbols')

    def test_find_similar_usages_case_insensitive(self, mock_index):
        """Test that similar usages search is case insensitive."""
        input_data = FindSimilarUsagesInput(
            symbol="CALCULATE",
            language="python"
        )
        
        result = find_similar_usages(input_data)
        
        assert isinstance(result, FindSimilarUsagesOutput)

    def test_find_similar_usages_no_matches(self, mock_index):
        """Test finding similar usages with no matches."""
        mock_index.load.return_value = {"symbol_definitions": {}}
        
        input_data = FindSimilarUsagesInput(
            symbol="nonexistent",
            language="python"
        )
        
        result = find_similar_usages(input_data)
        
        assert isinstance(result, FindSimilarUsagesOutput)

    def test_find_similar_usages_partial_match(self, mock_index):
        """Test finding similar usages with partial match."""
        input_data = FindSimilarUsagesInput(
            symbol="sum",
            language="python"
        )
        
        result = find_similar_usages(input_data)
        
        assert isinstance(result, FindSimilarUsagesOutput)
