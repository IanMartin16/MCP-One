from fastapi import APIRouter

from app.config.settings import get_settings
from app.registry.loader import load_registry

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    settings = get_settings()
    registry = load_registry()

    modules_count = len(registry.modules)
    capabilities_count = len(registry.capabilities)
    rules_count = len(registry.intent_rules)

    ok = modules_count > 0 and capabilities_count > 0 and rules_count > 0

    return {
        "ok": ok,
        "status": "operational" if ok else "degraded",
        "service": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
        "active_provider": settings.active_provider,
        "registry_source": settings.registry_source,
        "registry_modules": modules_count,
        "registry_capabilities": capabilities_count,
        "registry_rules": rules_count,
    }