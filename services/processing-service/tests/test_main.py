import asyncio

import app.main as processing
from pymongo.errors import DuplicateKeyError


class FakeConsumer:
    def __init__(self) -> None:
        self.produced: list[dict] = []
        self.committed = False

    async def produce(self, article: dict) -> None:
        self.produced.append(article)

    async def commit(self) -> None:
        self.committed = True


def test_process_one_skips_invalid_raw_message() -> None:
    consumer = FakeConsumer()

    asyncio.run(processing.process_one({"title": "Missing fields"}, consumer))

    assert consumer.produced == []
    assert consumer.committed is False


def test_process_one_merges_topics_and_publishes_url(monkeypatch) -> None:
    saved = {}
    marked = []

    async def is_published(url: str) -> bool:
        return False

    async def assign_topics(article: dict) -> list[str]:
        return ["business"]

    async def save_article(article: dict) -> str:
        saved.update(article)
        return "article-1"

    async def mark_published(article_id: str) -> None:
        marked.append(article_id)

    monkeypatch.setattr(processing, "is_published", is_published)
    monkeypatch.setattr(processing, "assign_topics", assign_topics)
    monkeypatch.setattr(processing, "save_article", save_article)
    monkeypatch.setattr(processing, "mark_published", mark_published)

    consumer = FakeConsumer()
    raw = {
        "title": "Market AI story",
        "url": "https://example.com/story",
        "source": "Example",
        "content": "Business article content",
        "published_at": "2026-04-19T12:30:00+00:00",
        "topics": ["technology"],
    }

    asyncio.run(processing.process_one(raw, consumer))

    assert saved["topics"] == ["technology", "business"]
    assert consumer.produced == [
        {
            "article_id": "article-1",
            "title": "Market AI story",
            "url": "https://example.com/story",
            "content": "Business article content",
            "source": "Example",
            "topics": ["technology", "business"],
            "published_at": "2026-04-19T12:30:00+00:00",
        }
    ]
    assert marked == ["article-1"]
    assert consumer.committed is True


def test_process_one_skips_already_published_duplicate(monkeypatch) -> None:
    async def is_published(url: str) -> bool:
        return True

    monkeypatch.setattr(processing, "is_published", is_published)
    consumer = FakeConsumer()

    asyncio.run(
        processing.process_one(
            {
                "title": "Duplicate",
                "url": "https://example.com/duplicate",
                "source": "Example",
                "content": "Duplicate content",
            },
            consumer,
        )
    )

    assert consumer.produced == []
    assert consumer.committed is False


def test_process_one_republishes_unpublished_duplicate(monkeypatch) -> None:
    marked = []

    async def is_published(url: str) -> bool:
        return False

    async def save_article(article: dict) -> str:
        raise DuplicateKeyError("duplicate")

    async def get_article_id_by_url(url: str) -> str:
        return "existing-id"

    async def mark_published(article_id: str) -> None:
        marked.append(article_id)

    monkeypatch.setattr(processing, "is_published", is_published)
    monkeypatch.setattr(processing, "save_article", save_article)
    monkeypatch.setattr(processing, "get_article_id_by_url", get_article_id_by_url)
    monkeypatch.setattr(processing, "mark_published", mark_published)

    consumer = FakeConsumer()
    asyncio.run(
        processing.process_one(
            {
                "title": "Unpublished duplicate",
                "url": "https://example.com/unpublished",
                "source": "Example",
                "content": "Content",
                "topics": ["general"],
            },
            consumer,
        )
    )

    assert consumer.produced[0]["article_id"] == "existing-id"
    assert consumer.produced[0]["url"] == "https://example.com/unpublished"
    assert marked == ["existing-id"]
    assert consumer.committed is True
