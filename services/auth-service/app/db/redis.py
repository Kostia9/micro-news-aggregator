import asyncio
import logging

import redis.asyncio as aioredis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

client: aioredis.Redis | None = None


def init_redis(url: str) -> None:
    global client
    client = aioredis.from_url(url, decode_responses=True)


async def wait_for_redis(retries: int = 30, delay: float = 1.0) -> None:
    assert client is not None
    for attempt in range(1, retries + 1):
        try:
            if await client.ping():
                return
        except RedisError as exc:
            if attempt == retries:
                raise
            logger.warning("redis not ready (attempt %s/%s): %s", attempt, retries, exc)
            await asyncio.sleep(delay)


def get_redis() -> aioredis.Redis:
    assert client is not None, "init_redis must be called before get_redis"
    return client
