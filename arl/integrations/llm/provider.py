"""LLM provider abstraction using LiteLLM."""

from typing import Any

import litellm
from pydantic import BaseModel

from arl.config.llm_config import LLMConfig
from arl.config.settings import settings


class LLMResponse(BaseModel):
    """LLM response wrapper."""

    content: str
    model: str
    tokens_used: int = 0
    finish_reason: str = "stop"


class LLMProvider:
    """Provider-agnostic LLM interface using LiteLLM."""

    def __init__(self, config: LLMConfig | None = None):
        """Initialize LLM provider."""
        self.config = config or LLMConfig()

        # Set API keys from settings
        if settings.google_api_key:
            litellm.api_key = settings.google_api_key
        if settings.azure_openai_api_key:
            litellm.azure_key = settings.azure_openai_api_key
        if settings.azure_openai_endpoint:
            litellm.azure_api_base = settings.azure_openai_endpoint
        if settings.azure_openai_api_version:
            litellm.azure_api_version = settings.azure_openai_api_version
        if settings.anthropic_api_key:
            litellm.anthropic_key = settings.anthropic_api_key

    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Get completion from LLM.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            **kwargs: Additional arguments for LiteLLM

        Returns:
            LLM response
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Merge config with kwargs
        call_kwargs = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "timeout": self.config.timeout_seconds,
            **kwargs,
        }

        # Add Azure-specific parameters if using Azure provider
        if self.config.provider == "azure":
            if settings.azure_openai_api_key:
                call_kwargs["api_key"] = settings.azure_openai_api_key
            if settings.azure_openai_endpoint:
                call_kwargs["api_base"] = settings.azure_openai_endpoint
            if settings.azure_openai_api_version:
                call_kwargs["api_version"] = settings.azure_openai_api_version

        # Call LiteLLM
        response = litellm.completion(**call_kwargs)

        # Extract response
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens if hasattr(response, "usage") else 0
        finish = response.choices[0].finish_reason

        return LLMResponse(
            content=content,
            model=response.model,
            tokens_used=tokens,
            finish_reason=finish,
        )

    def complete_for_agent(
        self,
        agent_type: str,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Get completion using agent-specific model configuration.

        Args:
            agent_type: Type of agent (orchestrator, hypothesis, etc.)
            prompt: User prompt
            system_prompt: System prompt
            **kwargs: Additional arguments

        Returns:
            LLM response
        """
        model = self.config.get_model_for_agent(agent_type)
        return self.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            **kwargs,
        )
