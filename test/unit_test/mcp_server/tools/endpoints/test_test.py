"""Unit tests for test tool endpoints."""

from unittest.mock import MagicMock, patch

import pytest

from codebax_mcp.mcp_server.models.output import (
    CreateOrUpdateForSymbolOutput,
    LocateForSourceOutput,
)


class TestTestEndpoints:
    """Test suite for test tool endpoints."""

    @pytest.fixture(autouse=True)
    def mock_mcp_instance(self):
        """Mock MCP instance for all tests."""
        with patch("codebax_mcp.mcp_server.tools.endpoints.code.get_mcp_instance") as mock_get:
            mock_mcp = MagicMock()
            mock_get.return_value = mock_mcp
            yield mock_mcp

    @patch("codebax_mcp.mcp_server.tools.endpoints.test._locate_for_source")
    @pytest.mark.asyncio
    async def test_locate_for_source_endpoint(self, mock_service):
        """Test locate_for_source endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.test import test_locate_for_source

        # Mock service response
        mock_service.return_value = LocateForSourceOutput(
            source_path="src/module.py",
            workspace_root="/test/path",
            existing_tests=[],
            suggested_new_test_path="test/test_module.py",
        )

        # Call endpoint
        result = await test_locate_for_source(
            source_path="src/module.py",
            workspace_root="/test/path",
        )

        # Verify service was called
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.source_path == "src/module.py"
        assert call_args.workspace_root == "/test/path"

        # Verify result
        assert isinstance(result, LocateForSourceOutput)

    @patch("codebax_mcp.mcp_server.tools.endpoints.test._create_or_update_for_symbol")
    @pytest.mark.asyncio
    async def test_create_or_update_for_symbol_endpoint(self, mock_service, tmp_path):
        """Test create_or_update_for_symbol endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.test import test_create_or_update_for_symbol

        # Mock service response
        mock_service.return_value = CreateOrUpdateForSymbolOutput(
            source_path="src/module.py",
            workspace_root=str(tmp_path),
            status="ok",
            test_files_modified=[],
        )

        # Call endpoint
        result = await test_create_or_update_for_symbol(
            source_path="src/module.py",
            symbol="foo",
            language="python",
            intent="add_or_update",
            behavior_description="Test function that adds two numbers",
            workspace_root=str(tmp_path),
        )

        # Verify service was called
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.source_path == "src/module.py"
        assert call_args.symbol == "foo"
        assert call_args.language == "python"
        assert call_args.intent == "add_or_update"

        # Verify result
        assert isinstance(result, CreateOrUpdateForSymbolOutput)
