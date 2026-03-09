"""Unit tests for health service dependency injection.

This module contains tests for the health service dependency functions
used in FastAPI endpoints.
"""

from __future__ import annotations
from typing import Annotated

from fastapi import Depends, FastAPI

from codebax_mcp.web_server.dependencies.health import (
    get_health_service,
    reset_health_service,
)
from codebax_mcp.web_server.services.health import HealthCheckService


class TestGetHealthService:
    """Tests for get_health_service dependency function."""

    def setup_method(self) -> None:
        """Reset health service before each test."""
        reset_health_service()

    def test_get_health_service_returns_instance(self) -> None:
        """Test that get_health_service returns a HealthCheckService instance."""
        service = get_health_service()

        assert isinstance(service, HealthCheckService)

    def test_get_health_service_singleton(self) -> None:
        """Test that get_health_service returns the same instance."""
        service1 = get_health_service()
        service2 = get_health_service()

        assert service1 is service2

    def test_get_health_service_has_default_checkers(self) -> None:
        """Test that health service has default checkers registered."""
        service = get_health_service()

        result = service.check_all_health()

        assert result["status"] == "healthy"
        assert len(result["checks"]) >= 2

    def test_get_health_service_multiple_calls_same_instance(self) -> None:
        """Test that multiple calls return the same instance."""
        services = [get_health_service() for _ in range(5)]

        # All should be the same instance
        assert all(s is services[0] for s in services)


class TestResetHealthService:
    """Tests for reset_health_service function."""

    def test_reset_health_service_clears_instance(self) -> None:
        """Test that reset_health_service clears the cached instance."""
        service1 = get_health_service()
        reset_health_service()
        service2 = get_health_service()

        assert service1 is not service2

    def test_reset_health_service_allows_new_instance(self) -> None:
        """Test that reset allows creating a new service instance."""
        get_health_service()
        reset_health_service()

        # Should be able to get a new instance
        new_service = get_health_service()
        assert isinstance(new_service, HealthCheckService)

    def test_reset_health_service_multiple_times(self) -> None:
        """Test that reset can be called multiple times."""
        for _ in range(3):
            service = get_health_service()
            assert isinstance(service, HealthCheckService)
            reset_health_service()

    def test_reset_health_service_idempotent(self) -> None:
        """Test that reset is idempotent."""
        reset_health_service()
        reset_health_service()
        reset_health_service()

        # Should still be able to get a service
        service = get_health_service()
        assert isinstance(service, HealthCheckService)


class TestHealthServiceDependencyIntegration:
    """Integration tests for health service dependency."""

    def setup_method(self) -> None:
        """Reset health service before each test."""
        reset_health_service()

    def test_dependency_injection_in_fastapi(self) -> None:
        """Test that health service can be injected into FastAPI endpoints."""
        app = FastAPI()

        @app.get("/test-health")
        async def test_endpoint(
            service: Annotated[HealthCheckService, Depends(get_health_service)],
        ) -> dict:
            if service is None:
                service = get_health_service()
            result = service.check_all_health()
            return {"status": result["status"]}

        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/test-health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_dependency_injection_multiple_endpoints(self) -> None:
        """Test that health service is shared across multiple endpoints."""
        app = FastAPI()

        @app.get("/health1")
        async def endpoint1(
            service: Annotated[HealthCheckService, Depends(get_health_service)],
        ) -> dict:
            if service is None:
                service = get_health_service()
            return {"id": id(service)}

        @app.get("/health2")
        async def endpoint2(
            service: Annotated[HealthCheckService, Depends(get_health_service)],
        ) -> dict:
            if service is None:
                service = get_health_service()
            return {"id": id(service)}

        from fastapi.testclient import TestClient

        client = TestClient(app)
        response1 = client.get("/health1")
        response2 = client.get("/health2")

        # Should be the same instance
        assert response1.json()["id"] == response2.json()["id"]

    def test_health_service_state_persistence(self) -> None:
        """Test that health service state persists across calls."""
        service1 = get_health_service()
        result1 = service1.check_all_health()
        uptime1 = result1["uptime_seconds"]

        service2 = get_health_service()
        result2 = service2.check_all_health()
        uptime2 = result2["uptime_seconds"]

        # Uptime should increase (or stay same)
        assert uptime2 >= uptime1
