import asyncio
import logging
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


def init_mongo(uri: str, db_name: str) -> None:
    global client, db
    client = AsyncIOMotorClient(uri)
    db = client[db_name]


async def wait_for_mongo(retries: int, delay: float) -> None:
    if client is None:
        raise RuntimeError("Call init_mongo() before wait_for_mongo()")
    for attempt in range(1, retries + 1):
        try:
            await client.admin.command("ping")
            return
        except Exception as exc:
            if attempt == retries:
                raise
            logger.warning("mongo not ready (attempt %s/%s): %s", attempt, retries, exc)
            await asyncio.sleep(delay)


async def ensure_indexes() -> None:
    if db is None:
        raise RuntimeError("Call init_mongo() before ensure_indexes()")
    await db.seen_urls.create_index("url", unique=True)


async def is_url_seen(url: str) -> bool:
    if db is None:
        raise RuntimeError("Call init_mongo() before is_url_seen()")
    doc = await db.seen_urls.find_one({"url": url}, projection={"_id": 1})
    return doc is not None


async def mark_url_seen(url: str, source: str) -> None:
    if db is None:
        raise RuntimeError("Call init_mongo() before mark_url_seen()")
    try:
        await db.seen_urls.insert_one(
            {
                "url": url,
                "source": source,
                "seen_at": datetime.now(timezone.utc),
            }
        )
    except DuplicateKeyError:
        return
