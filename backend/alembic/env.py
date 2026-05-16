import os
from logging.config import fileConfig
from sqlalchemy import pool, create_engine, text
from sqlalchemy.engine import Connection
from alembic import context

alembic_config = context.config

if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)


def get_sync_url() -> str:
    """Get a synchronous (psycopg2) database URL for Alembic migrations."""
    url = os.environ.get(
        "DATABASE_URL",
        alembic_config.get_main_option("sqlalchemy.url", "")
    )
    # Strip async drivers — Alembic needs psycopg2 (sync)
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace("postgres://", "postgresql://")
    return url


# Import models for autogenerate support
# We import Base directly without triggering async engine creation
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import all models so Alembic sees the tables
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.user import User  # noqa
from app.models.lesson import Lesson  # noqa
from app.models.vocabulary import VocabularyItem, UserVocabulary  # noqa
from app.models.progress import LessonProgress  # noqa
from app.models.streak import Streak  # noqa
from app.models.oral_report import OralReport  # noqa

# Use the app's Base for metadata (models are registered there)
from app.core.database import Base as AppBase
target_metadata = AppBase.metadata


def run_migrations_offline() -> None:
    url = get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_sync_url()
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        do_run_migrations(connection)
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
