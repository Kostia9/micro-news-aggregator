import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from dataclasses import asdict

from fastapi import FastAPI

from app.config import settings
from app.fetcher.rss import RSSFetcher
from app.parser.feed import parse_feed
from app.producer.kafka import ArticleProducer
from app.routes.admin import router as admin_router
from app.sources import RSS_SOURCES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


async def ingest_sources(
    fetcher: RSSFetcher,
    producer: ArticleProducer,
    seen_urls: set[str],
) -> int:
    published = 0

    for source in RSS_SOURCES:
        name = source["name"]
        url = source["url"]
        topics = list(source.get("topics", []))
        try:
            raw_xml = await fetcher.fetch(url)
            articles = parse_feed(raw_xml, source_name=name, source_topics=topics)
            source_published = 0
            for article in articles:
                if article.url in seen_urls:
                    continue
                await producer.send(asdict(article))
                seen_urls.add(article.url)
                published += 1
                source_published += 1
            logger.info("Published %s new articles from %s", source_published, name)
        except Exception:
            logger.exception("Failed to ingest source %s (%s)", name, url)

    return published


async def start_producer_with_retry(producer: ArticleProducer) -> None:
    for attempt in range(1, settings.kafka_startup_retries + 1):
        try:
            await producer.start()
            return
        except Exception:
            if attempt == settings.kafka_startup_retries:
                logger.exception("Kafka producer did not start after %s attempts", attempt)
                raise
            logger.warning(
                "Kafka producer not ready (attempt %s/%s), retrying in %.1fs",
                attempt,
                settings.kafka_startup_retries,
                settings.kafka_startup_retry_delay_seconds,
            )
            await asyncio.sleep(settings.kafka_startup_retry_delay_seconds)


async def poll_sources(
    fetcher: RSSFetcher,
    producer: ArticleProducer,
    seen_urls: set[str],
    stop_event: asyncio.Event,
) -> None:
    while not stop_event.is_set():
        await ingest_sources(fetcher, producer, seen_urls)

        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(
                stop_event.wait(), timeout=settings.fetch_interval_seconds
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    fetcher = RSSFetcher()
    producer = ArticleProducer()
    seen_urls: set[str] = set()
    stop_event = asyncio.Event()
    poll_task: asyncio.Task[None] | None = None

    try:
        await start_producer_with_retry(producer)
        poll_task = asyncio.create_task(
            poll_sources(fetcher, producer, seen_urls, stop_event)
        )
        yield
    finally:
        stop_event.set()
        if poll_task is not None:
            poll_task.cancel()
            with suppress(asyncio.CancelledError):
                await poll_task
        await fetcher.close()
        await producer.stop()


app = FastAPI(title="Ingestion Service", lifespan=lifespan)
app.include_router(admin_router)
