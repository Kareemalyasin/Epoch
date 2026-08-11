"""Single source of truth for application configuration and secrets."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    resend_api_key: str
    cron_secret: str
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
