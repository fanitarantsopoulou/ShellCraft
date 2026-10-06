from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    env: Literal["development", "test", "production"] = "development"
    secret_key: str = Field(min_length=16)
    database_url: str = "postgresql+psycopg://linuxlearn:linuxlearn@db:5432/linuxlearn"
    content_dir: str = "/content"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # values come from the environment
