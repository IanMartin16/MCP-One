# app/health/models.py

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


OperationalStatus = Literal[
    "operational",
    "degraded",
    "maintenance",
    "down",
    "unknown",
]

CheckStatus = Literal[
    "operational",
    "degraded",
    "down",
    "unknown",
]


class ServiceInfo(BaseModel):
    id: str
    name: str
    version: str
    environment: str
    stack: str


class HealthCheck(BaseModel):
    status: CheckStatus
    message: str | None = Field(default=None, description="Optional message providing additional context about the health check status.")


class HealthResponse(BaseModel):
    contract_version: Literal["health.v1"] = "health.v1"
    service: ServiceInfo
    status: OperationalStatus
    readiness: Literal["ready", "not_ready"]
    timestamp: datetime
    uptime_seconds: int = Field(ge=0)
    checks: dict[str, HealthCheck]


class LiveResponse(BaseModel):
    contract_version: Literal["health.v1"] = "health.v1"
    service_id: str
    status: Literal["alive"]
    timestamp: datetime


class ReadyResponse(BaseModel):
    contract_version: Literal["health.v1"] = "health.v1"
    service_id: str
    status: Literal["ready", "not_ready"]
    timestamp: datetime
    checks: dict[str, HealthCheck]