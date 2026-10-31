from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from structlog import get_logger

from app.core.exceptions.base import AppException
from app.core.exceptions.rate_limit import RateLimitExceededError

logger = get_logger(__name__)


def app_error_response(exc: AppException) -> JSONResponse:
    """Standard error response, also used by middleware where app-level
    exception handlers cannot run."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


def _safe_serialize_value(value):
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    if isinstance(value, (list, tuple)):
        return [_safe_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _safe_serialize_value(v) for k, v in value.items()}
    return str(value)


def _sanitize_validation_errors(errors: list[dict]) -> list[dict]:
    sanitized = []
    for error in errors:
        safe_error = dict(error)
        if "ctx" in safe_error and isinstance(safe_error["ctx"], dict):
            safe_ctx = {}
            for k, v in safe_error["ctx"].items():
                safe_ctx[k] = _safe_serialize_value(v)
            safe_error["ctx"] = safe_ctx
        if "input" in safe_error:
            safe_error["input"] = _safe_serialize_value(safe_error["input"])
        sanitized.append(safe_error)
    return sanitized


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(
            "app_exception",
            error_code=exc.error_code,
            status_code=exc.status_code,
            message=exc.message,
            path=request.url.path,
        )
        return app_error_response(exc)

    @app.exception_handler(RateLimitExceededError)
    async def rate_limit_exception_handler(
        request: Request, exc: RateLimitExceededError
    ):
        headers = {}
        if exc.retry_after:
            headers["Retry-After"] = str(exc.retry_after)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
            headers=headers,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "details": {},
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        sanitized_errors = _sanitize_validation_errors(exc.errors())
        logger.warning(
            "validation_error",
            path=request.url.path,
            errors=sanitized_errors,
        )
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request parameters.",
                    "details": sanitized_errors,
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled_exception", path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred.",
                    "details": {},
                },
            },
        )