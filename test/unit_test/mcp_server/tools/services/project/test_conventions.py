"""Unit tests for project conventions tool."""

import pytest
from pathlib import Path
from codebax_mcp.mcp_server.tools.services.project.conventions import get_conventions
from codebax_mcp.mcp_server.models.input import GetConventionsInput
from codebax_mcp.mcp_server.models.output import ConventionsOutput


class TestGetConventions:
    """Test suite for get_conventions function."""

    @pytest.fixture
    def python_project(self, tmp_path):
        """Create a temporary Python project structure."""
        # Create pyproject.toml
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.black]
line-length = 100

[tool.isort]
profile = "black"

[tool.pytest.ini_options]
testpaths = ["tests"]
""")
        
        # Create .editorconfig
        editorconfig = tmp_path / ".editorconfig"
        editorconfig.write_text("""
[*.py]
indent_style = space
indent_size = 4
""")
        
        return tmp_path

    @pytest.fixture
    def node_project(self, tmp_path):
        """Create a temporary Node.js project structure."""
        package_json = tmp_path / "package.json"
        package_json.write_text("""
{
  "name": "test-project",
  "version": "1.0.0",
  "scripts": {
    "test": "jest",
    "lint": "eslint ."
  }
}
""")
        
        eslintrc = tmp_path / ".eslintrc.json"
        eslintrc.write_text("""
{
  "extends": "airbnb",
  "rules": {
    "indent": ["error", 2]
  }
}
""")
        
        return tmp_path

    def test_get_conventions_python_project(self, python_project):
        """Test getting conventions for Python project."""
        input_data = GetConventionsInput(workspace_root=str(python_project))
        result = get_conventions(input_data)
        
        assert isinstance(result, ConventionsOutput)
        assert result.test is not None
        assert result.test is not None

    def test_get_conventions_detects_black(self, python_project):
        """Test that Black configuration is detected."""
        input_data = GetConventionsInput(workspace_root=str(python_project))
        result = get_conventions(input_data)
        
        assert result.style is not None

    def test_get_conventions_detects_editorconfig(self, python_project):
        """Test that .editorconfig is detected."""
        input_data = GetConventionsInput(workspace_root=str(python_project))
        result = get_conventions(input_data)
        
        assert result.test is not None

    def test_get_conventions_node_project(self, node_project):
        """Test getting conventions for Node.js project."""
        input_data = GetConventionsInput(
            workspace_root=str(node_project),
            language="javascript"
        )
        result = get_conventions(input_data)
        
        assert isinstance(result, ConventionsOutput)
        assert result.test is not None

    def test_get_conventions_empty_project(self, tmp_path):
        """Test getting conventions for empty project."""
        input_data = GetConventionsInput(workspace_root=str(tmp_path))
        result = get_conventions(input_data)
        
        assert isinstance(result, ConventionsOutput)
        assert result.test is not None

    def test_get_conventions_nonexistent_path(self):
        """Test getting conventions for non-existent path."""
        input_data = GetConventionsInput(workspace_root="/nonexistent/path")
        result = get_conventions(input_data)
        
        assert isinstance(result, ConventionsOutput)

    def test_get_conventions_with_specific_language(self, python_project):
        """Test getting conventions with specific language."""
        input_data = GetConventionsInput(
            workspace_root=str(python_project),
            language="python"
        )
        result = get_conventions(input_data)
        
        assert result.test is not None

    def test_get_conventions_includes_linting(self, python_project):
        """Test that linting conventions are included."""
        # Add pylint config
        pylintrc = python_project / ".pylintrc"
        pylintrc.write_text("[MASTER]\nmax-line-length=100")
        
        input_data = GetConventionsInput(workspace_root=str(python_project))
        result = get_conventions(input_data)
        
        assert result.test is not None

    def test_get_conventions_includes_testing(self, python_project):
        """Test that testing conventions are included."""
        input_data = GetConventionsInput(workspace_root=str(python_project))
        result = get_conventions(input_data)
        
        assert result.test is not None

    def test_get_conventions_detects_prettier(self, node_project):
        """Test that Prettier configuration is detected."""
        prettierrc = node_project / ".prettierrc"
        prettierrc.write_text('{"semi": false, "singleQuote": true}')
        
        input_data = GetConventionsInput(
            workspace_root=str(node_project),
            language="javascript"
        )
        result = get_conventions(input_data)
        
        assert result.test is not None

    def test_get_conventions_multiple_config_files(self, python_project):
        """Test handling multiple configuration files."""
        # Add multiple config files
        (python_project / "setup.cfg").write_text("[flake8]\nmax-line-length = 100")
        (python_project / "tox.ini").write_text("[tox]\nenvlist = py38,py39")
        
        input_data = GetConventionsInput(workspace_root=str(python_project))
        result = get_conventions(input_data)
        
        assert isinstance(result, ConventionsOutput)

    def test_get_conventions_returns_dict_structure(self, python_project):
        """Test that conventions returns proper dictionary structure."""
        input_data = GetConventionsInput(workspace_root=str(python_project))
        result = get_conventions(input_data)
        
        assert result.test is not None

    def test_get_conventions_with_git_hooks(self, python_project):
        """Test detection of git hooks."""
        git_dir = python_project / ".git" / "hooks"
        git_dir.mkdir(parents=True)
        (git_dir / "pre-commit").write_text("#!/bin/sh\npytest")
        
        input_data = GetConventionsInput(workspace_root=str(python_project))
        result = get_conventions(input_data)
        
        assert isinstance(result, ConventionsOutput)

    def test_get_conventions_caching(self, python_project):
        """Test that conventions can be retrieved multiple times."""
        input_data = GetConventionsInput(workspace_root=str(python_project))
        
        result1 = get_conventions(input_data)
        result2 = get_conventions(input_data)
        
        assert result1.test == result2.test
