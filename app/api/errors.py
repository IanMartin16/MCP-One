from __future__ import annotations

from typing import Any, Optional

from fastapi.responses import JSONResponse

from app.models.errors import ErrorEnvelope, ErrorPayload


def build_error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    request_id: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
) -> JSONResponse:
    payload = ErrorEnvelope(
        error=ErrorPayload(
            code=code,
            message=message,
            request_id=request_id,
            details=details or {},
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(),
    )