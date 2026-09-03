from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CyberLey API"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_reload: bool = False

    frontend_origins: str = "http://localhost:5173"

    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_service_role_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.frontend_origins.split(",")
            if origin.strip()
        ]

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"

    @property
    def frontend_origin_regex(self) -> str | None:
        """Allow Vite's fallback ports only while developing locally."""
        if not self.is_development:
            return None
        return r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
