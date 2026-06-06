from __future__ import annotations

from typing import Literal, Optional, Any
from pydantic import BaseModel, Field

ResponseMode = Literal[
    "module_recommendation",
    "capability_explanation",
    "summary",
    "composed_summary",
    "handoff",
    "preview",
]

class NextStep(BaseModel):
    type: str
    module: Optional[str] = None
    reason: Optional[str] = None

class OrchestrationOutput(BaseModel):
    request_id: Optional[str] = None
    status: str | None = None

    mode: ResponseMode
    modules_used: list[str] = Field(default_factory=list)
    capabilities_used: list[str] = Field(default_factory=list)

    summary: str
    insight: Optional[str] = None
    recommended_module: Optional[str] = None
    next_step: Optional[NextStep] = None

    handoff: bool = False
    restrictions: list[str] = Field(default_factory=list)
    confidence: float = 0.0

    matched_patterns: list[str] = Field(default_factory=list)
    reason_codes: list[str] = Field(default_factory=list)

     # nuevos campos user-facing
    product_name: str | None = None
    capability_name: str | None = None
    discovery_mode: str | None = None
    user_facing_title: str | None = None
    user_facing_summary: str | None = None
    user_facing_context: str | None = None
    next_step_hint: str | None = None
    offer_help: str | None = None
