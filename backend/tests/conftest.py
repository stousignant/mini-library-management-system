"""
Pytest configuration and fixtures for testing.

Provides shared fixtures for database connections, test clients,
and other testing utilities.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_test_database_url
from app.core.database import get_db
from app.main import app
from app.models.book import Base


@pytest.fixture(scope="session")
def test_database_url():
    """Get test database URL."""
    return get_test_database_url()


@pytest_asyncio.fixture(scope="function")
async def async_engine(test_database_url):
    """Create async database engine for tests."""
    engine = create_async_engine(
        test_database_url,
        echo=False,
        future=True,
        poolclass=NullPool,  # Use NullPool to avoid connection pool issues
        connect_args={"server_settings": {"jit": "off"}, "ssl": "disable"},
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine):
    """
    Create a new database session for each test.

    Each test gets a fresh session that commits to the database.
    Tables are cleaned up between tests by the engine fixture.
    """
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(async_session):
    """
    Create an async test client with database session override.

    This client can be used to make HTTP requests to the FastAPI
    application during tests.
    """

    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
