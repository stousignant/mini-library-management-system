"""
Database connection and session management.

Provides async database engine and session factory for the application.
"""

import ssl
from collections.abc import AsyncGenerator

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


def build_async_database_url(database_url: str) -> tuple[str, dict]:
    """
    Build async database URL with proper driver and SSL configuration.

    Converts postgresql:// to postgresql+asyncpg:// for async support.
    Returns SSL context in connect_args for production databases (Supabase, Railway, etc).
    Local development and test URLs remain unchanged (except for driver conversion).

    Args:
        database_url: The base database URL

    Returns:
        Tuple of (database_url, connect_args) where connect_args may contain SSL context
    """
    url = make_url(database_url)

    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+asyncpg")

    is_production_db = "supabase" in str(url) or any(
        host in str(url) for host in ["railway.app", "render.com", "fly.io"]
    )

    connect_args = {}
    if is_production_db:
        connect_args["ssl"] = ssl.create_default_context()

    return url.render_as_string(hide_password=False), connect_args


settings = get_settings()

database_url, connect_args = build_async_database_url(settings.database_url)

async_engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    connect_args=connect_args,
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
