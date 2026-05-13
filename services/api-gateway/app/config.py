from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    auth_service_url: str = "http://auth-lb"
    feed_service_url: str = "http://feed-service:8000"
    redis_url: str = "redis://redis:6379"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    redis_startup_retries: int = 30
    redis_startup_retry_delay_seconds: float = 1.0


settings = Settings()
