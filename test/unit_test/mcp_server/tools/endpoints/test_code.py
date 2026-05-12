"""Unit tests for code tool endpoints."""

from unittest.mock import MagicMock, patch

import pytest

from codebax_mcp.mcp_server.models.output import (
    AnalyzePythonPatchCallsOutput,
    DefinitionLocation,
    ExtractFunctionOutput,
    FindUsagesOutput,
    GetCallGraphOutput,
    GetDefinitionOutput,
    IdentifySymbolOutput,
    IndexCodebaseOutput,
    RenameSymbolOutput,
    SemanticSearchOutput,
)


class TestCodeEndpoints:
    """Test suite for code tool endpoints."""

    @pytest.fixture(autouse=True)
    def mock_mcp_instance(self):
        """Mock MCP instance for all tests."""
        with patch("codebax_mcp.mcp_server.tools.endpoints.code.get_mcp_instance") as mock_get:
            mock_mcp = MagicMock()
            mock_get.return_value = mock_mcp
            yield mock_mcp

    @patch("codebax_mcp.mcp_server.tools.endpoints.code._index_codebase")
    @pytest.mark.asyncio
    async def test_index_codebase_endpoint(self, mock_service):
        """Test index_codebase endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.code import code_index

        # Mock service response
        mock_service.return_value = IndexCodebaseOutput(
            status="ok",
            indexed_files=10,
        )

        # Call endpoint
        result = await code_index(
            workspace_root="/test/path",
            paths=None,
            full=False,
        )

        # Verify service was called with correct input
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.workspace_root == "/test/path"
        assert call_args.full is False

        # Verify result
        assert result is not None
        assert result.status == "ok"
        assert result.indexed_files == 10

    @patch("codebax_mcp.mcp_server.tools.endpoints.code._identify_symbol")
    @pytest.mark.asyncio
    async def test_identify_symbol_endpoint(self, mock_service):
        """Test identify_symbol endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.code import code_identify_symbol

        # Mock service response
        mock_service.return_value = IdentifySymbolOutput(
            symbol_id="test:func:foo:1",
            name="foo",
            kind="function",
            language="python",
            defined_in=DefinitionLocation(file="test.py", line=10, column=0),
        )

        # Call endpoint
        result = await code_identify_symbol(
            file="test.py",
            line=10,
            column=5,
            workspace_root="/test/path",
            language="python",
        )

        # Verify service was called
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.file == "test.py"
        assert call_args.line == 10
        assert call_args.column == 5

        # Verify result
        assert result is not None
        assert result.symbol_id == "test:func:foo:1"

    @patch("codebax_mcp.mcp_server.tools.endpoints.code._get_definition")
    @pytest.mark.asyncio
    async def test_get_definition_endpoint(self, mock_service):
        """Test get_definition endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.code import code_get_definition

        # Mock service response
        mock_service.return_value = GetDefinitionOutput(
            symbol_id="test:func:foo:1",
            name="foo",
            kind="function",
            language="python",
            defined_in=DefinitionLocation(file="test.py", line=10, column=0),
        )

        # Call endpoint
        result = await code_get_definition(
            symbol_id="test:func:foo:1",
            workspace_root="/test/path",
        )

        # Verify
        assert mock_service.called
        assert result is not None
        assert result.symbol_id == "test:func:foo:1"

    @patch("codebax_mcp.mcp_server.tools.endpoints.code._find_usages")
    @pytest.mark.asyncio
    async def test_find_usages_endpoint(self, mock_service):
        """Test find_usages endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.code import code_find_usages

        # Mock service response
        mock_service.return_value = FindUsagesOutput(
            symbol_id="test:func:foo:1",
            usages=[],
            total=0,
        )

        # Call endpoint
        result = await code_find_usages(
            symbol_id="test:func:foo:1",
            workspace_root="/test/path",
            include_tests=True,
        )

        # Verify
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.include_tests is True
        assert result is not None

    @patch("codebax_mcp.mcp_server.tools.endpoints.code._get_call_graph")
    @pytest.mark.asyncio
    async def test_get_call_graph_endpoint(self, mock_service):
        """Test get_call_graph endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.code import code_get_call_graph

        # Mock service response
        mock_service.return_value = GetCallGraphOutput(
            symbol_id="test:func:foo:1",
            nodes=[],
            edges=[],
            direction="both",
        )

        # Call endpoint
        result = await code_get_call_graph(
            symbol_id="test:func:foo:1",
            workspace_root="/test/path",
            depth=2,
        )

        # Verify
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.depth == 2
        assert result is not None

    @patch("codebax_mcp.mcp_server.tools.endpoints.code._rename_symbol")
    @pytest.mark.asyncio
    async def test_rename_symbol_endpoint(self, mock_service):
        """Test rename_symbol endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.code import code_rename_symbol

        # Mock service response
        mock_service.return_value = RenameSymbolOutput(
            status="ok",
            symbol_id="test:func:foo:1",
            new_name="bar",
            changes=[],
        )

        # Call endpoint
        result = await code_rename_symbol(
            symbol_id="test:func:foo:1",
            new_name="bar",
            workspace_root="/test/path",
            dry_run=True,
        )

        # Verify
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.new_name == "bar"
        assert call_args.dry_run is True
        assert result is not None

    @patch("codebax_mcp.mcp_server.tools.endpoints.code._extract_function")
    @pytest.mark.asyncio
    async def test_extract_function_endpoint(self, mock_service):
        """Test extract_function endpoint delegates to service."""
        from codebax_mcp.mcp_server.models.input import CodeRange, Position
        from codebax_mcp.mcp_server.tools.endpoints.code import code_extract_function

        # Mock service response
        mock_service.return_value = ExtractFunctionOutput(
            status="ok",
            file="test.py",
            new_function_name="extracted_func",
            changes=[],
        )

        # Call endpoint
        result = await code_extract_function(
            file="test.py",
            language="python",
            range=CodeRange(start=Position(line=10, column=0), end=Position(line=20, column=0)),
            new_name="extracted_func",
            workspace_root="/test/path",
        )

        # Verify
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.range.start.line == 10
        assert call_args.range.end.line == 20
        assert result is not None

    @patch("codebax_mcp.mcp_server.tools.endpoints.code._semantic_search")
    @pytest.mark.asyncio
    async def test_semantic_search_endpoint(self, mock_service):
        """Test semantic_search endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.code import code_semantic_search

        # Mock service response
        mock_service.return_value = SemanticSearchOutput(
            query="find authentication",
            results=[],
            total=0,
        )

        # Call endpoint
        result = await code_semantic_search(
            query="find authentication",
            workspace_root="/test/path",
            top_k=10,
        )

        # Verify
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.query == "find authentication"
        assert call_args.top_k == 10
        assert result is not None

    @patch("codebax_mcp.mcp_server.tools.endpoints.code._analyze_python_patch_calls")
    @pytest.mark.asyncio
    async def test_analyze_python_patch_calls_endpoint(self, mock_service):
        """Test analyze_python_patch_calls endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.code import code_analyze_python_patch_calls

        # Mock service response
        mock_service.return_value = AnalyzePythonPatchCallsOutput(
            patches=[],
            total=0,
        )

        # Call endpoint
        result = await code_analyze_python_patch_calls(
            workspace_root="/test/path",
        )

        # Verify
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.workspace_root == "/test/path"
        assert result is not None
