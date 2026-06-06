from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.provider import ProviderRequest, ProviderResponse


class BaseProviderClient(ABC):
    provider_name: str = "base"

    @abstractmethod
    def generate(self, request: ProviderRequest) -> ProviderResponse:
        raise NotImplementedError