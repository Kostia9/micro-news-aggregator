import asyncio
import logging
import signal
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from app.config import settings
from app.consumer.kafka import ArticleConsumer
from app.db.mongo import (
    ensure_indexes,
    get_article_id_by_url,
    init_mongo,
    is_published,
    mark_published,
    save_article,
    wait_for_mongo,
)
from app.processors.enricher import enrich
from app.processors.tagger import assign_topics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class ArticleDoc:
    title: str
    url: str
    source: str
    content: str
    published_at: datetime
    summary: str | None
    topics: list[str]
    word_count: int
    processed_at: datetime
    published: bool = False


def _parse_published_at(raw: str) -> datetime:
    try:
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)


_REQUIRED_FIELDS = ("url", "title", "source", "content")


def _merge_topics(source_topics: list[str], assigned_topics: list[str]) -> list[str]:
    topics: list[str] = []
    for topic in [*source_topics, *assigned_topics]:
        if topic and topic not in topics:
            topics.append(topic)
    return topics or ["general"]


async def process_one(raw: dict, consumer: ArticleConsumer) -> None:
    missing = [f for f in _REQUIRED_FIELDS if not raw.get(f)]
    if missing:
        logger.warning("Message missing required fields %s, skipping", missing)
        return

    url = raw["url"]

    if await is_published(url):
        logger.debug("Duplicate skipped: %s", url)
        return

    article: dict = {
        "title": raw.get("title", ""),
        "url": url,
        "source": raw.get("source", ""),
        "content": raw.get("content", ""),
        "published_at": _parse_published_at(raw.get("published_at", "")),
        "summary": None,
    }

    article = await enrich(article)
    article["topics"] = _merge_topics(raw.get("topics", []), await assign_topics(article))

    doc = ArticleDoc(
        title=article["title"],
        url=article["url"],
        source=article["source"],
        content=article["content"],
        published_at=article["published_at"],
        summary=article["summary"],
        topics=article["topics"],
        word_count=article["word_count"],
        processed_at=article["processed_at"],
    )

    try:
        article_id = await save_article(asdict(doc))
    except DuplicateKeyError:
        article_id = await get_article_id_by_url(url)
        if article_id is None:
            logger.error("DuplicateKeyError but article not found for url: %s", url)
            return
        logger.debug("Re-publishing unpublished article: %s", url)

    processed_event = {
        "article_id": article_id,
        "title": doc.title,
        "url": doc.url,
        "content": doc.content,
        "source": doc.source,
        "topics": doc.topics,
        "published_at": doc.published_at.isoformat(),
    }
    await consumer.produce(processed_event)
    await mark_published(article_id)
    await consumer.commit()

    logger.info("Processed %s (%s)", article_id, url)


async def start_consumer_with_retry(consumer: ArticleConsumer) -> None:
    for attempt in range(1, settings.kafka_startup_retries + 1):
        try:
            await consumer.start()
            return
        except Exception:
            if attempt == settings.kafka_startup_retries:
                logger.exception("Kafka consumer did not start after %s attempts", attempt)
                raise
            logger.warning(
                "Kafka consumer not ready (attempt %s/%s), retrying in %.1fs",
                attempt,
                settings.kafka_startup_retries,
                settings.kafka_startup_retry_delay_seconds,
            )
            await asyncio.sleep(settings.kafka_startup_retry_delay_seconds)


async def main() -> None:
    init_mongo(settings.mongo_uri, settings.mongo_db)
    await wait_for_mongo()
    await ensure_indexes()

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _handle_signal() -> None:
        logger.info("Shutdown signal received")
        stop_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _handle_signal)

    consumer = ArticleConsumer()
    try:
        await start_consumer_with_retry(consumer)

        logger.info(
            "processing-service started, consuming from %s", settings.kafka_topic_raw
        )

        async for msg in consumer:
            if stop_event.is_set():
                break
            try:
                await process_one(msg.value, consumer)
            except Exception as exc:
                logger.exception("Unhandled error, skipping message: %s", exc)
    finally:
        await consumer.stop()
        logger.info("processing-service stopped")


if __name__ == "__main__":
    asyncio.run(main())
