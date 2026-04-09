"""MCP server instance for tool registration.

This module provides access to the FastMCP server instance for registering tools
in the tool package modules (__init__.py files).
"""

from mcp.server import FastMCP

# This will be set by the MCPServerFactory when the server is created
mcp: FastMCP | None = None


def set_mcp_instance(instance: FastMCP) -> None:
    """Set the MCP server instance for tool registration."""
    global mcp
    mcp = instance


def get_mcp_instance() -> FastMCP:
    """Get the MCP server instance."""
    global mcp
    if mcp is None:
        raise RuntimeError("MCP server instance not initialized. Call set_mcp_instance() first.")
    return mcp
