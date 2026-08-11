from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    LOG_LEVEL: str
    ENVIRONMENT: str
    SHOW_SQL_LOG: bool = False
    # Default to localhost for safety, but allow override via .env
    ALLOW_ORIGINS: list[str] = ["http://localhost:5173"]

    # JWT token settings
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 24 * 60

    model_config = SettingsConfigDict(
        env_file=('.env', 'backend/.env'),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )


settings = Settings()
