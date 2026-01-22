"""
Tests for database configuration and SSL handling.

Verifies that database URLs are properly configured with SSL
for production environments like Supabase.
"""

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
