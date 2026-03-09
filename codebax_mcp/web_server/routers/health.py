"""Health check router for the MCP server.

This module provides FastAPI router endpoints for health checking
using Pythonic FastAPI decorators with dependency injection.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies.health import get_health_service
from ..models.response.health_check import (
    ComprehensiveHealthResponseDto,
    LivenessResponseDto,
    ReadinessResponseDto,
    SimpleHealthResponseDto,
)
from ..services.health import HealthCheckService

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    summary="Comprehensive health check",
    description="Check health of all system components",
    response_model=ComprehensiveHealthResponseDto,
    status_code=status.HTTP_200_OK,
)
async def comprehensive_health_check(
    service: HealthCheckService = Depends(get_health_service),
) -> ComprehensiveHealthResponseDto:
    """Perform comprehensive health check.

    This endpoint checks all registered health checkers
    and returns detailed status information.

    Parameters
    ----------
    service : HealthCheckService
        Health check service (injected via dependency injection)

    Returns
    -------
    ComprehensiveHealthResponseDto
        Detailed health status with component information

    Raises
    ------
    HTTPException
        If overall health status is unhealthy (503)

    """
    try:
        health_result = service.check_all_health()

        response = ComprehensiveHealthResponseDto(
            status=health_result["status"],
            timestamp=health_result["timestamp"],
            version="0.0.0",
            uptime_seconds=health_result["uptime_seconds"],
            checks=health_result["checks"],
        )

        # Return 503 if unhealthy
        if health_result["status"] == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=response.model_dump(),
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "timestamp": "",
                "version": "0.0.0",
                "uptime_seconds": 0.0,
                "checks": [
                    {
                        "name": "health_check",
                        "status": "unhealthy",
                        "message": f"Health check failed: {e!s}",
                        "details": {"error": str(e)},
                    }
                ],
            },
        ) from e


@router.get(
    "/simple",
    summary="Simple health check",
    description="Basic health check for load balancers",
    response_model=SimpleHealthResponseDto,
    status_code=status.HTTP_200_OK,
)
async def simple_health_check(
    service: HealthCheckService = Depends(get_health_service),
) -> SimpleHealthResponseDto:
    """Perform simple health check.

    This endpoint provides a minimal health check suitable
    for load balancers and monitoring systems.

    Parameters
    ----------
    service : HealthCheckService
        Health check service (injected via dependency injection)

    Returns
    -------
    SimpleHealthResponseDto
        Simple health status

    Raises
    ------
    HTTPException
        If health check fails (503)

    """
    try:
        result = service.check_all_health()

        if result["status"] == "healthy":
            return SimpleHealthResponseDto(status="ok")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error"},
        ) from e


@router.get(
    "/ready",
    summary="Readiness check",
    description="Check if application is ready to serve traffic",
    response_model=ReadinessResponseDto,
    status_code=status.HTTP_200_OK,
)
async def readiness_check(
    service: HealthCheckService = Depends(get_health_service),
) -> ReadinessResponseDto:
    """Check if application is ready to serve traffic.

    This endpoint checks if all critical components are ready
    to accept requests. It's used by Kubernetes and other
    orchestration systems.

    Parameters
    ----------
    service : HealthCheckService
        Health check service (injected via dependency injection)

    Returns
    -------
    ReadinessResponseDto
        Readiness status

    Raises
    ------
    HTTPException
        If application is not ready (503)

    """
    try:
        health_result = service.check_all_health()

        # Consider application ready if not unhealthy
        if health_result["status"] != "unhealthy":
            return ReadinessResponseDto(
                ready=True,
                message="Application is ready to serve traffic",
            )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "ready": False,
                "message": "Application is not ready - some components are unhealthy",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "ready": False,
                "message": f"Readiness check failed: {e!s}",
            },
        ) from e


@router.get(
    "/live",
    summary="Liveness check",
    description="Check if application is alive and responsive",
    response_model=LivenessResponseDto,
    status_code=status.HTTP_200_OK,
)
async def liveness_check() -> LivenessResponseDto:
    """Check if application is alive.

    This endpoint provides a basic liveness check to determine
    if the application process is running and responsive.

    Returns
    -------
    LivenessResponseDto
        Liveness status

    """
    return LivenessResponseDto(alive=True)


def get_health_router() -> APIRouter:
    """Get the health router instance.

    This function returns the global router instance for consistency
    with other routers in the application.

    Returns
    -------
    APIRouter
        Health check router instance

    """
    return router
