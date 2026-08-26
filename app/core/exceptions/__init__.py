from app.core.exceptions.auth import (
    AuthenticationError,
    InvalidTokenError,
    PermissionDeniedError,
    UserAlreadyExistsError,
)
from app.core.exceptions.base import AppException
from app.core.exceptions.handlers import register_exception_handlers
from app.core.exceptions.rate_limit import RateLimitExceededError

__all__ = [
    "AppException",
    "AuthenticationError",
    "InvalidTokenError",
    "PermissionDeniedError",
    "UserAlreadyExistsError",
    "RateLimitExceededError",
    "register_exception_handlers",
]