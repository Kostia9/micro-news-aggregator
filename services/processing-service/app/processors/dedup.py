from app.db.mongo import is_published


async def is_duplicate(url: str) -> bool:
    return await is_published(url)
