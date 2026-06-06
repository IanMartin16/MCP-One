from __future__ import annotations

from app.models.provider import ProviderRequest, ProviderResponse
from app.providers.base import BaseProviderClient


class OpenAIClient(BaseProviderClient):
    provider_name = "openai"

    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model = model

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse(
            provider=self.provider_name,
            model=self.model,
            content=(
                "Stub response from OpenAIClient. "
                "Real provider integration is not enabled yet."
            ),
            raw={
                "request_prompt": request.prompt,
                "metadata": request.metadata,
                "stub": True,
            },
            success=True,
        )