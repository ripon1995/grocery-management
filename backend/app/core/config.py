from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    LOG_LEVEL: str
    ENVIRONMENT: str
    model_config = SettingsConfigDict(
        env_file='backend/.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )


settings = Settings()
