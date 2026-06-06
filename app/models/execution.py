from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class ExecutionContext(BaseModel):
    request_id: str
    client_context: dict[str, Any] = Field(default_factory=dict)

    app_env: str = "local"
    active_provider: str = "none"

    enable_composition: bool = True
    enable_provider_enrichment: bool = False
    enable_structured_logging: bool = True

    started_at: Optional[str] = None
    duration_ms: Optional[float] = None