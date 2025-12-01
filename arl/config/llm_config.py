"""LLM provider configuration.

Azure OpenAI Model Format:
    For Azure OpenAI, use the format: azure/<deployment-name>
    Example: "azure/gpt-4" where "gpt-4" is your deployment name in Azure

    Set these environment variables:
    - AZURE_OPENAI_API_KEY: Your Azure OpenAI API key
    - AZURE_OPENAI_ENDPOINT: Your endpoint (e.g., https://your-resource.openai.azure.com)
    - AZURE_OPENAI_API_VERSION: API version (default: 2024-02-15-preview)
    - AZURE_OPENAI_DEPLOYMENT_NAME: Your deployment name (e.g., "gpt-4", "gpt-35-turbo")
"""

from typing import Literal

from pydantic import BaseModel, Field

from arl.config.settings import settings


class LLMConfig(BaseModel):
    """Configuration for LLM provider and model selection."""

    provider: Literal["google", "azure", "anthropic", "ollama"] = "google"
    model: str = Field(default="gemini/gemini-2.0-flash-exp")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=8192, gt=0)
    timeout_seconds: int = Field(default=60, gt=0)

    # Agent-specific overrides
    orchestrator_model: str | None = None
    hypothesis_model: str | None = None
    code_gen_model: str | None = None
    analysis_model: str | None = None

    def get_model_for_agent(self, agent_type: str) -> str:
        """Get the appropriate model for a specific agent type."""
        override_map = {
            "orchestrator": self.orchestrator_model,
            "hypothesis": self.hypothesis_model,
            "code_gen": self.code_gen_model,
            "analysis": self.analysis_model,
        }
        return override_map.get(agent_type) or self.model


# Helper functions (defined first to avoid circular dependencies)
def get_azure_config(
    deployment_name: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 8192,
) -> LLMConfig:
    """
    Create Azure OpenAI configuration.

    Args:
        deployment_name: Azure deployment name. If None, uses AZURE_OPENAI_DEPLOYMENT_NAME env var
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response

    Returns:
        LLMConfig configured for Azure OpenAI

    Example:
        # Use environment variable
        config = get_azure_config()

        # Or specify deployment explicitly
        config = get_azure_config(deployment_name="my-gpt4-deployment")
    """
    deployment = deployment_name or settings.azure_openai_deployment_name or "gpt-4"
    return LLMConfig(
        provider="azure",
        model=f"azure/{deployment}",
        temperature=temperature,
        max_tokens=max_tokens,
    )


# Default LLM configurations - respect environment variable
if settings.provider == "azure":
    DEFAULT_LLM_CONFIG = get_azure_config(temperature=0.7, max_tokens=8192)
    FAST_LLM_CONFIG = get_azure_config(temperature=0.3, max_tokens=4096)
elif settings.provider == "anthropic":
    DEFAULT_LLM_CONFIG = LLMConfig(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        temperature=0.7,
        max_tokens=8192,
    )
    FAST_LLM_CONFIG = LLMConfig(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        temperature=0.3,
        max_tokens=4096,
    )
else:
    # Default to Google Gemini
    DEFAULT_LLM_CONFIG = LLMConfig(
        model="gemini/gemini-2.0-flash-exp"
    )
    FAST_LLM_CONFIG = LLMConfig(
        model="gemini/gemini-2.0-flash-exp",
        temperature=0.3,
        max_tokens=4096,
    )

# Powerful model for complex reasoning
# Respects DEFAULT_LLM_PROVIDER or LLM_PROVIDER environment variable
if settings.provider == "azure":
    POWERFUL_LLM_CONFIG = get_azure_config(temperature=0.7, max_tokens=8192)
elif settings.provider == "anthropic":
    POWERFUL_LLM_CONFIG = LLMConfig(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        temperature=0.7,
        max_tokens=8192,
    )
else:
    # Default to Google Gemini
    POWERFUL_LLM_CONFIG = LLMConfig(
        model="gemini/gemini-exp-1206",
        temperature=0.7,
        max_tokens=8192,
    )

# Azure OpenAI configuration
# Uses environment variable AZURE_OPENAI_DEPLOYMENT_NAME if set
# Set AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name in .env
_azure_deployment = settings.azure_openai_deployment_name or "gpt-4"
AZURE_GPT4_CONFIG = LLMConfig(
    provider="azure",
    model=f"azure/{_azure_deployment}",
    temperature=0.7,
    max_tokens=8192,
)


# Auto-select config based on default provider
def get_default_config() -> LLMConfig:
    """
    Get default LLM config based on DEFAULT_LLM_PROVIDER or LLM_PROVIDER environment variable.

    Returns:
        LLMConfig configured for the default provider
    """
    if settings.provider == "azure":
        return get_azure_config()
    elif settings.provider == "anthropic":
        # Fallback to a basic config - can be extended
        return LLMConfig(provider="anthropic", model="claude-3-5-sonnet-20241022")
    else:
        # Default to Google
        return DEFAULT_LLM_CONFIG
