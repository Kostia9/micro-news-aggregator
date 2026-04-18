from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


def init_mongo(uri: str, db_name: str) -> None:
    global client, db
    pass


async def save_article(article: dict) -> str:
    pass
