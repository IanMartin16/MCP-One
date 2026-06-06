from fastapi import HTTPException

from app.api.guards import (
    require_debug_routes_enabled,
    require_metrics_routes_enabled,
    require_recent_resolutions_enabled,
)
from app.config.settings import get_settings


def test_debug_routes_guard_enabled(monkeypatch):
    monkeypatch.setenv("ENABLE_DEBUG_ROUTES", "true")
    get_settings.cache_clear()

    require_debug_routes_enabled()

    get_settings.cache_clear()


def test_metrics_routes_guard_enabled(monkeypatch):
    monkeypatch.setenv("ENABLE_METRICS_ROUTES", "true")
    get_settings.cache_clear()

    require_metrics_routes_enabled()

    get_settings.cache_clear()


def test_recent_resolutions_guard_enabled(monkeypatch):
    monkeypatch.setenv("ENABLE_RECENT_RESOLUTIONS_ROUTE", "true")
    get_settings.cache_clear()

    require_recent_resolutions_enabled()

    get_settings.cache_clear()