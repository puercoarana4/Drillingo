import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


def _get_async_url() -> str:
    """
    Build the async database URL, converting any sync driver prefix.
    This runs at import time so the engine always gets the right URL.
    """
    # Try environment variable first (Railway sets this), then fall back to config
    try:
        from app.core.config import settings
        url = settings.DATABASE_URL
    except Exception:
        url = os.environ.get("DATABASE_URL", "")

    # Ensure asyncpg driver is used
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return url


# Async engine
engine = create_async_engine(
    _get_async_url(),
    echo=False,
    future=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
