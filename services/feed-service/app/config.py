from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_processed: str = "articles.processed"
    kafka_consumer_group: str = "feed-service"
    kafka_startup_retries: int = 30
    kafka_startup_retry_delay_seconds: float = 1.0
    mongo_uri: str = "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0"
    mongo_db: str = "feed"


settings = Settings()
