from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration.

    Secrets and environment-specific configuration are loaded
    from environment variables rather than hardcoded in code.
    """

    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = "auto"

    gsc_site_url: str = ""
    gsc_credentials_path: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def gsc_credentials_file(self) -> Path:
        return Path(self.gsc_credentials_path)


settings = Settings()