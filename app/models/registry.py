from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field


ModuleStatus = Literal["active", "beta", "planned", "disabled"]
CapabilityExposure = Literal["public", "preview", "internal", "handoff_only"]
IntentPriority = Literal["low", "medium", "high", "critical"]


class ModuleDef(BaseModel):
    module_id: str = Field(..., description="Unique module identifier")
    name: str = Field(..., description="Human readable module name")
    description: str = Field(..., description="Short module description")
    status: ModuleStatus = Field(..., description="Lifecycle status")
    version: str = Field(default="v0")
    owner: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    input_modes: list[str] = Field(default_factory=list)
    output_modes: list[str] = Field(default_factory=list)
    supports_handoff: bool = Field(default=False)
    enabled: bool = Field(default=True)


class CapabilityDef(BaseModel):
    capability_id: str = Field(..., description="Unique capability identifier")
    module_id: str = Field(..., description="Owning module identifier")
    name: str = Field(..., description="Human readable capability name")
    description: str = Field(..., description="Short capability description")
    exposure: CapabilityExposure = Field(default="public")
    enabled: bool = Field(default=True)
    tags: list[str] = Field(default_factory=list)
    intent_families: list[str] = Field(default_factory=list)
    output_modes: list[str] = Field(default_factory=list)
    restrictions: list[str] = Field(default_factory=list)
    execution_endpoint: str | None = None   # método de CryptoLinkClient, p.ej. "get_momentum"
    output_kind: str | None = None          # kind neutral emitido, p.ej. "momentum"
    disambiguation_hints: list[str] | None = None  # pistas para el enganche cuando


class IntentRule(BaseModel):
    rule_id: str = Field(..., description="Unique rule identifier")
    intent_family: str = Field(..., description="Intent family name")
    description: str = Field(..., description="Rule description")
    priority: IntentPriority = Field(default="medium")
    enabled: bool = Field(default=True)

    patterns: list[str] = Field(
        default_factory=list,
        description="Simple keyword/pattern triggers"
    )

    preferred_modules: list[str] = Field(
        default_factory=list,
        description="Modules preferred for this intent"
    )

    preferred_capabilities: list[str] = Field(
        default_factory=list,
        description="Capabilities preferred for this intent"
    )

    allow_composition: bool = Field(default=False)
    handoff_if_unavailable: bool = Field(default=True)
    preview_if_planned: bool = Field(default=True)
    notes: list[str] = Field(default_factory=list)


class RegistryDef(BaseModel):
    modules: list[ModuleDef] = Field(default_factory=list)
    capabilities: list[CapabilityDef] = Field(default_factory=list)
    intent_rules: list[IntentRule] = Field(default_factory=list)