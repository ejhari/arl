"""Application configuration"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "ARL API"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://arl_user:arl_dev_password@localhost:5432/arl_dev"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # LLM Configuration (supports multiple providers)
    # Provider options: "anthropic", "google", "azure", "bedrock", "openai"
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = "claude-sonnet-4-20250514"
    LLM_MAX_TOKENS: int = 4096

    # Anthropic (native ADK support)
    ANTHROPIC_API_KEY: Optional[str] = None

    # Google/Gemini (native ADK support)
    GOOGLE_API_KEY: Optional[str] = None

    # Azure OpenAI (via ADK LiteLLM)
    AZURE_API_KEY: Optional[str] = None
    AZURE_API_BASE: Optional[str] = None
    AZURE_API_VERSION: str = "2024-02-15-preview"

    # AWS Bedrock (via ADK LiteLLM)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION_NAME: str = "us-east-1"

    # OpenAI (via ADK's built-in LiteLLM)
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
