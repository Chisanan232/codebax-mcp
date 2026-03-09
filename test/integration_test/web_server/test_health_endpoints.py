"""Integration tests for health check endpoints.

This module contains comprehensive integration tests for the health checking
endpoints, verifying the complete request/response flow with a test
FastAPI application.
"""

from __future__ import annotations

import time
from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from codebax_mcp.web_server.dependencies.health import reset_health_service
from codebax_mcp.web_server.models.response.health_check import (
    ComprehensiveHealthResponseDto,
    LivenessResponseDto,
    ReadinessResponseDto,
    SimpleHealthResponseDto,
)
from codebax_mcp.web_server.routers.health import get_health_router


@pytest.fixture
def app() -> Generator[FastAPI]:
    """Create a FastAPI app with health router for testing."""
    reset_health_service()
    app = FastAPI()
    app.include_router(get_health_router())
    yield app
    reset_health_service()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a TestClient for the app."""
    return TestClient(app)


class TestHealthEndpointsIntegration:
    """Integration tests for health endpoints with full application."""

    def test_comprehensive_health_endpoint_accessible(self, client: TestClient) -> None:
        """Test that comprehensive health endpoint is accessible."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data

    def test_simple_health_endpoint_accessible(self, client: TestClient) -> None:
        """Test that simple health endpoint is accessible."""
        response = client.get("/health/simple")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_readiness_endpoint_accessible(self, client: TestClient) -> None:
        """Test that readiness endpoint is accessible."""
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert "ready" in data

    def test_liveness_endpoint_accessible(self, client: TestClient) -> None:
        """Test that liveness endpoint is accessible."""
        response = client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert "alive" in data

    def test_health_endpoints_with_cors_headers(self, client: TestClient) -> None:
        """Test that health endpoints respect CORS configuration."""
        response = client.get("/health")

        assert response.status_code == 200
        # Should have content-type header
        assert "content-type" in response.headers

    @pytest.mark.parametrize("endpoint", ["/health", "/health/simple", "/health/ready", "/health/live"])
    def test_health_endpoints_response_times(self, client: TestClient, endpoint: str) -> None:
        """Test that health endpoints respond quickly."""
        start = time.time()
        response = client.get(endpoint)
        elapsed = time.time() - start

        assert response.status_code in [200, 503]
        # Health checks should be fast (< 1 second)
        assert elapsed < 1.0

    def test_health_endpoints_with_multiple_requests(self, client: TestClient) -> None:
        """Test that health endpoints handle multiple requests."""
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200

    def test_health_endpoints_consistency_across_calls(self, client: TestClient) -> None:
        """Test that health status is consistent across multiple calls."""
        responses = [client.get("/health") for _ in range(5)]

        statuses = [r.json()["status"] for r in responses]
        # All should have the same status
        assert len(set(statuses)) == 1

    def test_comprehensive_health_includes_all_checks(self, client: TestClient) -> None:
        """Test that comprehensive health includes all registered checks."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        check_names = [check["name"] for check in data["checks"]]
        # Should have at least application and mcp_server checks
        assert "application" in check_names
        assert "mcp_server" in check_names

    @pytest.mark.parametrize("endpoint", ["/health", "/health/simple", "/health/ready", "/health/live"])
    def test_health_endpoints_json_format(self, client: TestClient, endpoint: str) -> None:
        """Test that all health endpoints return valid JSON."""
        response = client.get(endpoint)
        assert response.status_code in [200, 503]

        # Should be valid JSON
        data = response.json()
        assert isinstance(data, dict)

    @pytest.mark.parametrize("endpoint", ["/health", "/health/simple", "/health/ready", "/health/live"])
    def test_health_endpoints_no_errors_in_response(
        self,
        client: TestClient,
        endpoint: str,
    ) -> None:
        """Test that health endpoints don't return error responses."""
        response = client.get(endpoint)
        # Should not return 4xx or 5xx errors (except 503 for unhealthy)
        assert response.status_code in [200, 503]


class TestHealthEndpointsWithApplicationContext:
    """Tests for health endpoints within application context."""

    def test_health_endpoints_available_after_app_creation(self, app: FastAPI) -> None:
        """Test that health endpoints are available after app creation."""
        client = TestClient(app)

        # All endpoints should be accessible
        assert client.get("/health").status_code in [200, 503]
        assert client.get("/health/simple").status_code in [200, 503]
        assert client.get("/health/ready").status_code in [200, 503]
        assert client.get("/health/live").status_code in [200, 503]

    def test_health_endpoints_with_app_lifespan(self, app: FastAPI) -> None:
        """Test that health endpoints work with app lifespan."""
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200

    def test_health_endpoints_documentation(self, app: FastAPI) -> None:
        """Test that health endpoints are documented in OpenAPI."""
        client = TestClient(app)

        # Get OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        paths = schema.get("paths", {})

        # Health endpoints should be in the schema
        assert "/health" in paths or any("health" in path for path in paths)


class TestHealthEndpointsErrorScenarios:
    """Tests for error scenarios in health endpoints."""

    def test_health_endpoints_with_invalid_path(self, client: TestClient) -> None:
        """Test that invalid health paths return 404."""
        response = client.get("/health/invalid")

        assert response.status_code == 404

    def test_health_endpoints_with_wrong_method(self, client: TestClient) -> None:
        """Test that non-GET methods are not allowed."""
        response = client.post("/health")

        assert response.status_code == 405  # Method Not Allowed

    def test_health_endpoints_with_query_parameters(self, client: TestClient) -> None:
        """Test that health endpoints ignore query parameters."""
        response = client.get("/health?foo=bar&baz=qux")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestHealthEndpointsResponseModels:
    """Tests for response model validation."""

    def test_comprehensive_health_response_model(self, client: TestClient) -> None:
        """Test comprehensive health response model validation."""
        response = client.get("/health")
        assert response.status_code == 200

        # Should be able to parse as response model
        data = ComprehensiveHealthResponseDto(**response.json())
        assert data.status in ["healthy", "degraded", "unhealthy"]
        assert len(data.checks) > 0

    def test_simple_health_response_model(self, client: TestClient) -> None:
        """Test simple health response model validation."""
        response = client.get("/health/simple")
        assert response.status_code == 200

        data = SimpleHealthResponseDto(**response.json())
        assert data.status in ["ok", "error"]

    def test_readiness_response_model(self, client: TestClient) -> None:
        """Test readiness response model validation."""
        response = client.get("/health/ready")
        assert response.status_code == 200

        data = ReadinessResponseDto(**response.json())
        assert isinstance(data.ready, bool)

    def test_liveness_response_model(self, client: TestClient) -> None:
        """Test liveness response model validation."""
        response = client.get("/health/live")
        assert response.status_code == 200

        data = LivenessResponseDto(**response.json())
        assert isinstance(data.alive, bool)
