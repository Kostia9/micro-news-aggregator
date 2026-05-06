from datetime import datetime

from pydantic import BaseModel


class ArticleSummary(BaseModel):
    id: str
    title: str
    url: str
    source: str
    topics: list[str]
    summary: str | None
    published_at: datetime


class FeedResponse(BaseModel):
    articles: list[ArticleSummary]
    total: int
    page: int
    page_size: int
