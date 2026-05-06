from datetime import datetime, timezone


async def enrich(article: dict) -> dict:
    article["processed_at"] = datetime.now(timezone.utc)
    article["word_count"] = len(article.get("content", "").split())
    return article
