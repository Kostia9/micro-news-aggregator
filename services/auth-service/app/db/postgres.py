from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None


def init_db(dsn: str) -> None:
    global engine, SessionLocal
    pass
