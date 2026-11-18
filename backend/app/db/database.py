import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.core.config import settings

IS_VERCEL = os.environ.get("VERCEL", "") == "1"

# Create async engine (use NullPool in serverless environments to avoid stale pooled connections)
engine_kwargs = {
    "echo": not IS_VERCEL,
    "future": True,
}
if IS_VERCEL:
    engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(
    settings.async_database_url,
    **engine_kwargs,
)

# Create session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncSession:
    """
    Dependency to get DB session.
    """
    async with AsyncSessionLocal() as session:
        yield session
