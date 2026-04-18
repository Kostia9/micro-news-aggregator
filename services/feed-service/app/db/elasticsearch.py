from elasticsearch import AsyncElasticsearch

client: AsyncElasticsearch | None = None


def init_es(url: str) -> None:
    global client
    pass
