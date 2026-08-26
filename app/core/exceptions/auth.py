from app.core.exceptions.base import AppException


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed.", details: dict | None = None):
        super().__init__(
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            message=message,
            details=details,
        )


class InvalidTokenError(AppException):
    def __init__(self, message: str = "Invalid or expired token.", details: dict | None = None):
        super().__init__(
            status_code=401,
            error_code="INVALID_TOKEN",
            message=message,
            details=details,
        )


class PermissionDeniedError(AppException):
    def __init__(self, message: str = "Permission denied.", details: dict | None = None):
        super().__init__(
            status_code=403,
            error_code="PERMISSION_DENIED",
            message=message,
            details=details,
        )


class UserAlreadyExistsError(AppException):
    def __init__(self, message: str = "User with this email already exists.", details: dict | None = None):
        super().__init__(
            status_code=409,
            error_code="USER_ALREADY_EXISTS",
            message=message,
            details=details,
        )