"""
Database connection and session management.

Provides async database engine and session factory for the application.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

async_engine = create_async_engine(
    settings.database_url,
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

    Yields an async database session with explicit transaction management.
    Ensures rollback on errors and proper cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                yield session
        except:
            await session.rollback()
            raise
