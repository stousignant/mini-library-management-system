"""
Tests for database configuration and SSL handling.

Verifies that database URLs are properly configured with SSL
for production environments like Supabase.
"""

import ssl

import pytest

from app.core.config import Settings, get_cors_origin_regex, get_cors_origins
from app.core.constants import DEFAULT_CORS_ORIGINS
from app.core.database import build_async_database_url


class TestAsyncDatabaseURLConfiguration:
    """Test async database URL configuration with driver and SSL handling."""

    def test_postgresql_driver_converted_to_asyncpg(self):
        """
        Test that postgresql:// URLs are converted to postgresql+asyncpg://.

        Given: A standard PostgreSQL URL without async driver
        When: build_async_database_url is called
        Then: URL is converted to use asyncpg driver
        """
        standard_url = "postgresql://user:pass@localhost:5432/mydb"
        url, connect_args = build_async_database_url(standard_url)
        assert url.startswith("postgresql+asyncpg://")
        assert "user:pass@localhost:5432/mydb" in url
        assert connect_args == {}

    def test_asyncpg_driver_unchanged(self):
        """
        Test that URLs already using asyncpg driver are unchanged.

        Given: A URL already using postgresql+asyncpg://
        When: build_async_database_url is called
        Then: Driver specification remains unchanged
        """
        async_url = "postgresql+asyncpg://user:pass@localhost:5432/mydb"
        url, connect_args = build_async_database_url(async_url)
        assert url == async_url
        assert connect_args == {}

    def test_supabase_url_gets_ssl_and_driver_conversion(self):
        """
        Test that Supabase URLs get both driver conversion and SSL context.

        Given: A Supabase URL with standard postgresql:// driver
        When: build_async_database_url is called
        Then: Driver is converted and SSL context is in connect_args
        """
        supabase_url = "postgresql://user:pass@db.supabase.co/postgres"
        url, connect_args = build_async_database_url(supabase_url)
        assert "postgresql+asyncpg://" in url
        assert "ssl" in connect_args
        assert isinstance(connect_args["ssl"], ssl.SSLContext)

    def test_railway_url_gets_ssl_and_driver_conversion(self):
        """
        Test that Railway URLs get both driver conversion and SSL context.

        Given: A Railway PostgreSQL URL
        When: build_async_database_url is called
        Then: Driver is converted and SSL context is in connect_args
        """
        railway_url = "postgresql://user:pass@containers-us-west-123.railway.app:5432/railway"
        url, connect_args = build_async_database_url(railway_url)
        assert "postgresql+asyncpg://" in url
        assert "ssl" in connect_args
        assert isinstance(connect_args["ssl"], ssl.SSLContext)

    def test_render_url_gets_ssl_and_driver_conversion(self):
        """
        Test that Render URLs get both driver conversion and SSL context.

        Given: A Render PostgreSQL URL
        When: build_async_database_url is called
        Then: Driver is converted and SSL context is in connect_args
        """
        render_url = "postgresql://user:pass@dpg-abc123.render.com:5432/mydb"
        url, connect_args = build_async_database_url(render_url)
        assert "postgresql+asyncpg://" in url
        assert "ssl" in connect_args
        assert isinstance(connect_args["ssl"], ssl.SSLContext)

    def test_flyio_url_gets_ssl_and_driver_conversion(self):
        """
        Test that Fly.io URLs get both driver conversion and SSL context.

        Given: A Fly.io PostgreSQL URL
        When: build_async_database_url is called
        Then: Driver is converted and SSL context is in connect_args
        """
        flyio_url = "postgresql://user:pass@top1.fly.io:5432/mydb"
        url, connect_args = build_async_database_url(flyio_url)
        assert "postgresql+asyncpg://" in url
        assert "ssl" in connect_args
        assert isinstance(connect_args["ssl"], ssl.SSLContext)

    def test_production_url_with_existing_params_gets_ssl_context(self):
        """
        Test SSL context is provided for production URLs with existing query parameters.

        Given: A production URL with existing query parameters
        When: build_async_database_url is called
        Then: SSL context is in connect_args, existing params preserved
        """
        railway_url = "postgresql://user:pass@db.railway.app/postgres?connect_timeout=10"
        url, connect_args = build_async_database_url(railway_url)
        assert "connect_timeout=10" in url
        assert "postgresql+asyncpg://" in url
        assert "ssl" in connect_args
        assert isinstance(connect_args["ssl"], ssl.SSLContext)

    def test_production_url_with_ssl_query_param_gets_ssl_context(self):
        """
        Test that production URLs get SSL context regardless of query params.

        Given: A production URL with ssl query parameter
        When: build_async_database_url is called
        Then: SSL context is provided via connect_args
        """
        railway_url = "postgresql://user:pass@db.railway.app/postgres?ssl=require"
        url, connect_args = build_async_database_url(railway_url)
        assert "postgresql+asyncpg://" in url
        assert "ssl" in connect_args
        assert isinstance(connect_args["ssl"], ssl.SSLContext)

    def test_local_url_gets_driver_conversion_only(self):
        """
        Test that local URLs get driver conversion but not SSL context.

        Given: A localhost database URL
        When: build_async_database_url is called
        Then: Driver is converted but connect_args is empty
        """
        local_url = "postgresql://postgres:postgres@localhost:5432/library_dev"
        url, connect_args = build_async_database_url(local_url)
        assert "postgresql+asyncpg://" in url
        assert connect_args == {}

    def test_local_test_url_gets_driver_conversion_only(self):
        """
        Test that local test URLs get driver conversion but not SSL context.

        Given: A local test database URL
        When: build_async_database_url is called
        Then: Driver is converted but connect_args is empty
        """
        test_url = "postgresql://postgres:postgres@localhost:5433/library_test"
        url, connect_args = build_async_database_url(test_url)
        assert "postgresql+asyncpg://" in url
        assert connect_args == {}


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


class TestCORSWildcardPatterns:
    """Test CORS wildcard pattern support for dynamic domains."""

    def test_single_wildcard_vercel_domain_returns_regex(self, monkeypatch):
        """
        Test wildcard Vercel domain is converted to regex pattern.

        Given: CORS_ORIGINS with https://*.vercel.app
        When: get_cors_origin_regex is called
        Then: Returns regex pattern matching all Vercel subdomains
        """
        monkeypatch.setenv("CORS_ORIGINS", "https://*.vercel.app")
        result = get_cors_origin_regex()
        assert result is not None
        assert "vercel\\.app" in result
        assert r"https://[^/]+\.vercel\.app" in result

    def test_mixed_exact_and_wildcard_origins_returns_regex(self, monkeypatch):
        """
        Test mixed exact and wildcard origins returns combined regex.

        Given: CORS_ORIGINS with both exact and wildcard domains
        When: get_cors_origin_regex is called
        Then: Returns regex matching both exact and wildcard patterns
        """
        monkeypatch.setenv("CORS_ORIGINS", "https://example.com,https://*.vercel.app")
        result = get_cors_origin_regex()
        assert result is not None
        assert "example\\.com" in result
        assert "vercel\\.app" in result

    def test_only_exact_origins_returns_none(self, monkeypatch):
        """
        Test exact origins without wildcards returns None.

        Given: CORS_ORIGINS with only exact domains (no wildcards)
        When: get_cors_origin_regex is called
        Then: Returns None to use allow_origins instead
        """
        monkeypatch.setenv("CORS_ORIGINS", "https://example.com,https://test.com")
        result = get_cors_origin_regex()
        assert result is None

    def test_multiple_wildcard_domains_returns_combined_regex(self, monkeypatch):
        """
        Test multiple wildcard domains are combined in regex.

        Given: CORS_ORIGINS with multiple wildcard patterns
        When: get_cors_origin_regex is called
        Then: Returns regex matching all patterns
        """
        monkeypatch.setenv("CORS_ORIGINS", "https://*.vercel.app,https://*.netlify.app")
        result = get_cors_origin_regex()
        assert result is not None
        assert "vercel\\.app" in result
        assert "netlify\\.app" in result

    def test_no_cors_origins_env_returns_none(self, monkeypatch):
        """
        Test missing CORS_ORIGINS env returns None.

        Given: No CORS_ORIGINS env var set
        When: get_cors_origin_regex is called
        Then: Returns None to fall back to defaults
        """
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        result = get_cors_origin_regex()
        assert result is None
