from __future__ import annotations

from app.models.provider import ProviderRequest, ProviderResponse
from app.providers.base import BaseProviderClient


class AnthropicClient(BaseProviderClient):
    provider_name = "anthropic"

    def __init__(self, model: str = "claude-3-5-sonnet") -> None:
        self.model = model

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse(
            provider=self.provider_name,
            model=self.model,
            content=(
                "Stub response from AnthropicClient. "
                "Real provider integration is not enabled yet."
            ),
            raw={
                "request_prompt": request.prompt,
                "metadata": request.metadata,
                "stub": True,
            },
            success=True,
        )