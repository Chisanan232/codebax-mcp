"""Data transfer objects for health check and other responses.

This module contains Pydantic models for API responses and data transfer objects.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthyCheckResponseDto(BaseModel):
    """Health check response DTO.

    This model represents the health check response returned by the /health endpoint.
    It provides a standardized format for health status reporting.

    Attributes
    ----------
    status : Literal["healthy", "unhealthy"]
        Health status of the server
    timestamp : str | None
        ISO timestamp of when the health check was performed
    version : str | None
        Server version information
    uptime_seconds : float | None
        Server uptime in seconds
    checks : dict[str, bool] | None
        Individual health check results for different components

    """

    model_config = ConfigDict(
        use_enum_values=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "version": "0.1.0",
                "uptime_seconds": 3600.0,
                "checks": {
                    "database": True,
                    "external_api": True,
                    "mcp_server": True,
                },
            }
        },
    )

    status: Literal["healthy", "unhealthy"] = Field(
        default="healthy",
        description="Health status of the server",
    )
    timestamp: str | None = Field(
        default=None,
        description="Timestamp of the health check in ISO format",
    )
    version: str | None = Field(
        default=None,
        description="Server version information",
    )
    uptime_seconds: float | None = Field(
        default=None,
        description="Server uptime in seconds",
    )
    checks: dict[str, bool] | None = Field(
        default=None,
        description="Individual health check results for different components",
    )
