from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    auth_service_url: str = "http://auth-service:8000"
    feed_service_url: str = "http://feed-service:8000"
    llm_service_url: str = "http://llm-service:8000"
    redis_url: str = "redis://redis:6379"
    jwt_secret: str = "change-me"


settings = Settings()
