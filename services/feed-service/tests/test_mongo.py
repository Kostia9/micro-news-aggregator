import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

import app.db.mongo as mongo
import pytest


class FakeCursor:
    def __init__(self, docs: list[dict]) -> None:
        self.docs = docs
        self.sort_args = None
        self.skip_value = None
        self.limit_value = None

    def sort(self, *args):
        self.sort_args = args
        return self

    def skip(self, value: int):
        self.skip_value = value
        return self

    def limit(self, value: int):
        self.limit_value = value
        return self

    def __aiter__(self):
        self._iter = iter(self.docs)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


class FakeArticles:
    def __init__(self) -> None:
        self.updates = []
        self.query = None
        self.cursor = FakeCursor(
            [
                {
                    "article_id": "article-1",
                    "title": "Story",
                    "url": "https://example.com/story",
                    "source": "Example",
                    "topics": ["technology"],
                    "summary": None,
                    "published_at": datetime(2026, 4, 19, tzinfo=timezone.utc),
                }
            ]
        )

    async def update_one(self, *args, **kwargs) -> None:
        self.updates.append((args, kwargs))

    async def count_documents(self, query: dict) -> int:
        self.query = query
        return 1

    def find(self, query: dict, projection: dict):
        self.query = query
        return self.cursor


@pytest.fixture()
def fake_articles(monkeypatch) -> FakeArticles:
    articles = FakeArticles()
    monkeypatch.setattr(mongo, "db", SimpleNamespace(articles=articles))
    return articles


def test_upsert_article_stores_processed_projection(fake_articles: FakeArticles) -> None:
    asyncio.run(
        mongo.upsert_article(
            {
                "article_id": "article-1",
                "title": "Story",
                "url": "https://example.com/story",
                "source": "Example",
                "topics": ["technology"],
                "summary": None,
                "published_at": "2026-04-19T12:30:00+00:00",
            }
        )
    )

    args, kwargs = fake_articles.updates[0]
    assert args[0] == {"article_id": "article-1"}
    assert args[1]["$set"]["url"] == "https://example.com/story"
    assert args[1]["$set"]["topics"] == ["technology"]
    assert args[1]["$set"]["published_at"] == datetime(
        2026, 4, 19, 12, 30, tzinfo=timezone.utc
    )
    assert kwargs == {"upsert": True}


def test_list_articles_paginates_and_filters_by_topic(fake_articles: FakeArticles) -> None:
    rows, total = asyncio.run(
        mongo.list_articles(page=2, page_size=10, topic="technology")
    )

    assert total == 1
    assert fake_articles.query == {"topics": "technology"}
    assert fake_articles.cursor.sort_args == ("published_at", -1)
    assert fake_articles.cursor.skip_value == 10
    assert fake_articles.cursor.limit_value == 10
    assert rows[0]["id"] == "article-1"
    assert "article_id" not in rows[0]
