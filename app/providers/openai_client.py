"""
openai_client.py — cliente real de OpenAI.  (app/providers/openai_client.py)

Chat Completions API. Async (httpx). La narrativa es ENRIQUECIMIENTO: si falla,
se devuelve success=False con el error, pero NO se lanza excepción — el caller
omite la narrativa y el tool_result sigue intacto. Nunca tumbar la respuesta por
un fallo del LLM.
"""

from __future__ import annotations

import httpx

from app.config.settings import get_settings
from app.models.provider import ProviderRequest, ProviderResponse
from app.providers.base import BaseProviderClient

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIClient(BaseProviderClient):
    provider_name = "openai"

    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model = model
        s = get_settings()
        self._api_key = s.openai_api_key
        self._timeout = s.provider_timeout_seconds

    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        if not self._api_key:
            return self._fail("openai_api_key not configured")

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as http:
                resp = await http.post(OPENAI_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
            return ProviderResponse(
                provider=self.provider_name,
                model=self.model,
                content=content,
                raw={"usage": data.get("usage", {})},
                success=True,
            )
        except Exception as exc:  # noqa: BLE001 — el LLM nunca tumba la respuesta
            return self._fail(f"openai request failed: {exc}")

    def _fail(self, error: str) -> ProviderResponse:
        return ProviderResponse(
            provider=self.provider_name,
            model=self.model,
            content="",
            success=False,
            error=error,
        )
