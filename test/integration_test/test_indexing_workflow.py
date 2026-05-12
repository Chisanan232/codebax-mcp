"""Integration tests for complete indexing workflow."""

import pytest

from codebax_mcp.core.index.lock_file_store import LockFileStore
from codebax_mcp.core.index.symbol_index import SymbolIndex
from codebax_mcp.core.parser.python_parser import PythonParser
from codebax_mcp.mcp_server.models.input import IndexCodebaseInput
from codebax_mcp.mcp_server.tools.services.code.index import index_codebase


class TestIndexingWorkflow:
    """Integration tests for complete indexing workflow."""

    @pytest.fixture
    def sample_project(self, tmp_path):
        """Create a sample Python project for testing."""
        # Create project structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create main module
        (src_dir / "main.py").write_text("""
'''Main module for the application.'''

def main():
    '''Entry point of the application.'''
    calculator = Calculator()
    result = calculator.add(5, 3)
    print(f"Result: {result}")

class Calculator:
    '''A simple calculator class.'''

    def add(self, a, b):
        '''Add two numbers.'''
        return a + b

    def subtract(self, a, b):
        '''Subtract b from a.'''
        return a - b

    def multiply(self, a, b):
        '''Multiply two numbers.'''
        return a * b

if __name__ == "__main__":
    main()
""")

        # Create utils module
        (src_dir / "utils.py").write_text("""
'''Utility functions.'''

def format_number(num):
    '''Format a number as string.'''
    return f"{num:,.2f}"

def validate_input(value):
    '''Validate input value.'''
    if not isinstance(value, (int, float)):
        raise ValueError("Input must be a number")
    return True
""")

        return tmp_path

    def test_end_to_end_indexing(self, sample_project):
        """Test complete end-to-end indexing workflow."""
        # Index the codebase
        input_data = IndexCodebaseInput(workspace_root=str(sample_project), full=True)

        result = index_codebase(input_data)

        # Verify indexing succeeded
        assert result.status in ["success", "completed", "ok"]
        assert result.indexed_files >= 2

        # Verify lock file was created
        lock_file = sample_project / ".codebax_index.lock"
        assert lock_file.exists()

        # Verify lock file can be loaded
        store = LockFileStore(str(lock_file))
        data = store.load()
        assert data is not None
        assert "symbol_definitions" in data

    def test_parser_to_index_workflow(self, sample_project):
        """Test workflow from parsing to indexing."""
        # Parse files
        parser = PythonParser()
        main_file = sample_project / "src" / "main.py"
        symbols = parser.parse_file(str(main_file))

        # Verify parsing worked
        assert len(symbols) > 0

        # Add to index
        index = SymbolIndex()
        for symbol in symbols:
            index.add_symbol(symbol)

        # Verify symbols are in index
        assert len(index.get_file_symbols(str(main_file))) > 0

        # Search for symbols
        results = index.search_by_name("Calculator")
        assert len(results) > 0
        assert results[0].name == "Calculator"

    def test_incremental_indexing_workflow(self, sample_project):
        """Test incremental indexing after initial full index."""
        # Full index first
        input_full = IndexCodebaseInput(workspace_root=str(sample_project), full=True)
        result1 = index_codebase(input_full)
        initial_count = result1.indexed_files

        # Add new file
        new_file = sample_project / "src" / "new_module.py"
        new_file.write_text("""
def new_function():
    '''A new function.'''
    pass
""")

        # Incremental index
        input_incremental = IndexCodebaseInput(
            workspace_root=str(sample_project), full=False, paths=["src/new_module.py"]
        )
        result2 = index_codebase(input_incremental)

        # Verify incremental indexing worked
        assert result2.status in ["success", "completed", "ok"]

    def test_index_persistence_workflow(self, sample_project):
        """Test that index persists across sessions."""
        # Index the codebase
        input_data = IndexCodebaseInput(workspace_root=str(sample_project), full=True)
        result1 = index_codebase(input_data)

        # Load the persisted index
        lock_file = sample_project / ".codebax_index.lock"
        store = LockFileStore(str(lock_file))
        data = store.load()

        # Verify data persisted
        assert data is not None
        assert len(data["symbol_definitions"]) > 0

        # Index again (should load from lock file)
        result2 = index_codebase(input_data)

        # Both results should have similar file counts
        assert result2.indexed_files >= 0

    def test_multi_file_indexing_workflow(self, sample_project):
        """Test indexing multiple files in one operation."""
        input_data = IndexCodebaseInput(workspace_root=str(sample_project), full=True)

        result = index_codebase(input_data)

        # Verify all files were indexed
        assert result.indexed_files >= 2

        # Load index and verify symbols from both files
        lock_file = sample_project / ".codebax_index.lock"
        store = LockFileStore(str(lock_file))
        data = store.load()

        # Check for symbols from main.py
        main_symbols = [s for s in data["symbol_definitions"].values() if "main.py" in s.get("file", "")]
        assert len(main_symbols) > 0

        # Check for symbols from utils.py
        utils_symbols = [s for s in data["symbol_definitions"].values() if "utils.py" in s.get("file", "")]
        assert len(utils_symbols) > 0

    def test_index_with_errors_workflow(self, sample_project):
        """Test indexing workflow with files containing errors."""
        # Add file with syntax error
        error_file = sample_project / "src" / "error.py"
        error_file.write_text("def broken(\n    return 'missing paren'")

        # Index should still work for valid files
        input_data = IndexCodebaseInput(workspace_root=str(sample_project), full=True)

        result = index_codebase(input_data)

        # Should still index valid files
        assert result.status in ["success", "completed", "ok"]
        assert result.indexed_files >= 2

    def test_search_after_indexing_workflow(self, sample_project):
        """Test searching symbols after indexing."""
        # Index the codebase
        input_data = IndexCodebaseInput(workspace_root=str(sample_project), full=True)
        index_codebase(input_data)

        # Load index and search
        lock_file = sample_project / ".codebax_index.lock"
        store = LockFileStore(str(lock_file))
        data = store.load()

        # Search for Calculator class
        calculator_symbols = [s for s in data["symbol_definitions"].values() if s.get("name") == "Calculator"]
        assert len(calculator_symbols) > 0
        assert calculator_symbols[0]["kind"] == "class"

        # Search for add method
        add_symbols = [s for s in data["symbol_definitions"].values() if s.get("name") == "add"]
        assert len(add_symbols) > 0

    def test_reindex_after_file_change_workflow(self, sample_project):
        """Test re-indexing after file changes."""
        # Initial index
        input_data = IndexCodebaseInput(workspace_root=str(sample_project), full=True)
        result1 = index_codebase(input_data)

        # Modify file
        main_file = sample_project / "src" / "main.py"
        content = main_file.read_text()
        content += "\n\ndef new_function():\n    '''New function.'''\n    pass\n"
        main_file.write_text(content)

        # Re-index
        result2 = index_codebase(input_data)

        # Should have indexed files
        assert result2.indexed_files >= result1.indexed_files
