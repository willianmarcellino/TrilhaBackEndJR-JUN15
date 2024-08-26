from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )
    DATABASE_URL: str
    ACCESS_TOKEN_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_KEY: str
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    TOKEN_ALGORITHM: str
