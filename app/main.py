from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.errors import build_error_response
from app.api.routes.health import router as health_router
from app.api.routes.meta import router as meta_router
from app.api.routes.orchestrate import router as orchestrate_router
from app.api.routes.providers import router as providers_router
from app.api.routes.registry import router as registry_router
from app.api.routes.health import router as health_router
from app.config.settings import get_settings
from app.utils.error_codes import ErrorCodes

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(health_router)
app.include_router(registry_router)
app.include_router(orchestrate_router)
app.include_router(meta_router)
app.include_router(providers_router)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    return build_error_response(
        status_code=422,
        code=ErrorCodes.VALIDATION_ERROR,
        message="The request payload failed validation.",
        request_id=None,
        details={},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return build_error_response(
            status_code=404,
            code=ErrorCodes.NOT_FOUND,
            message="The requested resource was not found.",
            request_id=None,
            details={},
        )

    return build_error_response(
        status_code=exc.status_code,
        code=ErrorCodes.INVALID_REQUEST,
        message=str(exc.detail) if exc.detail else "The request could not be processed.",
        request_id=None,
        details={},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return build_error_response(
        status_code=500,
        code=ErrorCodes.INTERNAL_ERROR,
        message="An unexpected internal error occurred.",
        request_id=None,
        details={},
    )