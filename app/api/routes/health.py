# app/api/routes/health.py

from datetime import datetime, timezone

from fastapi import APIRouter, Response, status

from app.config.settings import get_settings
from app.health.evaluator import evaluate_health
from app.health.models import (
    HealthCheck,
    HealthResponse,
    LiveResponse,
    ReadyResponse,
    ServiceInfo,
)
from app.health.runtime import uptime_seconds
from app.registry.loader import load_registry


router = APIRouter(tags=["health"])


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def registry_check(registry_ready: bool) -> HealthCheck:
    if registry_ready:
        return HealthCheck(status="operational")

    return HealthCheck(
        status="degraded",
        message="Registry is not ready",
    )


@router.get("/health")
def legacy_health():
    """
    Contrato temporal consumido actualmente por Status-hub.
    Conservamos exactamente su estructura.
    """
    settings = get_settings()
    registry = load_registry()

    modules_count = len(registry.modules)
    capabilities_count = len(registry.capabilities)
    rules_count = len(registry.intent_rules)

    ok = (
        modules_count > 0
        and capabilities_count > 0
        and rules_count > 0
    )

    return {
        "ok": ok,
        "status": "operational" if ok else "degraded",
        "service": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
        "active_provider": settings.active_provider,
        "registry_source": settings.registry_source,
        "registry_modules": modules_count,
        "registry_capabilities": capabilities_count,
        "registry_rules": rules_count,
    }


@router.get(
    "/api/health",
    response_model=HealthResponse,
)
def health_v1() -> HealthResponse:
    settings = get_settings()
    evaluation = evaluate_health()

    return HealthResponse(
        service=ServiceInfo(
            id="mcpone",
            name=settings.app_name,
            version=settings.app_version,
            environment=settings.app_env,
            stack="fastapi",
        ),
        status=evaluation.operational_status,
        readiness=evaluation.readiness_status,
        timestamp=utc_now(),
        uptime_seconds=uptime_seconds(),
        checks={
            "application": HealthCheck(
                status="operational",
            ),
            "configuration": HealthCheck(
                status="operational",
            ),
            "provider_registry": registry_check(
                evaluation.registry_ready,
            ),
        },
    )


@router.get(
    "/api/health/live",
    response_model=LiveResponse,
)
def live() -> LiveResponse:
    return LiveResponse(
        service_id="mcpone",
        status="alive",
        timestamp=utc_now(),
    )


@router.get(
    "/api/health/ready",
    response_model=ReadyResponse,
)
def ready(response: Response) -> ReadyResponse:
    evaluation = evaluate_health()

    response.status_code = (
        status.HTTP_200_OK
        if evaluation.ready
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return ReadyResponse(
        service_id="mcpone",
        status=evaluation.readiness_status,
        timestamp=utc_now(),
        checks={
            "configuration": HealthCheck(
                status="operational",
            ),
            "registry": registry_check(
                evaluation.registry_ready,
            ),
        },
    )