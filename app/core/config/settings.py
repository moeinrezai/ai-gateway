from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_ENV: str = Field(
        default="development",
        description="Environment: development, testing, production",
    )
    APP_DEBUG: bool = Field(default=True, description="Enable debug mode")
    APP_NAME: str = Field(default="AI Gateway")
    APP_API_V1_PREFIX: str = Field(default="/api/v1")

    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: SecretStr = Field(default=SecretStr("postgres"))
    DB_NAME: str = Field(default="ai_gateway")
    DB_ECHO: bool = Field(default=False, description="Enable SQLAlchemy SQL logging")

    @property
    def database_url(self) -> str:

        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: SecretStr | None = Field(default=None)
    REDIS_DB: int = Field(default=0)

    @property
    def redis_url(self) -> str:

        pwd = self.REDIS_PASSWORD.get_secret_value() if self.REDIS_PASSWORD else ""
        auth = f":{pwd}@" if pwd else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    JWT_SECRET_KEY: SecretStr = Field(
        default=SecretStr("super-secret-key-change-in-production")
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    OPENAI_API_KEY: SecretStr = Field(default=SecretStr(""))
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1")
    AI_REQUEST_TIMEOUT: int = Field(
        default=30, description="Timeout in seconds for AI provider requests"
    )
    AI_DEFAULT_MODEL: str = Field(default="gpt-3.5-turbo")

    TRUSTED_PROXIES: str = Field(
        default="127.0.0.1",
        description="Comma-separated list of trusted proxy IPs (e.g., '127.0.0.1,10.0.0.1')",
    )
    
    

    @property
    def trusted_proxies_list(self) -> list[str]:

        if not self.TRUSTED_PROXIES:
            return []
        return [ip.strip() for ip in self.TRUSTED_PROXIES.split(",") if ip.strip()]
    
    CSRF_ENABLED: bool = Field(
        default=True,
        description="Enable CSRF protection for state-changing requests",
    )
    CSRF_HEADER_NAME: str = Field(
        default="X-CSRF-Token",
        description="HTTP header name for CSRF token",
    )
    CSRF_COOKIE_NAME: str = Field(
        default="csrf_token",
        description="Cookie name for CSRF token",
    )
    CSRF_COOKIE_SECURE: bool = Field(
        default=True,
        description="Set Secure flag on CSRF cookie (True in production)",
    )
    CSRF_COOKIE_SAMESITE: str = Field(
        default="lax",
        description="SameSite attribute for CSRF cookie (lax, strict, none)",
    )
    CSRF_COOKIE_PATH: str = Field(
        default="/",
        description="Path for CSRF cookie",
    )

settings = Settings()
