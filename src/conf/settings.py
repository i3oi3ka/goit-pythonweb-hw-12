"""
Configuration settings for the FastAPI application using Pydantic BaseSettings.

Loads environment variables from .env file and provides default values for local development and documentation builds.
"""

from pydantic import EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from redis import Redis
from redis_lru import RedisLRU


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """

    DB_URL: str = "sqlite+aiosqlite:///./test.db"
    JWT_SECRET: str = "your_jwt_secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXP_MIN: int = 60

    MAIL_USERNAME: EmailStr = "example@meta.ua"
    MAIL_PASSWORD: SecretStr = SecretStr("secretPassword")
    MAIL_FROM: EmailStr = "example@meta.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    MAIL_FROM_NAME: str = "Rest API HW10"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLD_NAME: str = "your_cloud_name"
    CLD_API_KEY: int = 123456789
    CLD_API_SECRET: str = "your_cloud_api_secret"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()


redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=None)
redis_cache = RedisLRU(redis_client)
