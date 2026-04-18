from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_raw: str = "articles.raw"
    fetch_interval_seconds: int = 300


settings = Settings()
