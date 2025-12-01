#!/usr/bin/env python
"""Test LLM configuration is reading from environment correctly."""

from arl.config.settings import settings
from arl.config.llm_config import (
    DEFAULT_LLM_CONFIG,
    FAST_LLM_CONFIG,
    POWERFUL_LLM_CONFIG,
    get_default_config,
)

print("=" * 60)
print("LLM Configuration Test")
print("=" * 60)
print()

print("Environment Settings:")
print(f"  Provider from .env: {settings.provider}")
print(f"  Azure Endpoint: {settings.azure_openai_endpoint}")
print(f"  Azure Deployment: {settings.azure_openai_deployment_name}")
print()

print("LLM Configurations:")
print(f"  DEFAULT_LLM_CONFIG:")
print(f"    - Provider: {DEFAULT_LLM_CONFIG.provider}")
print(f"    - Model: {DEFAULT_LLM_CONFIG.model}")
print()

print(f"  FAST_LLM_CONFIG:")
print(f"    - Provider: {FAST_LLM_CONFIG.provider}")
print(f"    - Model: {FAST_LLM_CONFIG.model}")
print(f"    - Temperature: {FAST_LLM_CONFIG.temperature}")
print()

print(f"  POWERFUL_LLM_CONFIG:")
print(f"    - Provider: {POWERFUL_LLM_CONFIG.provider}")
print(f"    - Model: {POWERFUL_LLM_CONFIG.model}")
print()

default_config = get_default_config()
print(f"  get_default_config():")
print(f"    - Provider: {default_config.provider}")
print(f"    - Model: {default_config.model}")
print()

# Validation
print("Validation:")
if settings.provider == "azure":
    if all(
        [
            DEFAULT_LLM_CONFIG.provider == "azure",
            FAST_LLM_CONFIG.provider == "azure",
            POWERFUL_LLM_CONFIG.provider == "azure",
            "azure/" in DEFAULT_LLM_CONFIG.model,
        ]
    ):
        print("  ✓ All configs correctly using Azure")
    else:
        print("  ✗ Configuration mismatch!")
        print(f"    DEFAULT provider: {DEFAULT_LLM_CONFIG.provider}")
        print(f"    FAST provider: {FAST_LLM_CONFIG.provider}")
        print(f"    POWERFUL provider: {POWERFUL_LLM_CONFIG.provider}")
else:
    print(f"  Provider is '{settings.provider}' (not Azure)")

print()
print("=" * 60)
