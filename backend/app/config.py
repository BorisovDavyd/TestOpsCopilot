import os
from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    api_v1_prefix: str = "/api"
    cloudru_api_key: str = Field(default="", env="CLOUDRU_API_KEY")
    cloudru_base_url: str = Field(
        default="https://foundation-models.api.cloud.ru", env="CLOUDRU_BASE_URL"
    )
    model_default: str = Field(default="gpt-lite", env="CLOUDRU_MODEL")
    request_timeout: int = Field(default=30, env="CLOUDRU_TIMEOUT")
    retries: int = Field(default=2, env="CLOUDRU_RETRIES")
    data_path: str = Field(default="/workspace/TestOpsCopilot/data", env="DATA_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
