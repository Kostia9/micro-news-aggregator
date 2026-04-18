from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_raw: str = "articles.raw"
    kafka_topic_processed: str = "articles.processed"
    kafka_consumer_group: str = "processing-service"
    mongo_uri: str = "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0"
    mongo_db: str = "news"
    llm_service_url: str = "http://llm-service:8000"


settings = Settings()
