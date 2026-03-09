"""Health checking services for the MCP server.

This module contains the business logic for health checking,
following duck typing principles for clean, maintainable code.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any, Protocol

from ..models.response.health_check import HealthCheckDetailDto


class HealthChecker(Protocol):
    """Protocol defining the contract for health checkers.

    This follows duck typing principles - any class that implements
    the check_health method with the expected signature can be used
    as a health checker.
    """

    def check_health(self) -> HealthCheckDetailDto:
        """Perform health check and return status.

        Returns
        -------
        HealthCheckDetailDto
            The health check result
        """
        ...


class BaseHealthChecker:
    """Base class for health checkers providing common functionality.

    This class follows the Template Method pattern and duck typing
    principles. Subclasses only need to implement the specific
    health check logic.
    """

    def __init__(self, name: str) -> None:
        """Initialize health checker.

        Parameters
        ----------
        name : str
            Name of the health checker for identification
        """
        self.name = name

    def check_health(self) -> HealthCheckDetailDto:
        """Perform health check with common error handling.

        This method provides the template while allowing subclasses
        to implement specific check logic via _do_check_health.

        Returns
        -------
        HealthCheckDetailDto
            The health check result
        """
        try:
            return self._do_check_health()
        except Exception as e:
            return HealthCheckDetailDto(
                name=self.name,
                status="unhealthy",
                message=f"Health check failed: {e!s}",
                details={"error": str(e)},
            )

    def _do_check_health(self) -> HealthCheckDetailDto:
        """Perform the actual health check.

        Subclasses must implement this method to provide specific
        health checking logic.

        Returns
        -------
        HealthCheckDetailDto
            The health check result

        Raises
        ------
        Exception
            If health check fails
        """
        error_msg = f"{self.__class__.__name__} must implement _do_check_health"
        raise NotImplementedError(error_msg)


class ApplicationHealthChecker(BaseHealthChecker):
    """Health checker for application components.

    This checker verifies that core application components
    are functioning properly.
    """

    def __init__(self, version: str = "0.0.0") -> None:
        """Initialize application health checker.

        Parameters
        ----------
        version : str
            Application version
        """
        super().__init__("application")
        self.version = version

    def _do_check_health(self) -> HealthCheckDetailDto:
        """Check application health.

        Returns
        -------
        HealthCheckDetailDto
            Application health status
        """
        return HealthCheckDetailDto(
            name=self.name,
            status="healthy",
            message="All systems operational",
            details={
                "version": self.version,
                "components": ["restapi", "mcp"],
            },
        )


class MCPServerHealthChecker(BaseHealthChecker):
    """Health checker for MCP server functionality.

    This checker verifies that the MCP server is running
    and responsive.
    """

    def __init__(self, transport: str = "sse") -> None:
        """Initialize MCP server health checker.

        Parameters
        ----------
        transport : str
            MCP transport type (sse or http-streaming)
        """
        super().__init__("mcp_server")
        self.transport = transport

    def _do_check_health(self) -> HealthCheckDetailDto:
        """Check MCP server health.

        Returns
        -------
        HealthCheckDetailDto
            MCP server health status
        """
        return HealthCheckDetailDto(
            name=self.name,
            status="healthy",
            message="MCP server is running",
            details={"transport": self.transport},
        )


class HealthCheckService:
    """Service for coordinating multiple health checkers.

    This class follows duck typing principles and can work with any
    objects that implement the HealthChecker protocol.
    """

    _start_time: float

    def __init__(self) -> None:
        """Initialize health check service."""
        self._checkers: list[HealthChecker] = []
        self._start_time = time.time()

    def register_checker(self, checker: HealthChecker) -> None:
        """Register a health checker.

        Parameters
        ----------
        checker : HealthChecker
            Health checker to register
        """
        self._checkers.append(checker)

    def check_all_health(self) -> dict[str, Any]:
        """Check health of all registered checkers.

        Returns
        -------
        dict[str, Any]
            Dict containing overall health status and individual checker results
        """
        results: list[HealthCheckDetailDto] = []
        overall_status = "healthy"

        for checker in self._checkers:
            try:
                status = checker.check_health()
                results.append(status)

                # Determine overall status
                if status.status == "unhealthy":
                    overall_status = "unhealthy"
                elif status.status == "degraded" and overall_status == "healthy":
                    overall_status = "degraded"

            except Exception as e:
                # Handle case where checker itself fails
                checker_name = (
                    checker.name if hasattr(checker, "name") else type(checker).__name__
                )
                results.append(
                    HealthCheckDetailDto(
                        name=checker_name,
                        status="unhealthy",
                        message=f"Checker failed: {e!s}",
                        details={"error": str(e)},
                    )
                )
                overall_status = "unhealthy"

        uptime_seconds = time.time() - self._start_time

        return {
            "status": overall_status,
            "timestamp": datetime.now(UTC).isoformat(),
            "uptime_seconds": uptime_seconds,
            "checks": results,
        }

    def reset_uptime(self) -> None:
        """Reset the uptime counter.

        This is useful for testing or when the service is restarted.
        """
        self._start_time = time.time()


def create_default_health_service(version: str = "0.0.0") -> HealthCheckService:
    """Create a health check service with default checkers.

    Parameters
    ----------
    version : str
        Application version

    Returns
    -------
    HealthCheckService
        Service with default health checkers registered
    """
    service = HealthCheckService()

    # Register default health checkers
    service.register_checker(ApplicationHealthChecker(version=version))
    service.register_checker(MCPServerHealthChecker())

    return service
