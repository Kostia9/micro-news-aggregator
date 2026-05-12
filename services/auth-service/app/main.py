from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db.postgres import create_schema, init_db, wait_for_db
from app.db.redis import init_redis, wait_for_redis
from app.routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(settings.postgres_dsn)
    init_redis(settings.redis_url)
    await wait_for_db(
        settings.dependency_startup_retries,
        settings.dependency_startup_retry_delay_seconds,
    )
    await wait_for_redis(
        settings.dependency_startup_retries,
        settings.dependency_startup_retry_delay_seconds,
    )
    await create_schema()
    yield


app = FastAPI(title="Auth Service", lifespan=lifespan)
app.include_router(auth_router)
