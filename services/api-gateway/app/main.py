import asyncio
from contextlib import asynccontextmanager

import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI
from redis.exceptions import RedisError

from app.config import settings
from app.routes.proxy import router as proxy_router


async def wait_for_redis(redis: aioredis.Redis, retries: int, delay: float) -> None:
    for attempt in range(1, retries + 1):
        try:
            if await redis.ping():
                return
        except RedisError:
            if attempt == retries:
                raise
            await asyncio.sleep(delay)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=10.0)
    app.state.redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    try:
        await wait_for_redis(
            app.state.redis,
            settings.redis_startup_retries,
            settings.redis_startup_retry_delay_seconds,
        )
        yield
    finally:
        await app.state.http_client.aclose()
        await app.state.redis.aclose()


app = FastAPI(title="API Gateway", lifespan=lifespan)
app.include_router(proxy_router)
