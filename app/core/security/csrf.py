import uuid

from fastapi import Request
from starlette.exceptions import HTTPException

from app.core.config.settings import settings
from app.core.exceptions.auth import PermissionDeniedError


def generate_csrf_token() -> str:

    return str(uuid.uuid4())


def validate_csrf_token(request: Request) -> None:
  
    if not settings.CSRF_ENABLED:
        return

    csrf_cookie = request.cookies.get(settings.CSRF_COOKIE_NAME)
    csrf_header = request.headers.get(settings.CSRF_HEADER_NAME)

    if not csrf_cookie or not csrf_header:
        raise PermissionDeniedError(
            message="CSRF token missing.",
            details={"reason": "Both CSRF cookie and header are required."}
        )

    if csrf_cookie != csrf_header:
        raise PermissionDeniedError(
            message="CSRF token validation failed.",
            details={"reason": "CSRF header does not match CSRF cookie."}
        )