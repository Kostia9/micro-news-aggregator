import asyncio

import app.main as main
from app.main import ingest_sources, start_producer_with_retry

RSS_XML = b"""
<rss version="2.0">
  <channel>
    <item>
      <title>Story</title>
      <link>https://example.com/story</link>
      <description>Story body</description>
    </item>
  </channel>
</rss>
"""


class FakeFetcher:
    async def fetch(self, url: str) -> bytes:
        return RSS_XML


class FakeProducer:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def send(self, article: dict) -> None:
        self.sent.append(article)


def test_ingest_sources_adds_topics_and_skips_seen_urls(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.main.RSS_SOURCES",
        [
            {
                "name": "Example",
                "url": "https://example.com/rss.xml",
                "topics": ["technology"],
            }
        ],
    )
    fetcher = FakeFetcher()
    producer = FakeProducer()
    seen_urls: set[str] = set()

    first_count = asyncio.run(ingest_sources(fetcher, producer, seen_urls))
    second_count = asyncio.run(ingest_sources(fetcher, producer, seen_urls))

    assert first_count == 1
    assert second_count == 0
    assert producer.sent == [
        {
            "title": "Story",
            "url": "https://example.com/story",
            "published_at": "",
            "content": "Story body",
            "source": "Example",
            "topics": ["technology"],
        }
    ]
    assert seen_urls == {"https://example.com/story"}


def test_start_producer_with_retry_retries_until_success(monkeypatch) -> None:
    class FlakyProducer:
        def __init__(self) -> None:
            self.attempts = 0

        async def start(self) -> None:
            self.attempts += 1
            if self.attempts < 3:
                raise RuntimeError("kafka unavailable")

    sleep_delays = []

    async def fake_sleep(delay: float) -> None:
        sleep_delays.append(delay)

    monkeypatch.setattr(main.settings, "kafka_startup_retries", 3)
    monkeypatch.setattr(main.settings, "kafka_startup_retry_delay_seconds", 0.5)
    monkeypatch.setattr("app.main.asyncio.sleep", fake_sleep)

    producer = FlakyProducer()

    asyncio.run(start_producer_with_retry(producer))

    assert producer.attempts == 3
    assert sleep_delays == [0.5, 0.5]
