from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine


class Settings(BaseSettings):
    APP_NAME: str = "Delay Gateway"
    JWT_SECRET: str = "f0862b861790236fd3d4b8bb058e93e9"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_SECONDS: int = 60*60*24  # 24h

    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"

    # For push notifications (placeholders)
    FCM_SERVER_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()

# Тепер engine створюємо вже з settings.DATABASE_URL
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)