import logging
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

_http_client: httpx.AsyncClient | None = None


def init_http_client(llm_service_url: str) -> None:
    global _http_client
    _http_client = httpx.AsyncClient(base_url=llm_service_url, timeout=10.0)


async def close_http_client() -> None:
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


async def enrich(article: dict) -> dict:
    article["processed_at"] = datetime.now(timezone.utc)
    article["word_count"] = len(article.get("content", "").split())
    return article
