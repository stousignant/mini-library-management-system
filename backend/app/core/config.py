"""
Application configuration management.

Handles environment variables and application settings using Pydantic.
"""

import logging
import os
from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import DEFAULT_CORS_ORIGINS, DEFAULT_TEST_DB_URL, TEST_JWT_SECRET

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str | None = None
    environment: str = "development"
    pythonunbuffered: str = "1"
    supabase_jwt_secret: str | None = None
    supabase_url: str | None = None
    supabase_anon_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("supabase_jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str | None) -> str | None:
        """Ensure JWT secret is not a placeholder and meets minimum length."""
        if v is None:
            return v

        if v == TEST_JWT_SECRET:
            return v

        placeholder_values = [
            "your-jwt-secret-from-supabase-dashboard",
            "your_jwt_secret_here",
            "changeme",
        ]

        if not v:
            raise ValueError("SUPABASE_JWT_SECRET must not be empty")

        if v.lower() in [p.lower() for p in placeholder_values]:
            raise ValueError(
                "SUPABASE_JWT_SECRET must be set to a valid JWT secret. "
                "Get it from Supabase Dashboard > Settings > API > JWT Secret"
            )

        if len(v) < 32:
            raise ValueError("SUPABASE_JWT_SECRET must be at least 32 characters for security")

        return v

    @model_validator(mode="after")
    def set_database_url(self) -> "Settings":
        """Set database URL based on environment if not explicitly provided."""
        if self.database_url is not None:
            return self

        if self.environment in ("local", "test"):
            self.database_url = os.getenv("LOCAL_DATABASE_URL", DEFAULT_TEST_DB_URL)
        elif self.environment == "development":
            self.database_url = os.getenv("DEV_DATABASE_URL", "")
            if not self.database_url:
                raise ValueError(
                    "DEV_DATABASE_URL environment variable must be set for development environment. "
                    "Refusing to use default credentials for security reasons."
                )
        elif self.environment == "production":
            self.database_url = os.getenv("DATABASE_URL", "")
            if not self.database_url:
                raise ValueError("DATABASE_URL environment variable must be set for production environment")
        else:
            self.database_url = os.getenv("DEV_DATABASE_URL", "")
            if not self.database_url:
                raise ValueError(f"Database URL must be set for environment: {self.environment}")

        return self

    @model_validator(mode="after")
    def set_jwt_secret(self) -> "Settings":
        """Set JWT secret based on environment if not explicitly provided."""
        if self.supabase_jwt_secret is not None:
            return self

        if self.environment in ("local", "test"):
            self.supabase_jwt_secret = TEST_JWT_SECRET
        else:
            raise ValueError(
                f"SUPABASE_JWT_SECRET environment variable must be set for {self.environment} environment. "
                "Get it from Supabase Dashboard > Settings > API > JWT Secret"
            )

        return self


@lru_cache
def get_settings() -> Settings:
    """Get application settings instance with caching to avoid multiple loads."""
    logger.info(f"Loading settings from environment: ENVIRONMENT={os.getenv('ENVIRONMENT')}")
    logger.info(f"SUPABASE_URL from os.getenv: {os.getenv('SUPABASE_URL', 'NOT SET')}")
    logger.info(f"SUPABASE_JWT_SECRET from os.getenv: {'SET' if os.getenv('SUPABASE_JWT_SECRET') else 'NOT SET'}")

    settings = Settings()
    logger.info(f"Settings loaded - supabase_url: {settings.supabase_url if settings.supabase_url else 'NOT SET'}")
    logger.info(f"Settings loaded - environment: {settings.environment}")

    return settings


def get_test_database_url() -> str:
    """Get test database URL from environment or use default.

    Priority order:
    1. TEST_DATABASE_URL env var (dedicated test DB URL)
    2. Default local test URL from constants
    """
    return os.getenv(
        "TEST_DATABASE_URL",
        DEFAULT_TEST_DB_URL,
    )


def get_cors_origins() -> list[str]:
    """Get CORS origins from environment or use defaults.

    Priority order:
    1. CORS_ORIGINS env var (comma-separated list, trimmed and filtered)
    2. Default CORS origins from constants (if env var is empty/blank)
    """
    cors_env = os.getenv("CORS_ORIGINS")
    if cors_env:
        origins = [origin.strip() for origin in cors_env.split(",")]
        origins = [origin for origin in origins if origin]
        if origins:
            return origins
    return DEFAULT_CORS_ORIGINS


def get_cors_origin_regex() -> str | None:
    """Get CORS origin regex pattern for wildcard domains.

    Returns regex pattern if any origins contain wildcards (*), otherwise None.
    When None is returned, use get_cors_origins() with allow_origins instead.

    Converts patterns like https://*.vercel.app to regex patterns that match
    all subdomains while escaping special characters properly.

    Returns:
        Regex pattern string if wildcards present, None if only exact origins
    """
    cors_env = os.getenv("CORS_ORIGINS")
    if not cors_env:
        return None

    origins = [origin.strip() for origin in cors_env.split(",")]
    origins = [origin for origin in origins if origin]

    if not origins:
        return None

    has_wildcard = any("*" in origin for origin in origins)
    if not has_wildcard:
        return None

    import re

    patterns = []
    for origin in origins:
        if "*" in origin:
            escaped = re.escape(origin)
            pattern = escaped.replace(r"\*", r"[^/]+")
            patterns.append(pattern)
        else:
            escaped = re.escape(origin)
            patterns.append(escaped)

    return "|".join(patterns)
