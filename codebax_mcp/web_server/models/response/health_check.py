"""Health check response models for comprehensive health checking.

This module contains Pydantic models for various health check endpoints,
supporting different levels of detail and use cases.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthCheckDetailDto(BaseModel):
    """Individual health check result detail.

    Attributes
    ----------
    name : str
        Name of the health checker
    status : Literal["healthy", "degraded", "unhealthy"]
        Status of the component
    message : str | None
        Optional message providing additional context
    details : dict[str, Any] | None
        Additional details about the health check result

    """

    name: str = Field(description="Name of the health checker")
    status: Literal["healthy", "degraded", "unhealthy"] = Field(description="Status of the component")
    message: str | None = Field(
        default=None,
        description="Optional message providing additional context",
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Additional details about the health check result",
    )


class ComprehensiveHealthResponseDto(BaseModel):
    """Comprehensive health check response with detailed component status.

    This model provides detailed health information including individual
    component status, timestamp, and version information.

    Attributes
    ----------
    status : Literal["healthy", "degraded", "unhealthy"]
        Overall health status
    timestamp : str
        ISO timestamp of when the health check was performed
    version : str
        Server version information
    uptime_seconds : float
        Server uptime in seconds
    checks : list[HealthCheckDetailDto]
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
                "checks": [
                    {
                        "name": "application",
                        "status": "healthy",
                        "message": "All systems operational",
                        "details": {"version": "0.1.0", "components": ["restapi", "mcp"]},
                    },
                    {
                        "name": "mcp_server",
                        "status": "healthy",
                        "message": "MCP server is running",
                        "details": {"transport": "sse"},
                    },
                ],
            }
        },
    )

    status: Literal["healthy", "degraded", "unhealthy"] = Field(description="Overall health status of the server")
    timestamp: str = Field(description="Timestamp of the health check in ISO format")
    version: str = Field(description="Server version information")
    uptime_seconds: float = Field(description="Server uptime in seconds")
    checks: list[HealthCheckDetailDto] = Field(description="Individual health check results for different components")


class SimpleHealthResponseDto(BaseModel):
    """Simple health check response for load balancers.

    This model provides a minimal health check response suitable
    for load balancers and monitoring systems.

    Attributes
    ----------
    status : Literal["ok", "error"]
        Simple health status

    """

    model_config = ConfigDict(
        use_enum_values=True,
        extra="forbid",
        json_schema_extra={"example": {"status": "ok"}},
    )

    status: Literal["ok", "error"] = Field(description="Simple health status (ok or error)")


class ReadinessResponseDto(BaseModel):
    """Readiness check response for Kubernetes and orchestration systems.

    Attributes
    ----------
    ready : bool
        Whether the application is ready to serve traffic
    message : str | None
        Optional message explaining readiness status

    """

    model_config = ConfigDict(
        use_enum_values=True,
        extra="forbid",
        json_schema_extra={"example": {"ready": True, "message": "Application is ready to serve traffic"}},
    )

    ready: bool = Field(description="Whether the application is ready to serve traffic")
    message: str | None = Field(
        default=None,
        description="Optional message explaining readiness status",
    )


class LivenessResponseDto(BaseModel):
    """Liveness check response for Kubernetes and orchestration systems.

    Attributes
    ----------
    alive : bool
        Whether the application process is alive and responsive

    """

    model_config = ConfigDict(
        use_enum_values=True,
        extra="forbid",
        json_schema_extra={"example": {"alive": True}},
    )

    alive: bool = Field(description="Whether the application process is alive and responsive")
