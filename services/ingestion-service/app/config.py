from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_raw: str = "articles.raw"
    fetch_interval_seconds: int = 300
    kafka_startup_retries: int = 30
    kafka_startup_retry_delay_seconds: float = 1.0
    mongo_uri: str = "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0"
    ingestion_mongo_db: str = "ingestion"


settings = Settings()
