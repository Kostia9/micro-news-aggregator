from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_dsn: str = "postgresql+asyncpg://user:pass@postgres:5432/auth"
    redis_url: str = "redis://redis:6379"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_ttl_seconds: int = 3600


settings = Settings()
