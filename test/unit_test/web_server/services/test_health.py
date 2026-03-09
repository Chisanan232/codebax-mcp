"""Unit tests for health checking service.

This module contains comprehensive unit tests for the health checking
service and its components.
"""

from __future__ import annotations

from codebax_mcp.web_server.models.response.health_check import (
    HealthCheckDetailDto,
)
from codebax_mcp.web_server.services.health import (
    ApplicationHealthChecker,
    BaseHealthChecker,
    HealthCheckService,
    MCPServerHealthChecker,
    create_default_health_service,
)


class TestApplicationHealthChecker:
    """Tests for ApplicationHealthChecker."""

    def test_application_health_checker_healthy(self) -> None:
        """Test that application health checker returns healthy status."""
        checker = ApplicationHealthChecker(version="1.0.0")
        result = checker.check_health()

        assert result.name == "application"
        assert result.status == "healthy"
        assert result.message == "All systems operational"
        assert result.details is not None
        assert result.details["version"] == "1.0.0"
        assert "components" in result.details

    def test_application_health_checker_with_default_version(self) -> None:
        """Test application health checker with default version."""
        checker = ApplicationHealthChecker()
        result = checker.check_health()

        assert result.status == "healthy"
        assert result.details is not None
        assert result.details["version"] == "0.0.0"


class TestMCPServerHealthChecker:
    """Tests for MCPServerHealthChecker."""

    def test_mcp_server_health_checker_healthy(self) -> None:
        """Test that MCP server health checker returns healthy status."""
        checker = MCPServerHealthChecker(transport="sse")
        result = checker.check_health()

        assert result.name == "mcp_server"
        assert result.status == "healthy"
        assert result.message == "MCP server is running"
        assert result.details is not None
        assert result.details["transport"] == "sse"

    def test_mcp_server_health_checker_with_http_streaming(self) -> None:
        """Test MCP server health checker with http-streaming transport."""
        checker = MCPServerHealthChecker(transport="http-streaming")
        result = checker.check_health()

        assert result.status == "healthy"
        assert result.details is not None
        assert result.details["transport"] == "http-streaming"


class TestBaseHealthChecker:
    """Tests for BaseHealthChecker error handling."""

    def test_base_health_checker_handles_exceptions(self) -> None:
        """Test that base health checker handles exceptions gracefully."""

        class FailingHealthChecker(BaseHealthChecker):
            """Health checker that always fails."""

            def _do_check_health(self) -> HealthCheckDetailDto:
                """Raise an exception."""
                raise RuntimeError("Test error")

        checker = FailingHealthChecker("failing")
        result = checker.check_health()

        assert result.name == "failing"
        assert result.status == "unhealthy"
        assert "Test error" in result.message
        assert result.details is not None
        assert "error" in result.details


class TestHealthCheckService:
    """Tests for HealthCheckService."""

    def test_health_check_service_initialization(self) -> None:
        """Test that health check service initializes correctly."""
        service = HealthCheckService()
        assert service._checkers == []

    def test_register_checker(self) -> None:
        """Test registering a health checker."""
        service = HealthCheckService()
        checker = ApplicationHealthChecker()

        service.register_checker(checker)

        assert len(service._checkers) == 1
        assert service._checkers[0] == checker

    def test_check_all_health_with_single_healthy_checker(self) -> None:
        """Test health check with a single healthy checker."""
        service = HealthCheckService()
        service.register_checker(ApplicationHealthChecker())

        result = service.check_all_health()

        assert result["status"] == "healthy"
        assert "timestamp" in result
        assert "uptime_seconds" in result
        assert isinstance(result["checks"], list)
        assert len(result["checks"]) == 1
        assert result["checks"][0].status == "healthy"

    def test_check_all_health_with_multiple_checkers(self) -> None:
        """Test health check with multiple checkers."""
        service = HealthCheckService()
        service.register_checker(ApplicationHealthChecker())
        service.register_checker(MCPServerHealthChecker())

        result = service.check_all_health()

        assert result["status"] == "healthy"
        assert len(result["checks"]) == 2
        assert all(check.status == "healthy" for check in result["checks"])

    def test_check_all_health_with_unhealthy_checker(self) -> None:
        """Test health check when one checker is unhealthy."""

        class UnhealthyChecker(BaseHealthChecker):
            """Health checker that returns unhealthy status."""

            def _do_check_health(self) -> HealthCheckDetailDto:
                """Return unhealthy status."""
                return HealthCheckDetailDto(
                    name=self.name,
                    status="unhealthy",
                    message="Component is down",
                )

        service = HealthCheckService()
        service.register_checker(ApplicationHealthChecker())
        service.register_checker(UnhealthyChecker("database"))

        result = service.check_all_health()

        assert result["status"] == "unhealthy"
        assert len(result["checks"]) == 2

    def test_check_all_health_with_degraded_checker(self) -> None:
        """Test health check when one checker is degraded."""

        class DegradedChecker(BaseHealthChecker):
            """Health checker that returns degraded status."""

            def _do_check_health(self) -> HealthCheckDetailDto:
                """Return degraded status."""
                return HealthCheckDetailDto(
                    name=self.name,
                    status="degraded",
                    message="Component is degraded",
                )

        service = HealthCheckService()
        service.register_checker(ApplicationHealthChecker())
        service.register_checker(DegradedChecker("cache"))

        result = service.check_all_health()

        assert result["status"] == "degraded"
        assert len(result["checks"]) == 2

    def test_check_all_health_uptime_tracking(self) -> None:
        """Test that uptime is tracked correctly."""
        service = HealthCheckService()
        service.register_checker(ApplicationHealthChecker())

        result = service.check_all_health()

        assert result["uptime_seconds"] >= 0

    def test_reset_uptime(self) -> None:
        """Test resetting uptime counter."""
        service = HealthCheckService()
        service.register_checker(ApplicationHealthChecker())

        result1 = service.check_all_health()
        uptime1 = result1["uptime_seconds"]

        service.reset_uptime()

        result2 = service.check_all_health()
        uptime2 = result2["uptime_seconds"]

        assert uptime2 < uptime1

    def test_check_all_health_with_failing_checker(self) -> None:
        """Test health check when a checker raises an exception."""

        class FailingChecker(BaseHealthChecker):
            """Health checker that raises an exception."""

            def _do_check_health(self) -> HealthCheckDetailDto:
                """Raise an exception."""
                raise RuntimeError("Checker failed")

        service = HealthCheckService()
        service.register_checker(ApplicationHealthChecker())
        service.register_checker(FailingChecker("failing"))

        result = service.check_all_health()

        assert result["status"] == "unhealthy"
        assert len(result["checks"]) == 2
        assert result["checks"][1].status == "unhealthy"


class TestCreateDefaultHealthService:
    """Tests for create_default_health_service factory function."""

    def test_create_default_health_service(self) -> None:
        """Test creating default health service."""
        service = create_default_health_service()

        assert isinstance(service, HealthCheckService)
        assert len(service._checkers) == 2

    def test_create_default_health_service_with_version(self) -> None:
        """Test creating default health service with custom version."""
        service = create_default_health_service(version="2.0.0")

        result = service.check_all_health()

        assert result["status"] == "healthy"
        app_check = result["checks"][0]
        assert app_check.details is not None
        assert app_check.details["version"] == "2.0.0"

    def test_default_health_service_is_healthy(self) -> None:
        """Test that default health service returns healthy status."""
        service = create_default_health_service()

        result = service.check_all_health()

        assert result["status"] == "healthy"
        assert all(check.status == "healthy" for check in result["checks"])
