from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from env vars / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    database_url: str = Field(
        default="postgresql+asyncpg://career:career@localhost:5432/careerdb",
        alias="DATABASE_URL",
    )

    # AI provider: Pollinations.ai (free, OpenAI-compatible, no API key required).
    # See https://pollinations.ai — the `openai` model alias resolves to a free
    # open-source LLM (currently gpt-oss-20b on the anonymous tier).
    pollinations_url: str = Field(
        default="https://text.pollinations.ai/openai",
        alias="POLLINATIONS_URL",
    )
    pollinations_model: str = Field(default="openai", alias="POLLINATIONS_MODEL")
    pollinations_timeout: float = Field(default=300.0, alias="POLLINATIONS_TIMEOUT")
    pollinations_referer: str = Field(
        default="career-guidance-kz",
        alias="POLLINATIONS_REFERER",
    )

    secret_key: str = Field(default="dev-secret", alias="SECRET_KEY")
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost,http://localhost:80",
        alias="CORS_ORIGINS",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
