from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class ProviderRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.2
    max_tokens: int = 400
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderResponse(BaseModel):
    provider: str
    model: str
    content: str
    raw: dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None