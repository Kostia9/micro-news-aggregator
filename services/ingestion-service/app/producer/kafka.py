import json
import logging

from aiokafka import AIOKafkaProducer

from app.config import settings

logger = logging.getLogger(__name__)


class ArticleProducer:
    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )
        await self._producer.start()
        logger.info("ArticleProducer started")

    async def send(self, article: dict) -> None:
        if self._producer is None:
            raise RuntimeError("Call start() before send()")
        key = str(article["url"]).encode("utf-8")
        await self._producer.send_and_wait(
            settings.kafka_topic_raw,
            key=key,
            value=article,
        )

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None
        logger.info("ArticleProducer stopped")
