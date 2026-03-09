"""Unit tests for health check router endpoints.

This module contains unit tests for the health check router,
verifying endpoint behavior and response structures.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from codebax_mcp.web_server.dependencies.health import reset_health_service
from codebax_mcp.web_server.models.response.health_check import (
    HealthCheckDetailDto,
)
from codebax_mcp.web_server.routers.health import get_health_router
from codebax_mcp.web_server.services.health import (
    BaseHealthChecker,
    HealthCheckService,
)


@pytest.fixture
def app() -> FastAPI:
    """Create a FastAPI app with health router for testing."""
    app = FastAPI()
    app.include_router(get_health_router())
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a TestClient for the app."""
    reset_health_service()
    return TestClient(app)


class TestComprehensiveHealthEndpoint:
    """Tests for the comprehensive health check endpoint."""

    def test_comprehensive_health_check_healthy(self, client: TestClient) -> None:
        """Test comprehensive health check returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "checks" in data
        assert isinstance(data["checks"], list)
        assert len(data["checks"]) > 0

    def test_comprehensive_health_check_response_structure(self, client: TestClient) -> None:
        """Test comprehensive health check response structure."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "timestamp" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], (int, float))
        assert "checks" in data
        assert isinstance(data["checks"], list)

        # Verify check structure
        for check in data["checks"]:
            assert "name" in check
            assert "status" in check
            assert check["status"] in ["healthy", "degraded", "unhealthy"]
            assert "message" in check or check["message"] is None
            assert "details" in check or check["details"] is None

    def test_comprehensive_health_check_contains_application_check(self, client: TestClient) -> None:
        """Test that comprehensive health check includes application check."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        check_names = [check["name"] for check in data["checks"]]
        assert "application" in check_names

    def test_comprehensive_health_check_contains_mcp_check(self, client: TestClient) -> None:
        """Test that comprehensive health check includes MCP server check."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        check_names = [check["name"] for check in data["checks"]]
        assert "mcp_server" in check_names

    def test_comprehensive_health_check_unhealthy_returns_503(self, app: FastAPI) -> None:
        """Test that unhealthy status returns 503 status code."""
        # Create a custom app with an unhealthy checker
        reset_health_service()
        app = FastAPI()

        # Add a custom dependency that returns unhealthy service
        from codebax_mcp.web_server.dependencies.health import get_health_service

        class UnhealthyChecker(BaseHealthChecker):
            def _do_check_health(self) -> HealthCheckDetailDto:
                return HealthCheckDetailDto(
                    name=self.name,
                    status="unhealthy",
                    message="Service is down",
                )

        def get_unhealthy_service() -> HealthCheckService:
            service = HealthCheckService()
            service.register_checker(UnhealthyChecker("test"))
            return service

        # Override the dependency
        app.dependency_overrides[get_health_service] = get_unhealthy_service
        app.include_router(get_health_router())

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["detail"]["status"] == "unhealthy"


class TestSimpleHealthEndpoint:
    """Tests for the simple health check endpoint."""

    def test_simple_health_check_returns_ok(self, client: TestClient) -> None:
        """Test simple health check returns ok status."""
        response = client.get("/health/simple")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_simple_health_check_response_structure(self, client: TestClient) -> None:
        """Test simple health check response structure."""
        response = client.get("/health/simple")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ok", "error"]

    def test_simple_health_check_minimal_response(self, client: TestClient) -> None:
        """Test that simple health check returns minimal response."""
        response = client.get("/health/simple")

        assert response.status_code == 200
        data = response.json()
        # Should only contain status field
        assert len(data) == 1
        assert "status" in data


class TestReadinessEndpoint:
    """Tests for the readiness check endpoint."""

    def test_readiness_check_returns_ready(self, client: TestClient) -> None:
        """Test readiness check returns ready status."""
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert "message" in data

    def test_readiness_check_response_structure(self, client: TestClient) -> None:
        """Test readiness check response structure."""
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
        assert isinstance(data["ready"], bool)
        assert "message" in data

    def test_readiness_check_message_content(self, client: TestClient) -> None:
        """Test readiness check message content."""
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert "ready" in data["message"].lower() or "traffic" in data["message"].lower()


class TestLivenessEndpoint:
    """Tests for the liveness check endpoint."""

    def test_liveness_check_returns_alive(self, client: TestClient) -> None:
        """Test liveness check returns alive status."""
        response = client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True

    def test_liveness_check_response_structure(self, client: TestClient) -> None:
        """Test liveness check response structure."""
        response = client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert "alive" in data
        assert isinstance(data["alive"], bool)

    def test_liveness_check_always_succeeds(self, client: TestClient) -> None:
        """Test that liveness check always succeeds."""
        # Liveness check should always return 200 and alive=true
        for _ in range(5):
            response = client.get("/health/live")
            assert response.status_code == 200
            assert response.json()["alive"] is True


class TestHealthEndpointIntegration:
    """Integration tests for multiple health endpoints."""

    def test_all_health_endpoints_accessible(self, client: TestClient) -> None:
        """Test that all health endpoints are accessible."""
        endpoints = ["/health", "/health/simple", "/health/ready", "/health/live"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 503], f"Endpoint {endpoint} failed"

    def test_health_endpoints_return_json(self, client: TestClient) -> None:
        """Test that all health endpoints return JSON."""
        endpoints = ["/health", "/health/simple", "/health/ready", "/health/live"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.headers["content-type"] == "application/json"

    def test_comprehensive_vs_simple_health_consistency(self, client: TestClient) -> None:
        """Test consistency between comprehensive and simple health checks."""
        comprehensive = client.get("/health").json()
        simple = client.get("/health/simple").json()

        # If comprehensive is healthy, simple should be ok
        if comprehensive["status"] == "healthy":
            assert simple["status"] == "ok"

    def test_readiness_vs_comprehensive_health_consistency(self, client: TestClient) -> None:
        """Test consistency between readiness and comprehensive health checks."""
        comprehensive = client.get("/health").json()
        readiness = client.get("/health/ready").json()

        # If comprehensive is not unhealthy, readiness should be ready
        if comprehensive["status"] != "unhealthy":
            assert readiness["ready"] is True

    def test_liveness_independent_of_other_checks(self, client: TestClient) -> None:
        """Test that liveness check is independent of other checks."""
        # Liveness should always return alive=true regardless of other checks
        liveness = client.get("/health/live").json()
        assert liveness["alive"] is True


class TestHealthEndpointErrorHandling:
    """Tests for error handling in health endpoints."""

    def test_comprehensive_health_handles_missing_service(self, app: FastAPI) -> None:
        """Test comprehensive health endpoint handles missing service gracefully."""
        reset_health_service()
        app = FastAPI()
        app.include_router(get_health_router())
        client = TestClient(app)

        response = client.get("/health")
        # Should still return a response (200 or 503)
        assert response.status_code in [200, 503]

    def test_health_endpoints_handle_concurrent_requests(self, client: TestClient) -> None:
        """Test that health endpoints handle concurrent requests."""
        # Simulate multiple concurrent requests
        responses = [client.get("/health") for _ in range(10)]

        # All should succeed
        assert all(r.status_code in [200, 503] for r in responses)
        # All should have same overall status
        statuses = [r.json()["status"] for r in responses]
        assert len(set(statuses)) == 1


class TestHealthEndpointResponseValidation:
    """Tests for response validation."""

    def test_comprehensive_health_response_validates(self, client: TestClient) -> None:
        """Test that comprehensive health response validates against schema."""
        from codebax_mcp.web_server.models.response.health_check import (
            ComprehensiveHealthResponseDto,
        )

        response = client.get("/health")
        assert response.status_code == 200

        # Should be able to parse as ComprehensiveHealthResponseDto
        data = ComprehensiveHealthResponseDto(**response.json())
        assert data.status in ["healthy", "degraded", "unhealthy"]

    def test_simple_health_response_validates(self, client: TestClient) -> None:
        """Test that simple health response validates against schema."""
        from codebax_mcp.web_server.models.response.health_check import (
            SimpleHealthResponseDto,
        )

        response = client.get("/health/simple")
        assert response.status_code == 200

        data = SimpleHealthResponseDto(**response.json())
        assert data.status in ["ok", "error"]

    def test_readiness_response_validates(self, client: TestClient) -> None:
        """Test that readiness response validates against schema."""
        from codebax_mcp.web_server.models.response.health_check import (
            ReadinessResponseDto,
        )

        response = client.get("/health/ready")
        assert response.status_code == 200

        data = ReadinessResponseDto(**response.json())
        assert isinstance(data.ready, bool)

    def test_liveness_response_validates(self, client: TestClient) -> None:
        """Test that liveness response validates against schema."""
        from codebax_mcp.web_server.models.response.health_check import (
            LivenessResponseDto,
        )

        response = client.get("/health/live")
        assert response.status_code == 200

        data = LivenessResponseDto(**response.json())
        assert isinstance(data.alive, bool)
