"""GRIP application configuration. Loads from .env file."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://grip:grip_dev@localhost:5432/grip"
    demo_mode: bool = True
    entsoe_api_key: str = ""
    gdelt_project_id: str = ""
    copernicus_api_key: str = ""
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
