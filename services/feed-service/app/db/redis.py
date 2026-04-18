import redis.asyncio as aioredis

client: aioredis.Redis | None = None


def init_redis(url: str) -> None:
    global client
    pass


async def get_cached_feed(key: str) -> str | None:
    pass


async def set_cached_feed(key: str, value: str, ttl: int) -> None:
    pass
