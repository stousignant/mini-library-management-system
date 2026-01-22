"""
Tests for database configuration and SSL handling.

Verifies that database URLs are properly configured with SSL
for production environments like Supabase.
"""

import pytest

from app.core.config import Settings, get_cors_origins
from app.core.constants import DEFAULT_CORS_ORIGINS
from app.core.database import build_database_url_with_ssl


class TestDatabaseSSLConfiguration:
    """Test SSL configuration for database connections."""

    def test_supabase_url_gets_ssl_appended(self):
        """
        Test that Supabase URLs automatically get SSL parameter.

        Given: A Supabase database URL without SSL parameter
        When: build_database_url_with_ssl is called
        Then: SSL parameter is appended to the URL
        """
        supabase_url = "postgresql+asyncpg://user:pass@db.supabase.co/postgres"
        result = build_database_url_with_ssl(supabase_url)
        assert "ssl=require" in result
        assert result == "postgresql+asyncpg://user:pass@db.supabase.co/postgres?ssl=require"

    def test_supabase_url_with_existing_params_gets_ssl(self):
        """
        Test SSL is added to Supabase URLs with existing query parameters.

        Given: A Supabase URL with existing query parameters
        When: build_database_url_with_ssl is called
        Then: SSL parameter is added to existing parameters
        """
        supabase_url = "postgresql+asyncpg://user:pass@db.supabase.co/postgres?connect_timeout=10"
        result = build_database_url_with_ssl(supabase_url)
        assert "ssl=require" in result
        assert "connect_timeout=10" in result

    def test_supabase_url_with_ssl_already_present_unchanged(self):
        """
        Test that existing SSL parameters are not duplicated.

        Given: A Supabase URL that already has ssl parameter
        When: build_database_url_with_ssl is called
        Then: URL is returned unchanged
        """
        supabase_url = "postgresql+asyncpg://user:pass@db.supabase.co/postgres?ssl=require"
        result = build_database_url_with_ssl(supabase_url)
        assert result == supabase_url

    def test_non_supabase_url_unchanged(self):
        """
        Test that non-Supabase URLs are not modified.

        Given: A localhost/non-Supabase database URL
        When: build_database_url_with_ssl is called
        Then: URL is returned unchanged
        """
        local_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/library_dev"
        result = build_database_url_with_ssl(local_url)
        assert result == local_url
        assert "ssl=" not in result

    def test_local_test_url_unchanged(self):
        """
        Test that local test URLs remain unchanged.

        Given: A local test database URL
        When: build_database_url_with_ssl is called
        Then: URL is returned unchanged
        """
        test_url = "postgresql+asyncpg://postgres:postgres@localhost:5433/library_test"
        result = build_database_url_with_ssl(test_url)
        assert result == test_url
        assert "ssl=" not in result


class TestDatabaseCredentialSecurity:
    """Test that database credentials are properly secured."""

    def test_development_environment_requires_explicit_database_url(self, monkeypatch):
        """
        Test development environment fails without DEV_DATABASE_URL.

        Given: ENVIRONMENT=development and no DEV_DATABASE_URL
        When: Settings is instantiated
        Then: ValueError is raised with security message
        """
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("DEV_DATABASE_URL", raising=False)
        monkeypatch.delenv("LOCAL_DATABASE_URL", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")

        with pytest.raises(ValueError, match="DEV_DATABASE_URL environment variable must be set"):
            Settings(_env_file=None)

    def test_production_environment_requires_explicit_database_url(self, monkeypatch):
        """
        Test production environment fails without DATABASE_URL.

        Given: ENVIRONMENT=production and no DATABASE_URL
        When: Settings is instantiated
        Then: ValueError is raised
        """
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("DEV_DATABASE_URL", raising=False)
        monkeypatch.delenv("LOCAL_DATABASE_URL", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "production")

        with pytest.raises(ValueError, match="DATABASE_URL environment variable must be set"):
            Settings(_env_file=None)

    def test_local_environment_uses_default_safely(self, monkeypatch):
        """
        Test local environment can use default credentials safely.

        Given: ENVIRONMENT=local and no explicit database URL
        When: Settings is instantiated
        Then: Default test database URL is used
        """
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("DEV_DATABASE_URL", raising=False)
        monkeypatch.delenv("LOCAL_DATABASE_URL", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "local")

        settings = Settings(_env_file=None)
        assert "localhost:5433" in settings.database_url
        assert "library_test" in settings.database_url

    def test_development_environment_works_with_explicit_url(self, monkeypatch):
        """
        Test development environment works when URL is provided.

        Given: ENVIRONMENT=development with DEV_DATABASE_URL set
        When: Settings is instantiated
        Then: Settings uses the provided URL
        """
        dev_url = "postgresql+asyncpg://user:pass@dev.example.com/mydb"
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("LOCAL_DATABASE_URL", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("DEV_DATABASE_URL", dev_url)

        settings = Settings(_env_file=None)
        assert settings.database_url == dev_url


class TestCORSOriginsConfiguration:
    """Test CORS origins configuration and fallback behavior."""

    def test_cors_origins_from_env_with_valid_origins(self, monkeypatch):
        """
        Test CORS origins are correctly parsed from environment variable.

        Given: CORS_ORIGINS env var with comma-separated valid origins
        When: get_cors_origins is called
        Then: Returns trimmed list of origins
        """
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://example.com")
        result = get_cors_origins()
        assert result == ["http://localhost:3000", "http://example.com"]

    def test_cors_origins_from_env_with_whitespace(self, monkeypatch):
        """
        Test CORS origins are trimmed when env var has extra whitespace.

        Given: CORS_ORIGINS env var with whitespace around origins
        When: get_cors_origins is called
        Then: Returns trimmed origins without whitespace
        """
        monkeypatch.setenv("CORS_ORIGINS", "  http://localhost:3000  , http://example.com  ")
        result = get_cors_origins()
        assert result == ["http://localhost:3000", "http://example.com"]

    def test_cors_origins_filters_empty_strings(self, monkeypatch):
        """
        Test empty strings are filtered out from CORS origins.

        Given: CORS_ORIGINS env var with empty/blank entries
        When: get_cors_origins is called
        Then: Returns only non-empty origins
        """
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000, , ,http://example.com,  ")
        result = get_cors_origins()
        assert result == ["http://localhost:3000", "http://example.com"]

    def test_cors_origins_fallback_when_only_empty_strings(self, monkeypatch):
        """
        Test fallback to defaults when all entries are empty/whitespace.

        Given: CORS_ORIGINS env var with only empty/whitespace entries
        When: get_cors_origins is called
        Then: Returns DEFAULT_CORS_ORIGINS
        """
        monkeypatch.setenv("CORS_ORIGINS", " , , ,  ")
        result = get_cors_origins()
        assert result == DEFAULT_CORS_ORIGINS

    def test_cors_origins_fallback_when_env_not_set(self, monkeypatch):
        """
        Test fallback to defaults when CORS_ORIGINS env var is not set.

        Given: No CORS_ORIGINS env var
        When: get_cors_origins is called
        Then: Returns DEFAULT_CORS_ORIGINS
        """
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        result = get_cors_origins()
        assert result == DEFAULT_CORS_ORIGINS

    def test_cors_origins_fallback_when_env_is_empty_string(self, monkeypatch):
        """
        Test fallback to defaults when CORS_ORIGINS env var is empty string.

        Given: CORS_ORIGINS env var set to empty string
        When: get_cors_origins is called
        Then: Returns DEFAULT_CORS_ORIGINS
        """
        monkeypatch.setenv("CORS_ORIGINS", "")
        result = get_cors_origins()
        assert result == DEFAULT_CORS_ORIGINS
