from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    API_SECRET_KEY: str
    TOKEN_BUCKET_CAPACITY: int = 10
    TOKEN_BUCKET_REFILL_RATE: float = 1.0 # tokens per second

    CACHE_TTL_SECONDS: int = 300 # 5 minute cache

    class Config:
        env_file = ".env"

settings = Settings()