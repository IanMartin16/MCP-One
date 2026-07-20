"""
base.py — interfaz async de los provider clients.  (app/providers/base.py)

Cambio vs. la versión stub: generate() ahora es `async`. Las llamadas a los LLM
son de red y lentas (segundos); en un servicio async no deben bloquear el event
loop. Los dos clientes reales (OpenAI, Anthropic) hacen HTTP async con httpx.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.provider import ProviderRequest, ProviderResponse


class BaseProviderClient(ABC):
    provider_name: str = "base"

    @abstractmethod
    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        raise NotImplementedError
