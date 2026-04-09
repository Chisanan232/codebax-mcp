"""Unit tests for input models."""

import pytest
from pydantic import ValidationError

from codebax_mcp.mcp_server.models.input import (
    CreateOrUpdateForSymbolInput,
    DescribeLayoutInput,
    ExtractFunctionInput,
    FindUsagesInput,
    GetConventionsInput,
    GetDefinitionInput,
    IdentifySymbolInput,
    IndexCodebaseInput,
    LocateForSourceInput,
    RenameSymbolInput,
    SemanticSearchInput,
)


class TestGetConventionsInput:
    """Test suite for GetConventionsInput model."""

    def test_get_conventions_input_creation(self):
        """Test creating GetConventionsInput."""
        input_data = GetConventionsInput(workspace_root="/path/to/project")

        assert input_data.workspace_root == "/path/to/project"
        assert input_data.language_hint is None

    def test_get_conventions_input_with_language(self):
        """Test GetConventionsInput with language."""
        input_data = GetConventionsInput(workspace_root="/path/to/project", language_hint="python")

        assert input_data.language_hint == "python"

    def test_get_conventions_input_missing_required(self):
        """Test that workspace_root is required."""
        with pytest.raises(ValidationError):
            GetConventionsInput()


class TestDescribeLayoutInput:
    """Test suite for DescribeLayoutInput model."""

    def test_describe_layout_input_creation(self):
        """Test creating DescribeLayoutInput."""
        input_data = DescribeLayoutInput(workspace_root="/path/to/project")

        assert input_data.workspace_root == "/path/to/project"

    def test_describe_layout_input_basic(self):
        """Test DescribeLayoutInput basic creation."""
        input_data = DescribeLayoutInput(workspace_root="/path/to/project")

        assert input_data.workspace_root == "/path/to/project"


class TestIndexCodebaseInput:
    """Test suite for IndexCodebaseInput model."""

    def test_index_codebase_input_creation(self):
        """Test creating IndexCodebaseInput."""
        input_data = IndexCodebaseInput(workspace_root="/path/to/project")

        assert input_data.workspace_root == "/path/to/project"
        assert input_data.full is False

    def test_index_codebase_input_full_index(self):
        """Test IndexCodebaseInput with full=True."""
        input_data = IndexCodebaseInput(workspace_root="/path/to/project", full=True)

        assert input_data.full is True

    def test_index_codebase_input_with_paths(self):
        """Test IndexCodebaseInput with specific paths."""
        input_data = IndexCodebaseInput(workspace_root="/path/to/project", paths=["module1.py", "module2.py"])

        assert len(input_data.paths) == 2
        assert "module1.py" in input_data.paths


class TestIdentifySymbolInput:
    """Test suite for IdentifySymbolInput model."""

    def test_identify_symbol_input_creation(self):
        """Test creating IdentifySymbolInput."""
        input_data = IdentifySymbolInput(file="test.py", language="python", line=10, column=5)

        assert input_data.file == "test.py"
        assert input_data.line == 10
        assert input_data.column == 5

    def test_identify_symbol_input_with_workspace(self):
        """Test IdentifySymbolInput with workspace_root."""
        input_data = IdentifySymbolInput(
            file="test.py", language="python", line=10, column=5, workspace_root="/path/to/project"
        )

        assert input_data.workspace_root == "/path/to/project"

    def test_identify_symbol_input_missing_required(self):
        """Test that required fields are validated."""
        with pytest.raises(ValidationError):
            IdentifySymbolInput(file="test.py", line=10)


class TestGetDefinitionInput:
    """Test suite for GetDefinitionInput model."""

    def test_get_definition_input_creation(self):
        """Test creating GetDefinitionInput."""
        input_data = GetDefinitionInput(symbol_id="test:func:foo:1")

        assert input_data.symbol_id == "test:func:foo:1"

    def test_get_definition_input_with_workspace(self):
        """Test GetDefinitionInput with workspace_root."""
        input_data = GetDefinitionInput(symbol_id="test:func:foo:1", workspace_root="/path/to/project")

        assert input_data.workspace_root == "/path/to/project"


class TestFindUsagesInput:
    """Test suite for FindUsagesInput model."""

    def test_find_usages_input_creation(self):
        """Test creating FindUsagesInput."""
        input_data = FindUsagesInput(symbol_id="test:func:foo:1")

        assert input_data.symbol_id == "test:func:foo:1"
        assert input_data.include_tests is False

    def test_find_usages_input_with_options(self):
        """Test FindUsagesInput with options."""
        input_data = FindUsagesInput(symbol_id="test:func:foo:1", include_tests=True, max_results=100)

        assert input_data.include_tests is True
        assert input_data.max_results == 100


class TestRenameSymbolInput:
    """Test suite for RenameSymbolInput model."""

    def test_rename_symbol_input_creation(self):
        """Test creating RenameSymbolInput."""
        input_data = RenameSymbolInput(symbol_id="test:func:foo:1", new_name="bar")

        assert input_data.symbol_id == "test:func:foo:1"
        assert input_data.new_name == "bar"

    def test_rename_symbol_input_dry_run(self):
        """Test RenameSymbolInput with dry_run."""
        input_data = RenameSymbolInput(symbol_id="test:func:foo:1", new_name="bar", dry_run=True)

        assert input_data.dry_run is True

    def test_rename_symbol_input_missing_new_name(self):
        """Test that new_name is required."""
        with pytest.raises(ValidationError):
            RenameSymbolInput(symbol_id="test:func:foo:1")


class TestExtractFunctionInput:
    """Test suite for ExtractFunctionInput model."""

    def test_extract_function_input_creation(self):
        """Test creating ExtractFunctionInput."""
        from codebax_mcp.mcp_server.models.input import CodeRange, Position

        input_data = ExtractFunctionInput(
            file="test.py",
            language="python",
            range=CodeRange(start=Position(line=10, column=0), end=Position(line=20, column=0)),
            new_name="extracted_func",
        )

        assert input_data.file == "test.py"
        assert input_data.language == "python"
        assert input_data.range.start.line == 10
        assert input_data.range.end.line == 20
        assert input_data.new_name == "extracted_func"

    def test_extract_function_input_with_dry_run(self):
        """Test ExtractFunctionInput with dry_run."""
        from codebax_mcp.mcp_server.models.input import CodeRange, Position

        input_data = ExtractFunctionInput(
            file="test.py",
            language="python",
            range=CodeRange(start=Position(line=10, column=0), end=Position(line=20, column=0)),
            new_name="extracted_func",
            dry_run=True,
        )

        assert input_data.dry_run is True


class TestSemanticSearchInput:
    """Test suite for SemanticSearchInput model."""

    def test_semantic_search_input_creation(self):
        """Test creating SemanticSearchInput."""
        input_data = SemanticSearchInput(query="find authentication code")

        assert input_data.query == "find authentication code"
        assert input_data.top_k == 10

    def test_semantic_search_input_with_filters(self):
        """Test SemanticSearchInput with filters."""
        input_data = SemanticSearchInput(
            query="find authentication code",
            filter_language="python",
            filter_path_prefix="src/auth",
        )

        assert input_data.filter_path_prefix == "src/auth"
        assert input_data.filter_language == "python"

    def test_semantic_search_input_missing_query(self):
        """Test that query is required."""
        with pytest.raises(ValidationError):
            SemanticSearchInput()


class TestLocateForSourceInput:
    """Test suite for LocateForSourceInput model."""

    def test_locate_for_source_input_creation(self):
        """Test creating LocateForSourceInput."""
        input_data = LocateForSourceInput(source_path="src/module.py", workspace_root="/path/to/project")

        assert input_data.source_path == "src/module.py"
        assert input_data.workspace_root == "/path/to/project"

    def test_locate_for_source_input_default_workspace(self):
        """Test LocateForSourceInput with default workspace."""
        input_data = LocateForSourceInput(source_path="src/module.py")

        assert input_data.workspace_root == "."


class TestCreateOrUpdateForSymbolInput:
    """Test suite for CreateOrUpdateForSymbolInput model."""

    def test_create_or_update_input_creation(self):
        """Test creating CreateOrUpdateForSymbolInput."""
        input_data = CreateOrUpdateForSymbolInput(
            source_path="src/module.py",
            symbol="foo",
            language="python",
            intent="add_or_update",
            behavior_description="Test function that adds two numbers",
            workspace_root="/path/to/project",
        )

        assert input_data.source_path == "src/module.py"
        assert input_data.symbol == "foo"
        assert input_data.workspace_root == "/path/to/project"

    def test_create_or_update_input_with_default_workspace(self):
        """Test CreateOrUpdateForSymbolInput with default workspace."""
        input_data = CreateOrUpdateForSymbolInput(
            source_path="src/module.py",
            symbol="foo",
            language="python",
            intent="add_or_update",
            behavior_description="Test function",
        )

        assert input_data.workspace_root == "."
        assert input_data.language == "python"
