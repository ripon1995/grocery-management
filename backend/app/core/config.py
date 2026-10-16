from typing import Literal
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    LOG_LEVEL: str
    ENVIRONMENT: str
    SHOW_SQL_LOG: bool = False
    # DB configs
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    # DB pool configs
    POOL_SIZE: int   # connection that can be taken at a moment
    MAX_OVERFLOW: int # extra connection count even after pool size is full
    POOL_TIMEOUT: int # time after trying to pool connection will be canceled
    POOL_RECYCLE: int

    # REDIS config
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_TTL: int

    # Default to localhost for safety, but allow override via .env
    ALLOW_ORIGINS: list[str] = ["http://localhost:5173"]

    # JWT token settings
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 24 * 60

    # GEMINI CONFIG
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = 'gemini-flash-latest'
    GEMINI_PROVIDER: Literal['real', 'fake'] = 'real'

    # FAKE GEMINI (GEMINI_PROVIDER=fake), see app/clients/fake_gemini_client.py
    FAKE_GEMINI_LATENCY_S: float = 2.0
    FAKE_GEMINI_RPM: int = 0  # 0 = no limit
    FAKE_GEMINI_FAIL_RATE: float = 0.0

    # RABBITMQ config
    RABBIT_MQ_CONNECTION_URL: str

    model_config = SettingsConfigDict(
        env_file=('.env', 'backend/.env'),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?prepared_statement_cache_size=0"
        )


settings = Settings()
