"""Unit tests for type tool endpoints."""

from unittest.mock import MagicMock, patch

import pytest

from codebax_mcp.mcp_server.models.output import (
    FindSimilarUsagesOutput,
    GetExpectedAtPositionOutput,
    GetSymbolInfoOutput,
    GetTechStackPreferencesOutput,
    InferExpressionOutput,
    SuggestFixOutput,
    ValidateChangesOutput,
)


class TestTypeEndpoints:
    """Test suite for type tool endpoints."""

    @pytest.fixture(autouse=True)
    def mock_mcp_instance(self):
        """Mock MCP instance for all tests."""
        with patch("codebax_mcp.mcp_server.tools.endpoints.code.get_mcp_instance") as mock_get:
            mock_mcp = MagicMock()
            mock_get.return_value = mock_mcp
            yield mock_mcp

    @patch("codebax_mcp.mcp_server.tools.endpoints.type._get_symbol_info")
    @pytest.mark.asyncio
    async def test_get_symbol_info_endpoint(self, mock_service):
        """Test get_symbol_info endpoint delegates to service."""
        from codebax_mcp.mcp_server.models.output import (
            DefinedIn,
            NormalizedType,
            ReturnType,
            SignatureInfo,
        )
        from codebax_mcp.mcp_server.tools.endpoints.type import type_get_symbol_info

        # Mock service response
        mock_service.return_value = GetSymbolInfoOutput(
            symbol="foo",
            kind="function",
            language="python",
            defined_in=DefinedIn(file="test.py", line=1, column=0),
            signature=SignatureInfo(
                parameters=[], return_type=ReturnType(raw=None, normalized=NormalizedType(kind="unknown", types=[]))
            ),
            confidence=0.8,
        )

        # Call endpoint
        result = await type_get_symbol_info(
            symbol="foo",
            workspace_root="/test/path",
        )

        # Verify
        assert mock_service.called
        assert result is not None

    @patch("codebax_mcp.mcp_server.tools.endpoints.type._find_similar_usages")
    @pytest.mark.asyncio
    async def test_find_similar_usages_endpoint(self, mock_service):
        """Test find_similar_usages endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.type import type_find_similar_usages

        # Mock service response
        mock_service.return_value = FindSimilarUsagesOutput(
            symbol="foo",
            similar_symbols=[],
            usages=[],
            total=0,
        )

        # Call endpoint
        result = await type_find_similar_usages(
            symbol="foo",
            workspace_root="/test/path",
        )

        # Verify
        assert mock_service.called
        assert result is not None

    @patch("codebax_mcp.mcp_server.tools.endpoints.type._get_expected_at_position")
    @pytest.mark.asyncio
    async def test_get_expected_at_position_endpoint(self, mock_service):
        """Test get_expected_at_position endpoint delegates to service."""
        from codebax_mcp.mcp_server.models.output import ExpectedType, NormalizedType, Position
        from codebax_mcp.mcp_server.tools.endpoints.type import type_get_expected_at_position

        # Mock service response
        mock_service.return_value = GetExpectedAtPositionOutput(
            file="test.py",
            position=Position(line=10, column=5),
            expected_type=ExpectedType(raw="str", normalized=NormalizedType(kind="primitive", types=[])),
            confidence=0.9,
        )

        # Call endpoint
        result = await type_get_expected_at_position(
            file="test.py",
            line=10,
            column=5,
            workspace_root="/test/path",
        )

        # Verify
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.file == "test.py"
        assert call_args.line == 10
        assert result is not None

    @patch("codebax_mcp.mcp_server.tools.endpoints.type._infer_expression")
    @pytest.mark.asyncio
    async def test_infer_expression_endpoint(self, mock_service):
        """Test infer_expression endpoint delegates to service."""
        from codebax_mcp.mcp_server.models.output import InferredType, NormalizedType
        from codebax_mcp.mcp_server.tools.endpoints.type import type_infer_expression

        # Mock service response
        mock_service.return_value = InferExpressionOutput(
            file="test.py",
            expression="x + y",
            inferred_type=InferredType(raw="int", normalized=NormalizedType(kind="primitive", types=[])),
            source="type_inference",
            confidence=0.85,
        )

        # Call endpoint
        result = await type_infer_expression(
            file="test.py",
            expression="x + y",
            workspace_root="/test/path",
        )

        # Verify
        assert mock_service.called
        assert result is not None

    @patch("codebax_mcp.mcp_server.tools.endpoints.type._validate_changes")
    @pytest.mark.asyncio
    async def test_validate_changes_endpoint(self, mock_service):
        """Test validate_changes endpoint delegates to service."""
        from codebax_mcp.mcp_server.models.input import Change, ChangeEdit
        from codebax_mcp.mcp_server.models.input.type_input import EditRange, Position
        from codebax_mcp.mcp_server.tools.endpoints.type import type_validate_changes

        # Mock service response
        mock_service.return_value = ValidateChangesOutput(
            status="ok",
            diagnostics=[],
        )

        # Call endpoint
        result = await type_validate_changes(
            file="test.py",
            changes=[
                Change(
                    file="test.py",
                    edits=[
                        ChangeEdit(
                            range=EditRange(start=Position(line=1, column=0), end=Position(line=1, column=10)),
                            new_text="new",
                        )
                    ],
                )
            ],
            workspace_root="/test/path",
        )

        # Verify
        assert mock_service.called
        assert result is not None

    @patch("codebax_mcp.mcp_server.tools.endpoints.type._suggest_fix")
    @pytest.mark.asyncio
    async def test_suggest_fix_endpoint(self, mock_service):
        """Test suggest_fix endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.type import type_suggest_fix

        # Mock service response
        mock_service.return_value = SuggestFixOutput(
            fix_kind="import",
            suggestions=[],
            notes="No fixes available",
        )

        # Call endpoint
        result = await type_suggest_fix(
            file="test.py",
            line=10,
            column=5,
            error_message="Type error",
            workspace_root="/test/path",
        )

        # Verify
        assert mock_service.called
        assert result is not None

    @patch("codebax_mcp.mcp_server.tools.endpoints.type._get_tech_stack_preferences")
    @pytest.mark.asyncio
    async def test_get_tech_stack_preferences_endpoint(self, mock_service):
        """Test get_tech_stack_preferences endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.type import type_get_tech_stack_preferences

        # Mock service response
        mock_service.return_value = GetTechStackPreferencesOutput(
            language="python",
            packages={},
            patterns=[],
        )

        # Call endpoint
        result = await type_get_tech_stack_preferences(
            workspace_root="/test/path",
        )

        # Verify
        assert mock_service.called
        assert result is not None
