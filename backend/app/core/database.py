"""
Database connection and session management.

Provides async database engine and session factory for the application.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


def build_async_database_url(database_url: str) -> str:
    """
    Build async database URL with proper driver and SSL configuration.

    Converts postgresql:// to postgresql+asyncpg:// for async support.
    Automatically appends ssl=require for production databases (Supabase, Railway, etc).
    Local development and test URLs remain unchanged (except for driver conversion).

    Args:
        database_url: The base database URL

    Returns:
        Database URL with async driver and SSL parameter if needed
    """
    url = make_url(database_url)

    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+asyncpg")

    is_production_db = "supabase" in str(url) or any(
        host in str(url) for host in ["railway.app", "render.com", "fly.io"]
    )

    if is_production_db:
        query = dict(url.query)
        if "ssl" not in query:
            query["ssl"] = "require"
            return url.set(query=query).render_as_string(hide_password=False)

    return url.render_as_string(hide_password=False)


settings = get_settings()

async_engine = create_async_engine(
    build_async_database_url(settings.database_url),
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
