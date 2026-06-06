from __future__ import annotations

from typing import Any


ALLOWED_CLIENT_CONTEXT_KEYS = {
    "source",
    "channel",
    "tenant",
    "session_id",
    "user_role",
}


def sanitize_client_context(raw_context: dict[str, Any]) -> dict[str, Any]:
    if not raw_context:
        return {}

    sanitized: dict[str, Any] = {}

    for key, value in raw_context.items():
        if key not in ALLOWED_CLIENT_CONTEXT_KEYS:
            continue

        if value is None:
            continue

        if isinstance(value, (str, int, float, bool)):
            sanitized[key] = value
        else:
            sanitized[key] = str(value)

    return sanitized