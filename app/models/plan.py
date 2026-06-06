from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field


PlanStrategy = Literal["single_module", "composed", "handoff", "fallback"]


class PlanStep(BaseModel):
    step_id: str
    module_id: str
    capability_id: Optional[str] = None
    role: str = "primary"
    optional: bool = False
    reason: Optional[str] = None


class OrchestrationPlan(BaseModel):
    strategy: PlanStrategy
    primary_module: Optional[str] = None
    primary_capability: Optional[str] = None

    secondary_modules: list[str] = Field(default_factory=list)
    secondary_capabilities: list[str] = Field(default_factory=list)

    steps: list[PlanStep] = Field(default_factory=list)

    requires_handoff: bool = False
    preview_only: bool = False
    notes: list[str] = Field(default_factory=list)