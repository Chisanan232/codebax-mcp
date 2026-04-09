"""Pytest configuration for endpoint tests."""

import sys
import pytest
from unittest.mock import MagicMock


# Mock MCP modules BEFORE any test imports
def setup_mcp_mocks():
    """Set up MCP mocks in sys.modules."""
    # Create a mock MCP instance
    mock_mcp = MagicMock()
    
    # Make the tool decorator a no-op that just returns the function
    def tool_decorator(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    mock_mcp.tool = tool_decorator
    
    # Mock get_mcp_instance to return our mock
    def mock_get_mcp_instance():
        return mock_mcp
    
    # Create mock app module
    mock_app_module = MagicMock()
    mock_app_module.mcp = mock_mcp
    mock_app_module.get_mcp_instance = mock_get_mcp_instance
    
    # Create mock tools.app module  
    mock_tools_app_module = MagicMock()
    mock_tools_app_module.get_mcp_instance = mock_get_mcp_instance
    mock_tools_app_module.mcp = mock_mcp
    
    # Inject mocks into sys.modules
    sys.modules['codebax_mcp.mcp_server.app'] = mock_app_module
    sys.modules['codebax_mcp.mcp_server.tools.app'] = mock_tools_app_module
    
    return mock_mcp


# Set up mocks immediately when conftest is loaded
_mock_mcp = setup_mcp_mocks()


@pytest.fixture(scope="session", autouse=True)
def mock_mcp_app():
    """Provide the mock MCP instance to tests."""
    yield _mock_mcp
