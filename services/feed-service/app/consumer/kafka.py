import json
import logging
from collections.abc import AsyncIterator

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import ConsumerRecord

from app.config import settings

logger = logging.getLogger(__name__)


class ProcessedArticleConsumer:
    def __init__(self) -> None:
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            settings.kafka_topic_processed,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_consumer_group,
            value_deserializer=lambda b: json.loads(b.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        await self._consumer.start()
        logger.info("ProcessedArticleConsumer started")

    async def commit(self) -> None:
        if self._consumer is None:
            raise RuntimeError("Call start() before commit()")
        await self._consumer.commit()

    async def stop(self) -> None:
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None
        logger.info("ProcessedArticleConsumer stopped")

    def __aiter__(self) -> AsyncIterator[ConsumerRecord]:
        if self._consumer is None:
            raise RuntimeError("Call start() before iterating")
        return self._consumer.__aiter__()
