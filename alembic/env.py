from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.configurations.settings import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url in alembic.ini with our database URL from settings
config.set_main_option("sqlalchemy.url", settings.database_url.replace("+asyncpg", ""))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# Import the models that should be part of the metadata
from src.models.base import BaseModel
from src.models.books import Book
from src.models.sellers import Seller

target_metadata = BaseModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True 
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode asynchronously."""
    sync_url = settings.database_url.replace('postgresql+asyncpg', 'postgresql')  # the sync version of database_url by replacing the driver

    connectable = engine_from_config(
        {"sqlalchemy.url": sync_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    sync_url = settings.database_url.replace('postgresql+asyncpg', 'postgresql')
    
    connectable = engine_from_config(
        {"sqlalchemy.url": sync_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()