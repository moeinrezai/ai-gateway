from typing import ClassVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config.settings import settings
from app.core.exceptions.auth import PermissionDeniedError
from app.core.exceptions.handlers import app_error_response
from app.core.security.csrf import validate_csrf_token


class CSRFMiddleware(BaseHTTPMiddleware):
    SAFE_METHODS: ClassVar[set[str]] = {"GET", "HEAD", "OPTIONS", "TRACE"}
    EXEMPT_PATHS: ClassVar[set[str]] = {
        f"{settings.APP_API_V1_PREFIX}/auth/login",
        f"{settings.APP_API_V1_PREFIX}/auth/register",
    }

    # Requests without authentication cookies carry no credentials, so there
    # is no cross-site request to forge; validation only protects
    # cookie-authenticated requests.
    AUTH_COOKIE_NAMES = ("access_token", "refresh_token")

    async def dispatch(self, request: Request, call_next) -> Response:
        if not settings.CSRF_ENABLED:
            return await call_next(request)

        if request.method in self.SAFE_METHODS:
            return await call_next(request)

        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        if not any(
            name in request.cookies for name in self.AUTH_COOKIE_NAMES
        ):
            return await call_next(request)

        try:
            validate_csrf_token(request)
        except PermissionDeniedError as exc:
            # App-level exception handlers run inside the router stack and
            # cannot catch exceptions raised from middleware, so the response
            # is built here.
            return app_error_response(exc)

        return await call_next(request)
