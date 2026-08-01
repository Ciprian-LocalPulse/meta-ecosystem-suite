"""Centralized environment configuration via Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings, loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "MetaEcosystemSuite"
    DEBUG: bool = False

    # Meta Graph & Marketing API credentials
    META_APP_ID: str = Field(default="")
    META_APP_SECRET: str = Field(default="")
    META_ACCESS_TOKEN: str = Field(default="")
    META_GRAPH_VERSION: str = Field(default="v19.0")

    # TikTok Commercial Content API (Research API v2) credentials.
    # Unlike Meta, TikTok's client access token goes in an Authorization
    # header, not a query param — see platforms/tiktok/client.py.
    TIKTOK_CLIENT_KEY: str = Field(default="")
    TIKTOK_CLIENT_SECRET: str = Field(default="")
    TIKTOK_ACCESS_TOKEN: str = Field(default="")

    # Notifications & webhooks
    SLACK_WEBHOOK_URL: str = Field(default="")
    ALERT_EMAIL: str = Field(default="")

    @property
    def graph_base_url(self) -> str:
        return f"https://graph.facebook.com/{self.META_GRAPH_VERSION}"


settings = Settings()
