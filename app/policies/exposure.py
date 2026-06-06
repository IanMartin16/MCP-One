from __future__ import annotations

from app.config.settings import get_settings
from app.models.registry import CapabilityDef, ModuleDef


def resolve_output_mode(module: ModuleDef, capability: CapabilityDef) -> str:
    settings = get_settings()

    if not module.enabled:
        return "handoff" if settings.enable_handoff_for_disabled else "summary"

    if module.status == "planned":
        if not settings.enable_preview_for_planned:
            return "handoff" if settings.enable_handoff_for_planned else "summary"

        if capability.exposure in {"handoff_only", "internal"}:
            return "handoff"

        return "preview"

    if module.status == "beta":
        if capability.exposure == "handoff_only":
            return "handoff"
        if capability.exposure in {"preview", "internal"}:
            return "preview"
        return "summary"

    if capability.exposure == "handoff_only":
        return "handoff"

    if capability.exposure in {"preview", "internal"}:
        return "preview"

    return "summary"