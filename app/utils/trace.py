from __future__ import annotations

import uuid


def generate_request_id() -> str:
    return f"mcp-{uuid.uuid4().hex[:12]}"