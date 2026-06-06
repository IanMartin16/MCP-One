from fastapi import APIRouter

from app.registry.loader import load_registry

router = APIRouter(prefix="/registry", tags=["registry"])


@router.get("/modules")
def get_modules():
    return load_registry().modules


@router.get("/capabilities")
def get_capabilities():
    return load_registry().capabilities


@router.get("/rules")
def get_rules():
    return load_registry().intent_rules

@router.get("/meta")
def get_registry_meta():
    registry = load_registry()

    return {
        "modules_count": len(registry.modules),
        "capabilities_count": len(registry.capabilities),
        "rules_count": len(registry.intent_rules),
    }