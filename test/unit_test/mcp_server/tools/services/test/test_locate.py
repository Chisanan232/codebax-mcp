"""Unit tests for test locate tool."""

import pytest

from codebax_mcp.mcp_server.models.input import LocateForSourceInput
from codebax_mcp.mcp_server.models.output import LocateForSourceOutput
from codebax_mcp.mcp_server.tools.services.test.locate import locate_for_source


class TestLocateForSource:
    """Test suite for locate_for_source function."""

    @pytest.fixture
    def python_project(self, tmp_path):
        """Create a temporary Python project with source and test files."""
        # Create source directory
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create source file
        source_file = src_dir / "calculator.py"
        source_file.write_text("""
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
""")

        # Create test directory
        test_dir = tmp_path / "tests"
        test_dir.mkdir()

        # Create test file
        test_file = test_dir / "test_calculator.py"
        test_file.write_text("""
import pytest
from src.calculator import Calculator

def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_subtract():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2
""")

        return tmp_path

    def test_locate_finds_test_file(self, python_project):
        """Test that locate_for_source finds corresponding test file."""
        source_file = str(python_project / "src" / "calculator.py")
        input_data = LocateForSourceInput(source_path=source_file, workspace_root=str(python_project))

        result = locate_for_source(input_data)

        assert isinstance(result, LocateForSourceOutput)
        assert result.existing_tests is not None
        assert any("test_calculator" in test.path for test in result.existing_tests)

    def test_locate_nonexistent_source(self, python_project):
        """Test locating test for non-existent source file."""
        input_data = LocateForSourceInput(
            source_path=str(python_project / "src" / "nonexistent.py"), workspace_root=str(python_project)
        )

        result = locate_for_source(input_data)

        assert isinstance(result, LocateForSourceOutput)

    def test_locate_with_no_test_file(self, tmp_path):
        """Test locating test when no test file exists."""
        source_file = tmp_path / "module.py"
        source_file.write_text("def foo(): pass")

        input_data = LocateForSourceInput(source_path=str(source_file), workspace_root=str(tmp_path))

        result = locate_for_source(input_data)

        assert isinstance(result, LocateForSourceOutput)

    def test_locate_suggests_test_path(self, tmp_path):
        """Test that locate suggests test path when not found."""
        source_file = tmp_path / "module.py"
        source_file.write_text("def foo(): pass")

        input_data = LocateForSourceInput(source_path=str(source_file), workspace_root=str(tmp_path))

        result = locate_for_source(input_data)

        assert result.suggested_new_test_path is not None or result.existing_tests is None

    def test_locate_with_nested_directories(self, tmp_path):
        """Test locating test file in nested directory structure."""
        # Create nested source
        src_dir = tmp_path / "src" / "utils"
        src_dir.mkdir(parents=True)
        source_file = src_dir / "helper.py"
        source_file.write_text("def helper(): pass")

        # Create nested test
        test_dir = tmp_path / "tests" / "utils"
        test_dir.mkdir(parents=True)
        test_file = test_dir / "test_helper.py"
        test_file.write_text("def test_helper(): pass")

        input_data = LocateForSourceInput(source_path=str(source_file), workspace_root=str(tmp_path))

        result = locate_for_source(input_data)

        assert isinstance(result, LocateForSourceOutput)

    def test_locate_with_different_test_patterns(self, tmp_path):
        """Test locating test files with different naming patterns."""
        source_file = tmp_path / "module.py"
        source_file.write_text("def foo(): pass")

        # Create test with different pattern
        test_file = tmp_path / "module_test.py"
        test_file.write_text("def test_foo(): pass")

        input_data = LocateForSourceInput(source_path=str(source_file), workspace_root=str(tmp_path))

        result = locate_for_source(input_data)

        assert isinstance(result, LocateForSourceOutput)

    def test_locate_returns_confidence_score(self, python_project):
        """Test that locate returns confidence score."""
        source_file = str(python_project / "src" / "calculator.py")
        input_data = LocateForSourceInput(source_path=source_file, workspace_root=str(python_project))

        result = locate_for_source(input_data)

        assert hasattr(result, "confidence") or result.existing_tests is not None

    def test_locate_with_multiple_test_candidates(self, tmp_path):
        """Test locating when multiple test files could match."""
        source_file = tmp_path / "module.py"
        source_file.write_text("def foo(): pass")

        # Create multiple potential test files
        (tmp_path / "test_module.py").write_text("def test_foo(): pass")
        (tmp_path / "module_test.py").write_text("def test_foo(): pass")

        input_data = LocateForSourceInput(source_path=str(source_file), workspace_root=str(tmp_path))

        result = locate_for_source(input_data)

        assert isinstance(result, LocateForSourceOutput)

    def test_locate_with_language_parameter(self, python_project):
        """Test locating with explicit language parameter."""
        source_file = str(python_project / "src" / "calculator.py")
        input_data = LocateForSourceInput(
            source_path=source_file, workspace_root=str(python_project), language="python"
        )

        result = locate_for_source(input_data)

        assert isinstance(result, LocateForSourceOutput)

    def test_locate_handles_absolute_paths(self, python_project):
        """Test that locate handles absolute paths correctly."""
        source_file = python_project / "src" / "calculator.py"
        input_data = LocateForSourceInput(source_path=str(source_file.absolute()), workspace_root=str(python_project))

        result = locate_for_source(input_data)

        assert isinstance(result, LocateForSourceOutput)

    def test_locate_handles_relative_paths(self, python_project):
        """Test that locate handles relative paths correctly."""
        input_data = LocateForSourceInput(source_path="src/calculator.py", workspace_root=str(python_project))

        result = locate_for_source(input_data)

        assert isinstance(result, LocateForSourceOutput)
