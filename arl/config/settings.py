"""Global application settings."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "ARL"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Deployment
    deployment_mode: Literal["local", "cloud", "hybrid"] = "local"

    # Storage
    data_dir: Path = Path("./data")
    projects_dir: Path = Path("./data/projects")
    artifacts_dir: Path = Path("./data/artifacts")

    # Database
    database_url: str = "sqlite:///./data/arl.db"

    # LLM Providers
    default_llm_provider: str = "google"
    llm_provider: str | None = None  # Alternative naming for default_llm_provider

    @property
    def provider(self) -> str:
        """Get LLM provider from any naming convention."""
        return (self.llm_provider or self.default_llm_provider).lower()

    google_api_key: str | None = None

    # Azure OpenAI
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment_name: str | None = None

    anthropic_api_key: str | None = None

    # External APIs
    arxiv_api_enabled: bool = True
    pubmed_api_key: str | None = None

    # Execution
    docker_enabled: bool = True
    max_concurrent_experiments: int = 3
    experiment_timeout_seconds: int = 600

    # Memory
    memory_backend: Literal["local", "vertex"] = "local"
    vertex_project_id: str | None = None
    vertex_location: str = "us-central1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
