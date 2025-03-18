import asyncio

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.configurations.database import run_alembic_upgrade
from src.configurations.settings import settings
from src.models.base import BaseModel

# Create an async engine for the test DB
async_test_engine = create_async_engine(
    settings.database_test_url,
    echo=False,
    poolclass=NullPool,
)

# A session factory for the test database
async_test_session = async_sessionmaker(
    bind=async_test_engine, expire_on_commit=False, autoflush=False
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Run Alembic migrations on the test database once per session."""
    # TODO: adjust run_alembic_upgrade to use the test URL.
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_alembic_upgrade)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Provide a clean database session for each test function."""
    async with async_test_session() as session:
        # Start with clean tables for each test
        try:
            # Clean tables within transaction
            await session.execute(text("TRUNCATE TABLE books_table CASCADE"))
            await session.execute(text("TRUNCATE TABLE sellers CASCADE"))
            await session.commit()

            yield session
        finally:
            # Ensure rollback happens if test fails
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def print_table_info():
    """Debug fixture to print table information."""
    async with async_test_engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
        )
        tables = result.fetchall()
        print("Available tables in the database:", [table[0] for table in tables])


@pytest.fixture
def override_get_async_session(db_session):
    """Override the get_async_session dependency for testing."""

    async def _override_get_async_session():
        yield db_session

    return _override_get_async_session


@pytest.fixture
def test_app(override_get_async_session):
    """Configure test application with test database session."""
    from src.configurations.database import get_async_session
    from src.main import app

    app.dependency_overrides[get_async_session] = override_get_async_session
    return app


@pytest_asyncio.fixture
async def async_client(test_app):
    """Provide an async HTTP client configured to use the test app."""
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://127.0.0.1:8000"
    ) as client:
        yield client
