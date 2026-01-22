"""
Application configuration management.

Handles environment variables and application settings using Pydantic.
"""

import os

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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

        local_db_url = os.getenv(
            "LOCAL_DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5433/library_test",
        )
        dev_db_url = os.getenv(
            "DEV_DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/library_dev",
        )

        environment_database_map = {
            "local": local_db_url,
            "development": dev_db_url,
            "production": os.getenv("DATABASE_URL", ""),
        }

        self.database_url = environment_database_map.get(
            self.environment,
            dev_db_url,
        )

        if self.environment == "production" and not self.database_url:
            raise ValueError("DATABASE_URL environment variable must be set for production environment")

        return self


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


def get_test_database_url() -> str:
    """Get test database URL from environment or use default.

    Priority order:
    1. TEST_DATABASE_URL env var (dedicated test DB URL)
    2. Hardcoded local test URL fallback
    """
    return os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5433/library_test",
    )
