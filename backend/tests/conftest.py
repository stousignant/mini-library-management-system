"""
Pytest configuration and fixtures for testing.

Provides shared fixtures for database connections, test clients,
and other testing utilities.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_test_database_url
from app.main import app


@pytest.fixture(scope="session")
def test_database_url():
    """Get test database URL."""
    return get_test_database_url()


@pytest.fixture(scope="session")
async def async_engine(test_database_url):
    """Create async database engine for tests."""
    engine = create_async_engine(
        test_database_url,
        echo=False,
        future=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(async_engine):
    """
    Create a new database session for each test.
    
    Rolls back all changes after the test completes to ensure
    test isolation.
    """
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(async_session):
    """
    Create an async test client with database session override.
    
    This client can be used to make HTTP requests to the FastAPI
    application during tests.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
