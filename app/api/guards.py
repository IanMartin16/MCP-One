from __future__ import annotations

from app.api.errors import build_error_response
from app.config.settings import get_settings
from app.utils.error_codes import ErrorCodes


def require_debug_routes_enabled():
    settings = get_settings()
    if not settings.enable_debug_routes:
        return build_error_response(
            status_code=404,
            code=ErrorCodes.ROUTE_DISABLED,
            message="The requested route is not available in this environment.",
            request_id=None,
            details={},
        )
    return None


def require_metrics_routes_enabled():
    settings = get_settings()
    if not settings.enable_metrics_routes:
        return build_error_response(
            status_code=404,
            code=ErrorCodes.ROUTE_DISABLED,
            message="The requested route is not available in this environment.",
            request_id=None,
            details={},
        )
    return None


def require_recent_resolutions_enabled():
    settings = get_settings()
    if not settings.enable_recent_resolutions_route:
        return build_error_response(
            status_code=404,
            code=ErrorCodes.ROUTE_DISABLED,
            message="The requested route is not available in this environment.",
            request_id=None,
            details={},
        )
    return None