import asyncio
import logging
import sys

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from alembic import command
from alembic.config import Config
from src.configurations.settings import settings

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = settings.database_url

__async_engine = None
__session_factory = None

__all__ = [
    "global_init",
    "get_async_session",
    "run_alembic_upgrade",
    "create_db_and_tables",
]


def global_init() -> None:
    """
    Initializes the async database engine and session factory.
    """
    global __async_engine, __session_factory
    if __session_factory:
        return
    if not __async_engine:
        __async_engine = create_async_engine(url=SQLALCHEMY_DATABASE_URL, echo=True)
    __session_factory = async_sessionmaker(__async_engine, expire_on_commit=False)



async def get_async_session() -> AsyncSession:
    """
    Provides an async database session.
    """
    global __session_factory
    if not __session_factory:
        raise ValueError("You must call global_init() before using this method")

    session: AsyncSession = __session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        logger.error("Exception occurred: %s", e)
        raise e
    finally:
        await session.rollback()
        await session.close()


def run_alembic_upgrade():
    """
    Runs Alembic migrations synchronously. Ensures that all migrations are applied.
    """
    logger.info("Running Alembic migrations...")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option(
        "sqlalchemy.url", settings.database_url.replace("+asyncpg", "")
    )
    command.upgrade(alembic_cfg, "head")
    logger.info("✅ Alembic migrations applied successfully.")


async def create_db_and_tables():
    """
    Uses Alembic to apply the latest migrations instead of directly calling create_all().
    """
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_alembic_upgrade)
