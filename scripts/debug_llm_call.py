#!/usr/bin/env python
"""Debug what's actually being passed to litellm."""

from arl.config.llm_config import POWERFUL_LLM_CONFIG
from arl.integrations.llm.provider import LLMProvider

print("=" * 60)
print("Debug LLM Provider")
print("=" * 60)
print()

print(f"POWERFUL_LLM_CONFIG:")
print(f"  Provider: {POWERFUL_LLM_CONFIG.provider}")
print(f"  Model: {POWERFUL_LLM_CONFIG.model}")
print(f"  Temperature: {POWERFUL_LLM_CONFIG.temperature}")
print()

print("Creating LLMProvider...")
provider = LLMProvider(config=POWERFUL_LLM_CONFIG)
print(f"  Provider initialized with model: {provider.config.model}")
print()

print("Preparing call kwargs...")
call_kwargs = {
    "model": provider.config.model,
    "messages": [{"role": "user", "content": "Say 'test' in one word"}],
    "temperature": provider.config.temperature,
    "max_tokens": 10,
}

print("Call kwargs:")
for key, value in call_kwargs.items():
    if key != "messages":
        print(f"  {key}: {value}")
print()

print("This is what will be passed to litellm.completion()")
print()

# Check if Azure env vars are set
import os
print("Azure Environment Variables:")
print(f"  AZURE_OPENAI_API_KEY: {'Set' if os.getenv('AZURE_OPENAI_API_KEY') else 'NOT SET'}")
print(f"  AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT', 'NOT SET')}")
print(f"  AZURE_OPENAI_API_VERSION: {os.getenv('AZURE_OPENAI_API_VERSION', 'NOT SET')}")
print(f"  AZURE_OPENAI_DEPLOYMENT_NAME: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'NOT SET')}")
print()

print("If you want to test the actual call, uncomment the code below")
print("(it will make a real API call)")
print()

# Uncomment to test actual call:
# try:
#     print("Making test call to Azure OpenAI...")
#     response = provider.complete(prompt="Say 'test' in one word", max_tokens=10)
#     print(f"Success! Response: {response.content}")
# except Exception as e:
#     print(f"Error: {e}")
