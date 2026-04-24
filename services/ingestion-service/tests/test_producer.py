import asyncio
import json

import pytest

from app.config import settings
from app.producer.kafka import ArticleProducer


class FakeAIOKafkaProducer:
    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.sent = []
        self.started = False
        self.stopped = False
        self.__class__.instances.append(self)

    async def start(self) -> None:
        self.started = True

    async def send_and_wait(self, topic: str, value: dict) -> None:
        self.sent.append((topic, value))

    async def stop(self) -> None:
        self.stopped = True


def test_article_producer_serializes_and_sends_to_raw_topic(monkeypatch) -> None:
    FakeAIOKafkaProducer.instances = []
    monkeypatch.setattr("app.producer.kafka.AIOKafkaProducer", FakeAIOKafkaProducer)

    async def run() -> FakeAIOKafkaProducer:
        producer = ArticleProducer()
        await producer.start()
        await producer.send({"title": "Story", "url": "https://example.com/story"})
        await producer.stop()
        return FakeAIOKafkaProducer.instances[0]

    fake = asyncio.run(run())

    assert fake.started is True
    assert fake.stopped is True
    assert fake.kwargs["bootstrap_servers"] == settings.kafka_bootstrap_servers
    assert json.loads(fake.kwargs["value_serializer"]({"title": "Story"}).decode()) == {
        "title": "Story"
    }
    assert fake.sent == [
        (settings.kafka_topic_raw, {"title": "Story", "url": "https://example.com/story"})
    ]


def test_article_producer_raises_if_send_before_start() -> None:
    async def run() -> None:
        producer = ArticleProducer()
        with pytest.raises(RuntimeError, match="Call start"):
            await producer.send({"title": "Story"})

    asyncio.run(run())
