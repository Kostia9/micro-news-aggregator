from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str
    gemini_model: str = "gemini-3-flash-preview"
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_processed: str = "articles.processed"
    kafka_topic_summarized: str = "articles.summarized"
    kafka_consumer_group: str = "llm-service"


settings = Settings()
