from __future__ import annotations

from typing import Optional, Any
from pydantic import BaseModel, Field

from app.models.execution import ExecutionContext
from app.models.plan import OrchestrationPlan


class ResolutionResult(BaseModel):
    request_id: Optional[str] = None
    status: str | None = None
    client_context: dict[str, Any] = Field(default_factory=dict)
    execution_context: ExecutionContext | None = None

    intent_family: Optional[str] = None
    rule_id: Optional[str] = None

    matched_patterns: list[str] = Field(default_factory=list)

    candidate_modules: list[str] = Field(default_factory=list)
    candidate_capabilities: list[str] = Field(default_factory=list)

    selected_modules: list[str] = Field(default_factory=list)
    selected_capabilities: list[str] = Field(default_factory=list)

    recommended_module: Optional[str] = None
    mode: str = "summary"

    should_compose: bool = False
    handoff: bool = False

    restrictions: list[str] = Field(default_factory=list)
    confidence: float = 0.0

    reason_codes: list[str] = Field(default_factory=list)
    reasoning_notes: list[str] = Field(default_factory=list)


    plan: Optional[OrchestrationPlan] = None