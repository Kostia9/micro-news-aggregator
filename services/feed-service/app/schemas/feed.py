from pydantic import BaseModel
from datetime import datetime


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


class SearchRequest(BaseModel):
    query: str
    topics: list[str] = []
    page: int = 1
    page_size: int = 20
