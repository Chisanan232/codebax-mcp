"""Health service dependency for FastAPI endpoints.

This module provides dependency injection functions for health-related
endpoints following FastAPI's dependency injection pattern.
"""

from __future__ import annotations

from ..services.health import HealthCheckService, create_default_health_service

_health_service_instance: HealthCheckService | None = None


def get_health_service() -> HealthCheckService:
    """Dependency function to get health service instance.

    This follows FastAPI's dependency injection pattern and provides
    a clean way to inject the health service into endpoints.

    Returns
    -------
    HealthCheckService
        Health check service instance

    """
    global _health_service_instance
    if _health_service_instance is None:
        _health_service_instance = create_default_health_service()
    return _health_service_instance


def reset_health_service() -> None:
    """Reset the health service instance.

    This is primarily used for testing to ensure a fresh service
    instance for each test.
    """
    global _health_service_instance
    _health_service_instance = None
