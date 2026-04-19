import asyncio
import logging

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


def init_mongo(uri: str, db_name: str) -> None:
    global client, db
    client = AsyncIOMotorClient(uri)
    db = client[db_name]


async def wait_for_mongo(retries: int = 30, delay: float = 1.0) -> None:
    assert client is not None
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
    assert db is not None
    await db.articles.create_index("url", unique=True)


async def save_article(article: dict) -> str:
    assert db is not None
    result = await db.articles.insert_one(article)
    return str(result.inserted_id)


async def is_published(url: str) -> bool:
    assert db is not None
    doc = await db.articles.find_one({"url": url, "published": True}, projection={"_id": 1})
    return doc is not None


async def get_article_id_by_url(url: str) -> str | None:
    assert db is not None
    doc = await db.articles.find_one({"url": url}, projection={"_id": 1})
    return str(doc["_id"]) if doc else None


async def mark_published(article_id: str) -> None:
    assert db is not None
    await db.articles.update_one({"_id": ObjectId(article_id)}, {"$set": {"published": True}})
