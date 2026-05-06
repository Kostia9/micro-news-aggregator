from fastapi import APIRouter, Query

from app.db.mongo import list_articles
from app.schemas.feed import ArticleSummary, FeedResponse

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("", response_model=FeedResponse)
async def get_feed(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    topic: str | None = None,
) -> FeedResponse:
    rows, total = await list_articles(page=page, page_size=page_size, topic=topic)
    return FeedResponse(
        articles=[ArticleSummary(**row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )
