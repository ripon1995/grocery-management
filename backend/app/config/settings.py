from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGODB_URL: str
    MONGODB_DB_NAME: str

    model_config = SettingsConfigDict(
        env_file='backend/.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
    )


settings = Settings()
