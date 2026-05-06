from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    auth_service_url: str = "http://auth-lb"
    feed_service_url: str = "http://feed-service:8000"
    redis_url: str = "redis://redis:6379"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"


settings = Settings()
