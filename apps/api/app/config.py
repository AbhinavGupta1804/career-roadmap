from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Career Roadmap API"
    debug: bool = False
    api_prefix: str = "/api"

    # CORS — comma-separated origins in .env, e.g. http://localhost:3000
    cors_origins: str = "http://localhost:3000"

    # Supabase (optional until you wire a project)
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None

    # Anthropic
    anthropic_api_key: str | None = None
    agent_mock_mode: bool = False
    usd_to_inr: float = 84.0

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.cors_origins.strip():
            return ["http://localhost:3000"]
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_role_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
