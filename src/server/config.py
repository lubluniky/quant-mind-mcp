"""Server configuration management."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment
    environment: Literal["development", "production"] = "development"

    # Database
    database_url: str = "sqlite+aiosqlite:///./quantmind.db"

    # Alpha Vault
    alpha_vault_min_sharpe: float = 1.5
    alpha_vault_min_trades: int = 100

    # Paths
    research_papers_path: Path = Path(__file__).parent.parent.parent / "assets" / "research_papers"
    prompts_path: Path = Path(__file__).parent.parent.parent / "assets" / "prompts"
    alpha_vault_path: Path = Path(__file__).parent.parent.parent / "data" / "alpha_vault"

    # Logging
    log_level: str = "INFO"


settings = Settings()
