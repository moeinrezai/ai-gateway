from app.core.exceptions.base import AppException


class AIProviderError(AppException):
    def __init__(
        self,
        message: str = "AI provider error occurred.",
        provider: str | None = None,
        details: dict | None = None,
    ):
        super().__init__(
            status_code=502,
            error_code="AI_PROVIDER_ERROR",
            message=message,
            details=details or {},
        )
        self.provider = provider


class AIProviderTimeoutError(AIProviderError):
    def __init__(
        self,
        provider: str | None = None,
        message: str = "AI provider request timed out.",
    ):
        super().__init__(
            status_code=504,
            error_code="AI_PROVIDER_TIMEOUT",
            message=message,
            provider=provider,
        )


class AIProviderUnavailableError(AIProviderError):
    def __init__(
        self,
        provider: str | None = None,
        message: str = "AI provider is currently unavailable.",
    ):
        super().__init__(
            status_code=503,
            error_code="AI_PROVIDER_UNAVAILABLE",
            message=message,
            provider=provider,
        )


class AIProviderAuthenticationError(AIProviderError):
    def __init__(
        self,
        provider: str | None = None,
        message: str = "AI provider authentication failed.",
    ):
        super().__init__(
            status_code=502,
            error_code="AI_PROVIDER_AUTH_ERROR",
            message=message,
            provider=provider,
        )


class AIInvalidModelError(AppException):
    def __init__(self, model: str, message: str | None = None):
        super().__init__(
            status_code=400,
            error_code="AI_INVALID_MODEL",
            message=message or f"Model '{model}' is not supported or not allowed.",
            details={"model": model},
        )


class AIPromptTooLargeError(AppException):
    def __init__(self, max_tokens: int, message: str | None = None):
        super().__init__(
            status_code=400,
            error_code="AI_PROMPT_TOO_LARGE",
            message=message or f"Prompt exceeds maximum allowed tokens ({max_tokens}).",
            details={"max_tokens": max_tokens},
        )
