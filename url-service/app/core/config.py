from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/urlshortener"
    REDIS_URL: str = "redis://redis:6379"
    SQS_QUEUE_URL: str = "http://localstack:4566/000000000000/click-events"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_DEFAULT_REGION: str = "us-east-1"
    AWS_ENDPOINT_URL: str = "http://localstack:4566"
    BASE_URL: str = "http://localhost:8000"
    CACHE_TTL_SECONDS: int = 3600

    class Config:
        env_file = ".env"

settings = Settings()
