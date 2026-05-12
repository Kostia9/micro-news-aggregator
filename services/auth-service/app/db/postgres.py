import asyncio
import logging
from collections.abc import AsyncIterator

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.user import Base

logger = logging.getLogger(__name__)

engine = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None

SCHEMA_LOCK_KEY = 4891234567


def init_db(dsn: str) -> None:
    global engine, SessionLocal
    engine = create_async_engine(dsn, pool_pre_ping=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def wait_for_db(retries: int, delay: float) -> None:
    assert engine is not None
    for attempt in range(1, retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return
        except OperationalError as exc:
            if attempt == retries:
                raise
            logger.warning("postgres not ready (attempt %s/%s): %s", attempt, retries, exc)
            await asyncio.sleep(delay)


async def create_schema() -> None:
    assert engine is not None
    async with engine.begin() as conn:
        await conn.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": SCHEMA_LOCK_KEY})
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    assert SessionLocal is not None, "init_db must be called before get_session"
    async with SessionLocal() as session:
        yield session
