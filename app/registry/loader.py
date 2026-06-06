from __future__ import annotations

from functools import lru_cache

from app.config.settings import get_settings
from app.models.registry import RegistryDef
from app.registry.data import REGISTRY


def _load_local_registry() -> RegistryDef:
    return REGISTRY


@lru_cache
def load_registry() -> RegistryDef:
    settings = get_settings()

    if settings.registry_source == "local":
        return _load_local_registry()

    raise ValueError(f"Unsupported registry_source: {settings.registry_source}")