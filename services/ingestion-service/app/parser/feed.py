from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import struct_time

import feedparser


@dataclass
class RawArticle:
    title: str
    url: str
    published_at: str
    content: str
    source: str
    topics: list[str] = field(default_factory=list)


def parse_feed(
    raw_xml: bytes,
    source_name: str,
    source_topics: list[str] | None = None,
) -> list[RawArticle]:
    parsed = feedparser.parse(raw_xml)
    articles: list[RawArticle] = []
    topics = list(source_topics or [])

    for entry in parsed.entries:
        title = _clean(entry.get("title"))
        url = _clean(entry.get("link") or entry.get("id"))
        if not title or not url:
            continue

        articles.append(
            RawArticle(
                title=title,
                url=url,
                published_at=_published_at(entry),
                content=_content(entry),
                source=source_name,
                topics=topics,
            )
        )

    return articles


def _clean(value: object) -> str:
    return str(value).strip() if value is not None else ""


def _content(entry: dict) -> str:
    content = entry.get("content")
    if content:
        first = content[0]
        value = first.get("value") if hasattr(first, "get") else None
        cleaned = _clean(value)
        if cleaned:
            return cleaned

    for attr in ("summary", "description"):
        cleaned = _clean(entry.get(attr))
        if cleaned:
            return cleaned

    return ""


def _published_at(entry: dict) -> str:
    for field in ("published_parsed", "updated_parsed", "created_parsed"):
        parsed = entry.get(field)
        if isinstance(parsed, struct_time):
            return datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()

    return ""
