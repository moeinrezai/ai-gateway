from app.core.exceptions.base import AppException


class RateLimitExceededError(AppException):
    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        retry_after: int | None = None,
        details: dict | None = None,
    ):
        super().__init__(
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            message=message,
            details=details or {},
        )
        self.retry_after = retry_after