"""
Application configuration management.

Handles environment variables and application settings using Pydantic.
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/library_dev"
    environment: str = "development"
    pythonunbuffered: str = "1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


def get_test_database_url() -> str:
    """Get test database URL from environment or use default."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5433/library_test",
    )
