"""
Pytest configuration and fixtures for testing.

Provides shared fixtures for database connections, test clients,
and other testing utilities.
"""

import os

import pytest
import pytest_asyncio
import sqlalchemy as sa
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from alembic import command
from app.core.config import get_test_database_url
from app.core.constants import DB_TEST_CONNECT_ARGS
from app.core.database import get_db
from app.main import app
from app.models import Base


@pytest.fixture(scope="session", autouse=True)
def set_test_environment():
    """Ensure ENVIRONMENT is set to 'test' for all tests."""
    os.environ["ENVIRONMENT"] = "test"
    yield
    os.environ.pop("ENVIRONMENT", None)


@pytest.fixture(scope="session")
def test_database_url():
    """Get test database URL."""
    return get_test_database_url()


@pytest.fixture(scope="session", autouse=True)
def setup_database(test_database_url):
    """
    Apply Alembic migrations to test database before tests run.

    This fixture runs automatically at session start and ensures
    the test database has the proper schema via migrations.
    Schema persists after tests; data is cleaned via table truncation.
    """
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_database_url)

    command.upgrade(alembic_cfg, "head")

    yield


@pytest_asyncio.fixture(scope="function")
async def async_engine(test_database_url, setup_database):
    """
    Create async database engine for tests.

    Schema is managed by the setup_database fixture via Alembic migrations.
    """
    engine = create_async_engine(
        test_database_url,
        echo=False,
        future=True,
        poolclass=NullPool,
        connect_args=DB_TEST_CONNECT_ARGS,
    )

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine):
    """
    Create a new database session for each test.

    Each test gets a fresh session that commits to the database.
    Tables are truncated after each test to ensure isolation.
    """
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session

    async with async_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(sa.text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE"))
        await conn.commit()


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
