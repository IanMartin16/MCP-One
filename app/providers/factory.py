from __future__ import annotations

from app.config.settings import get_settings
from app.providers.anthropic_client import AnthropicClient
from app.providers.base import BaseProviderClient
from app.providers.openai_client import OpenAIClient


def get_provider_client() -> BaseProviderClient:
    settings = get_settings()

    if settings.active_provider == "openai":
        return OpenAIClient(model=settings.openai_model)

    if settings.active_provider == "anthropic":
        return AnthropicClient(model=settings.anthropic_model)

    return OpenAIClient(model="stub-none")