import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from app.config import settings
from app.consumer.kafka import ProcessedArticleConsumer
from app.db.mongo import ensure_indexes, init_mongo, upsert_article, wait_for_mongo
from app.routes.feed import router as feed_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


async def consume_processed_articles(consumer: ProcessedArticleConsumer) -> None:
    async for msg in consumer:
        try:
            await upsert_article(msg.value)
            await consumer.commit()
            logger.info("Stored feed projection for %s", msg.value.get("article_id"))
        except Exception:
            logger.exception("Failed to store processed article")


async def start_consumer_with_retry(consumer: ProcessedArticleConsumer) -> None:
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_mongo(settings.mongo_uri, settings.mongo_db)
    await wait_for_mongo(
        settings.mongo_startup_retries,
        settings.mongo_startup_retry_delay_seconds,
    )
    await ensure_indexes()

    consumer = ProcessedArticleConsumer()
    consume_task: asyncio.Task[None] | None = None
    try:
        await start_consumer_with_retry(consumer)
        consume_task = asyncio.create_task(consume_processed_articles(consumer))
        yield
    finally:
        if consume_task is not None:
            consume_task.cancel()
            with suppress(asyncio.CancelledError):
                await consume_task
        await consumer.stop()


app = FastAPI(title="Feed Service", lifespan=lifespan)
app.include_router(feed_router)
