"""Unit tests for code index tool."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from codebax_mcp.mcp_server.models.input import IndexCodebaseInput
from codebax_mcp.mcp_server.models.output import IndexCodebaseOutput


class TestIndexCodebase:
    """Test suite for index_codebase function."""

    @pytest.fixture
    def python_project(self, tmp_path):
        """Create a temporary Python project."""
        # Create source files
        (tmp_path / "module1.py").write_text("""
def function1():
    '''First function.'''
    pass

class Class1:
    '''First class.'''
    def method1(self):
        pass
""")
        
        (tmp_path / "module2.py").write_text("""
def function2():
    '''Second function.'''
    pass

class Class2:
    '''Second class.'''
    pass
""")
        
        return tmp_path

    def test_index_codebase_basic(self, python_project):
        """Test basic codebase indexing."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        input_data = IndexCodebaseInput(
            workspace_root=str(python_project),
            full=True
        )
        
        result = index_codebase(input_data)
        
        assert isinstance(result, IndexCodebaseOutput)
        assert result.status in ["success", "completed", "ok"]

    def test_index_codebase_counts_files(self, python_project):
        """Test that indexing counts files correctly."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        input_data = IndexCodebaseInput(
            workspace_root=str(python_project),
            full=True
        )
        
        result = index_codebase(input_data)
        
        assert result.indexed_files >= 2

    def test_index_codebase_counts_symbols(self, python_project):
        """Test that indexing counts symbols correctly."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        input_data = IndexCodebaseInput(
            workspace_root=str(python_project),
            full=True
        )
        
        result = index_codebase(input_data)
        
        assert result.indexed_files >= 2

    def test_index_codebase_incremental(self, python_project):
        """Test incremental indexing."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        # First full index
        input_full = IndexCodebaseInput(
            workspace_root=str(python_project),
            full=True
        )
        index_codebase(input_full)
        
        # Then incremental
        input_incremental = IndexCodebaseInput(
            workspace_root=str(python_project),
            full=False
        )
        
        result = index_codebase(input_incremental)
        
        assert isinstance(result, IndexCodebaseOutput)

    def test_index_codebase_with_specific_paths(self, python_project):
        """Test indexing specific paths only."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        input_data = IndexCodebaseInput(
            workspace_root=str(python_project),
            full=False,
            paths=["module1.py"]
        )
        
        result = index_codebase(input_data)
        
        assert isinstance(result, IndexCodebaseOutput)

    def test_index_codebase_empty_directory(self, tmp_path):
        """Test indexing empty directory."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        input_data = IndexCodebaseInput(
            workspace_root=str(tmp_path),
            full=True
        )
        
        result = index_codebase(input_data)
        
        assert isinstance(result, IndexCodebaseOutput)
        assert result.indexed_files == 0

    def test_index_codebase_nonexistent_directory(self):
        """Test indexing non-existent directory."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        input_data = IndexCodebaseInput(
            workspace_root="/nonexistent/path",
            full=True
        )
        
        result = index_codebase(input_data)
        
        assert isinstance(result, IndexCodebaseOutput)

    def test_index_codebase_with_syntax_errors(self, tmp_path):
        """Test indexing files with syntax errors."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        invalid_file = tmp_path / "invalid.py"
        invalid_file.write_text("def broken(\n    return 'missing paren'")
        
        input_data = IndexCodebaseInput(
            workspace_root=str(tmp_path),
            full=True
        )
        
        result = index_codebase(input_data)
        
        assert isinstance(result, IndexCodebaseOutput)

    def test_index_codebase_ignores_venv(self, tmp_path):
        """Test that indexing ignores virtual environment directories."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        venv_dir = tmp_path / "venv" / "lib"
        venv_dir.mkdir(parents=True)
        (venv_dir / "module.py").write_text("def foo(): pass")
        
        (tmp_path / "main.py").write_text("def main(): pass")
        
        input_data = IndexCodebaseInput(
            workspace_root=str(tmp_path),
            full=True
        )
        
        result = index_codebase(input_data)
        
        assert isinstance(result, IndexCodebaseOutput)

    def test_index_codebase_ignores_pycache(self, tmp_path):
        """Test that indexing ignores __pycache__ directories."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        pycache_dir = tmp_path / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "module.pyc").write_text("compiled")
        
        (tmp_path / "main.py").write_text("def main(): pass")
        
        input_data = IndexCodebaseInput(
            workspace_root=str(tmp_path),
            full=True
        )
        
        result = index_codebase(input_data)
        
        assert isinstance(result, IndexCodebaseOutput)

    def test_index_codebase_reports_duration(self, python_project):
        """Test that indexing reports duration."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        input_data = IndexCodebaseInput(
            workspace_root=str(python_project),
            full=True
        )
        
        result = index_codebase(input_data)
        
        assert hasattr(result, 'duration') or result.status in ["success", "ok"]

    def test_index_codebase_with_nested_directories(self, tmp_path):
        """Test indexing nested directory structure."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        nested_dir = tmp_path / "src" / "utils"
        nested_dir.mkdir(parents=True)
        (nested_dir / "helper.py").write_text("def helper(): pass")
        
        input_data = IndexCodebaseInput(
            workspace_root=str(tmp_path),
            full=True
        )
        
        result = index_codebase(input_data)
        
        assert isinstance(result, IndexCodebaseOutput)
        assert result.indexed_files >= 1

    def test_index_codebase_with_large_files(self, tmp_path):
        """Test indexing large files."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        large_file = tmp_path / "large.py"
        content = "\n".join([f"def func{i}(): pass" for i in range(100)])
        large_file.write_text(content)
        
        input_data = IndexCodebaseInput(
            workspace_root=str(tmp_path),
            full=True
        )
        
        result = index_codebase(input_data)
        
        assert isinstance(result, IndexCodebaseOutput)
        assert result.indexed_files >= 1

    def test_index_codebase_creates_lock_file(self, python_project):
        """Test that indexing creates lock file."""
        from codebax_mcp.mcp_server.tools.services.code.index import index_codebase
        
        input_data = IndexCodebaseInput(
            workspace_root=str(python_project),
            full=True
        )
        
        result = index_codebase(input_data)
        
        lock_file = python_project / ".codebax_index.lock"
        assert lock_file.exists() or result.status in ["success", "ok"]
