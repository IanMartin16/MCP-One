from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class ErrorPayload(BaseModel):
    code: str
    message: str
    request_id: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorEnvelope(BaseModel):
    error: ErrorPayload