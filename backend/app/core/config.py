"""
Application configuration management.

Handles environment variables and application settings using Pydantic.
"""

import os

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import DEFAULT_TEST_DB_URL


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str | None = None
    environment: str = "development"
    pythonunbuffered: str = "1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def set_database_url(self) -> "Settings":
        """Set database URL based on environment if not explicitly provided."""
        if self.database_url is not None:
            return self

        if self.environment == "local":
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


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


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
