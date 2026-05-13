import json
import logging
from collections.abc import AsyncIterator

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.structs import ConsumerRecord

from app.config import settings

logger = logging.getLogger(__name__)


class ArticleConsumer:
    def __init__(self) -> None:
        self._consumer: AIOKafkaConsumer | None = None
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            settings.kafka_topic_raw,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_consumer_group,
            value_deserializer=lambda b: json.loads(b.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        )
        await self._consumer.start()
        await self._producer.start()
        logger.info("ArticleConsumer started")

    async def produce(self, article: dict) -> None:
        if self._producer is None:
            raise RuntimeError("Call start() before produce()")
        key = str(article["article_id"]).encode("utf-8")
        await self._producer.send_and_wait(
            settings.kafka_topic_processed,
            key=key,
            value=article,
        )

    async def commit(self) -> None:
        if self._consumer is None:
            raise RuntimeError("Call start() before commit()")
        await self._consumer.commit()

    async def stop(self) -> None:
        if self._consumer:
            await self._consumer.stop()
        if self._producer:
            await self._producer.stop()
        logger.info("ArticleConsumer stopped")

    def __aiter__(self) -> AsyncIterator[ConsumerRecord]:
        if self._consumer is None:
            raise RuntimeError("Call start() before iterating")
        return self._consumer.__aiter__()
