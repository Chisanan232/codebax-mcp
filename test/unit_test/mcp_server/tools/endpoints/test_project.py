"""Unit tests for project tool endpoints."""

from unittest.mock import MagicMock, patch

import pytest

from codebax_mcp.mcp_server.models.output import (
    ConventionsOutput,
    ExecutionProfileOutput,
    LayoutOutput,
    SubprojectsOutput,
)


class TestProjectEndpoints:
    """Test suite for project tool endpoints."""

    @pytest.fixture(autouse=True)
    def mock_mcp_instance(self):
        """Mock MCP instance for all tests."""
        with patch("codebax_mcp.mcp_server.tools.endpoints.project.get_mcp_instance") as mock_get:
            mock_mcp = MagicMock()
            mock_get.return_value = mock_mcp
            yield mock_mcp

    @patch("codebax_mcp.mcp_server.tools.endpoints.project._get_conventions")
    @pytest.mark.asyncio
    async def test_get_conventions_endpoint(self, mock_service):
        """Test get_conventions endpoint delegates to service."""
        # Mock service response
        from codebax_mcp.mcp_server.models.output import (
            JvmTooling,
            NodeScripts,
            NodeTooling,
            NodeWorkspace,
            PreCommitConfig,
            ProjectConstraints,
            PythonStyle,
            PythonTooling,
            SourceConventions,
            StyleConventions,
            TestConventions,
            ToolingConventions,
            TypeScriptStyle,
        )
        from codebax_mcp.mcp_server.tools.endpoints.project import project_get_conventions

        mock_service.return_value = ConventionsOutput(
            test=TestConventions(root="test", framework=None, file_patterns=[], naming_style=None),
            source=SourceConventions(roots=[], module_layout=None),
            style=StyleConventions(
                python=PythonStyle(formatter=None, type_checker=None),
                typescript=TypeScriptStyle(formatter=None, test_framework=None),
            ),
            tooling=ToolingConventions(
                python=PythonTooling(
                    manager=None,
                    entry=None,
                    lock_files=[],
                    test_command=None,
                    lint_commands=[],
                    pre_commit=PreCommitConfig(enabled=False, config=None, run_command=None),
                ),
                node=NodeTooling(
                    manager=None,
                    root_package_json=None,
                    workspace=NodeWorkspace(enabled=False, tool=None, config=None),
                    scripts=NodeScripts(test=None, lint=None, build=None),
                ),
                jvm=JvmTooling(build_tool=None, wrapper=None, subprojects=[], test_command=None),
            ),
            constraints=ProjectConstraints(forbid_creating_dirs=[], prefer_existing_over_new=False),
        )

        # Call endpoint
        result = await project_get_conventions(
            workspace_root="/test/path",
            language_hint="python",
        )

        # Verify service was called
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.workspace_root == "/test/path"
        assert call_args.language_hint == "python"

        # Verify result
        assert isinstance(result, ConventionsOutput)

    @patch("codebax_mcp.mcp_server.tools.endpoints.project._describe_layout")
    @pytest.mark.asyncio
    async def test_describe_layout_endpoint(self, mock_service):
        """Test describe_layout endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.project import project_describe_layout

        # Mock service response
        mock_service.return_value = LayoutOutput(
            roots=[],
            modules=[],
            test_roots=[],
        )

        # Call endpoint
        result = await project_describe_layout(
            workspace_root="/test/path",
        )

        # Verify
        assert mock_service.called
        call_args = mock_service.call_args[0][0]
        assert call_args.workspace_root == "/test/path"
        assert isinstance(result, LayoutOutput)

    @patch("codebax_mcp.mcp_server.tools.endpoints.project._list_subprojects")
    @pytest.mark.asyncio
    async def test_list_subprojects_endpoint(self, mock_service):
        """Test list_subprojects endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.project import project_list_subprojects

        # Mock service response
        mock_service.return_value = SubprojectsOutput(
            workspace_root="/test/path",
            subprojects=[],
            total=0,
        )

        # Call endpoint
        result = await project_list_subprojects(
            workspace_root="/test/path",
        )

        # Verify
        assert mock_service.called
        assert isinstance(result, SubprojectsOutput)

    @patch("codebax_mcp.mcp_server.tools.endpoints.project._get_execution_profile")
    @pytest.mark.asyncio
    async def test_get_execution_profile_endpoint(self, mock_service):
        """Test get_execution_profile endpoint delegates to service."""
        from codebax_mcp.mcp_server.tools.endpoints.project import project_get_execution_profile

        # Mock service response
        mock_service.return_value = ExecutionProfileOutput(
            command="pytest",
            cwd="/test/path",
            pre_steps=[],
        )

        # Call endpoint
        result = await project_get_execution_profile(
            workspace_root="/test/path",
            intent="test",
        )

        # Verify
        assert mock_service.called
        assert isinstance(result, ExecutionProfileOutput)
