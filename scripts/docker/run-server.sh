#!/bin/bash
set -e

#
# Environment variables:
#
# SERVER_HOST → --host
# SERVER_PORT → --port
# MCP_TRANSPORT → --transport
# LOG_LEVEL → --log-level
# ENV_FILE → --env-file
# RELOAD → --reload
# INTEGRATED → --integrated (run in integrated mode)
#

# Initialize command line arguments array
CMD_ARGS=()

# Map environment variables to command line options

# HOST: Host for FastAPI HTTP transports (used for sse or streamable-http)
if [ -n "${SERVER_HOST}" ]; then
  CMD_ARGS+=(--host "${SERVER_HOST}")
fi

# PORT: Port for FastAPI HTTP transports
if [ -n "${SERVER_PORT}" ]; then
  CMD_ARGS+=(--port "${SERVER_PORT}")
fi

# TRANSPORT: Transport mode for MCP server (stdio, sse, http-streaming)
if [ -n "${MCP_TRANSPORT}" ]; then
  CMD_ARGS+=(--transport "${MCP_TRANSPORT}")
fi

# LOG_LEVEL: Python logging level
if [ -n "${LOG_LEVEL}" ]; then
  CMD_ARGS+=(--log-level "${LOG_LEVEL}")
fi

# ENV_FILE: Path to .env file
if [ -n "${ENV_FILE}" ]; then
  CMD_ARGS+=(--env-file "${ENV_FILE}")
fi

# RELOAD: Enable auto-reload for development
if [ -n "${RELOAD}" ] && [ "${RELOAD}" = "true" ]; then
  CMD_ARGS+=(--reload)
fi

# INTEGRATED: Run in integrated mode (MCP + webhook)
if [ -n "${INTEGRATED}" ] && [ "${INTEGRATED}" = "true" ]; then
  CMD_ARGS+=(--integrated)
fi

# Print the command that will be executed
echo "Starting MCP server with arguments: ${CMD_ARGS[@]}"
# Only print debug command information if log level is debug (case insensitive)
if [ -n "${LOG_LEVEL}" ] && [ "$(echo ${LOG_LEVEL} | tr '[:upper:]' '[:lower:]')" == "debug" ]; then
  echo "[DEBUG] Run the MCP server with command: uv run codebax-mcp ${CMD_ARGS[@]}"
fi

# Execute the entry point with the collected arguments
exec uv run codebax-mcp "${CMD_ARGS[@]}"
