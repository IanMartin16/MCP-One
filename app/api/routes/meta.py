from fastapi import APIRouter, Query, Request

from app.api.guards import (
    require_metrics_routes_enabled,
    require_recent_resolutions_enabled,
)
from app.metrics.recent_store import recent_resolution_store
from app.metrics.store import metrics_store
from app.utils.reason_codes import ReasonCodes

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/reason-codes")
def get_reason_codes():
    return {
        "reason_codes": [
            value
            for key, value in ReasonCodes.__dict__.items()
            if not key.startswith("_") and isinstance(value, str)
        ]
    }


@router.get("/metrics")
def get_metrics(request: Request):
    disabled = require_metrics_routes_enabled()
    if disabled is not None:
        return disabled
    return metrics_store.snapshot()


@router.get("/metrics/summary")
def get_metrics_summary(request: Request, limit: int = Query(default=5, ge=1, le=20)):
    disabled = require_metrics_routes_enabled()
    if disabled is not None:
        return disabled
    return metrics_store.summary(limit=limit)


@router.post("/metrics/reset")
def reset_metrics(request: Request):
    disabled = require_metrics_routes_enabled()
    if disabled is not None:
        return disabled
    metrics_store.reset()
    recent_resolution_store.reset()
    return {"ok": True}


@router.get("/recent-resolutions")
def get_recent_resolutions(request: Request, limit: int = Query(default=10, ge=1, le=50)):
    disabled = require_recent_resolutions_enabled()
    if disabled is not None:
        return disabled
    return {
        "items": recent_resolution_store.list(limit=limit)
    }