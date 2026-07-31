from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Setări de mediu centralizate gestionate prin Pydantic."""
    
    APP_NAME: str = "MetaEcosystemSuite"
    DEBUG: bool = False
    
    # Meta Graph & Marketing API Credentials
    META_APP_ID: str = Field(default="", env="META_APP_ID")
    META_APP_SECRET: str = Field(default="", env="META_APP_SECRET")
    META_ACCESS_TOKEN: str = Field(default="", env="META_ACCESS_TOKEN")
    META_GRAPH_VERSION: str = "v19.0"
    
    # Notifications & Webhooks
    SLACK_WEBHOOK_URL: str = Field(default="", env="SLACK_WEBHOOK_URL")
    ALERT_EMAIL: str = Field(default="", env="ALERT_EMAIL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
