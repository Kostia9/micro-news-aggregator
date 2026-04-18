from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_uri: str = "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0"
    mongo_db: str = "news"
    redis_url: str = "redis://redis:6379"
    feed_cache_ttl_seconds: int = 120
    elasticsearch_url: str = "http://elasticsearch:9200"


settings = Settings()
