"""
Database connection and session management.

Provides async database engine and session factory for the application.
"""

from collections.abc import AsyncGenerator
from urllib.parse import parse_qs, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


def build_database_url_with_ssl(database_url: str) -> str:
    """
    Build database URL with SSL parameter for production databases.

    Automatically appends ssl=require for Supabase URLs if not already present.
    Local development and test URLs remain unchanged.

    Args:
        database_url: The base database URL

    Returns:
        Database URL with SSL parameter if needed
    """
    if "supabase" not in database_url:
        return database_url

    if "ssl=" in database_url:
        return database_url

    parsed = urlparse(database_url)
    query_params = parse_qs(parsed.query) if parsed.query else {}
    query_params["ssl"] = ["require"]

    query_string = "&".join(f"{key}={value[0]}" for key, value in query_params.items())

    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, query_string, parsed.fragment))


settings = get_settings()

async_engine = create_async_engine(
    build_database_url_with_ssl(settings.database_url),
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.

    Yields an async database session. Transaction management
    is handled by the service layer via explicit commit/rollback calls.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
