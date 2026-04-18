import redis.asyncio as aioredis

client: aioredis.Redis | None = None


def init_redis(url: str) -> None:
    global client
    pass
