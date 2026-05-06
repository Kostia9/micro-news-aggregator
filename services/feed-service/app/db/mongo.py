import asyncio
import logging
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


def init_mongo(uri: str, db_name: str) -> None:
    global client, db
    client = AsyncIOMotorClient(uri)
    db = client[db_name]


async def wait_for_mongo(retries: int = 30, delay: float = 1.0) -> None:
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
    await db.articles.create_index("article_id", unique=True)
    await db.articles.create_index([("published_at", -1)])
    await db.articles.create_index("topics")


async def upsert_article(article: dict) -> None:
    if db is None:
        raise RuntimeError("Call init_mongo() before upsert_article()")
    article_id = article.get("article_id")
    if not article_id:
        raise ValueError("article_id is required")
    document = {
        "article_id": str(article_id),
        "title": article.get("title", ""),
        "url": article.get("url", ""),
        "source": article.get("source", ""),
        "topics": list(article.get("topics", [])),
        "summary": article.get("summary"),
        "published_at": _parse_datetime(article.get("published_at")),
    }
    await db.articles.update_one(
        {"article_id": document["article_id"]},
        {"$set": document},
        upsert=True,
    )


async def list_articles(
    page: int,
    page_size: int,
    topic: str | None = None,
) -> tuple[list[dict], int]:
    if db is None:
        raise RuntimeError("Call init_mongo() before list_articles()")
    query = {"topics": topic} if topic else {}
    total = await db.articles.count_documents(query)
    cursor = (
        db.articles.find(query, projection={"_id": 0})
        .sort("published_at", -1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    articles = []
    async for doc in cursor:
        doc["id"] = doc.pop("article_id")
        articles.append(doc)
    return articles, total


def _parse_datetime(raw: object) -> datetime:
    if isinstance(raw, datetime):
        dt = raw
    elif isinstance(raw, str) and raw:
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError:
            dt = datetime.now(timezone.utc)
    else:
        dt = datetime.now(timezone.utc)

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
