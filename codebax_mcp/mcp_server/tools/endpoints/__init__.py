"""MCP tool endpoints - registers all tools with MCP server."""

# Import all endpoint modules to trigger @mcp.tool() registrations
from . import code, project, test
from . import type as type_endpoints

__all__ = ["code", "project", "test", "type_endpoints"]
