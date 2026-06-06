from __future__ import annotations

from app.config.settings import get_settings
from app.models.registry import CapabilityDef, ModuleDef


def should_handoff(module: ModuleDef, capability: CapabilityDef) -> bool:
    settings = get_settings()

    if not module.enabled:
        return settings.enable_handoff_for_disabled

    if module.status == "planned":
        return settings.enable_handoff_for_planned

    if capability.exposure == "handoff_only":
        return True

    return False