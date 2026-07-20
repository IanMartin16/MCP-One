"""
anthropic_client.py — cliente real de Anthropic.  (app/providers/anthropic_client.py)

Messages API. Difiere de OpenAI en la firma (la abstracción absorbe eso):
  - header `x-api-key` (no Authorization: Bearer)
  - header `anthropic-version` obligatorio
  - `max_tokens` obligatorio en el body
  - system prompt va como parámetro `system` (top-level), no dentro de messages
  - la respuesta está en data["content"][0]["text"]

Mismo contrato que OpenAI: async, y si falla devuelve success=False sin lanzar.
"""

from __future__ import annotations

import httpx

from app.config.settings import get_settings
from app.models.provider import ProviderRequest, ProviderResponse
from app.providers.base import BaseProviderClient

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


class AnthropicClient(BaseProviderClient):
    provider_name = "anthropic"

    def __init__(self, model: str = "claude-haiku-4-5") -> None:
        self.model = model
        s = get_settings()
        self._api_key = s.anthropic_api_key
        self._timeout = s.provider_timeout_seconds

    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        if not self._api_key:
            return self._fail("anthropic_api_key not configured")

        payload = {
            "model": self.model,
            "max_tokens": request.max_tokens,       # obligatorio en Anthropic
            "temperature": request.temperature,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        if request.system_prompt:
            payload["system"] = request.system_prompt  # system es top-level aquí

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as http:
                resp = await http.post(ANTHROPIC_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            # content es una lista de bloques; el texto está en el primer bloque.
            content = data["content"][0]["text"].strip()
            return ProviderResponse(
                provider=self.provider_name,
                model=self.model,
                content=content,
                raw={"usage": data.get("usage", {})},
                success=True,
            )
        except Exception as exc:  # noqa: BLE001 — el LLM nunca tumba la respuesta
            return self._fail(f"anthropic request failed: {exc}")

    def _fail(self, error: str) -> ProviderResponse:
        return ProviderResponse(
            provider=self.provider_name,
            model=self.model,
            content="",
            success=False,
            error=error,
        )
