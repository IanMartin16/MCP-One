from __future__ import annotations

from typing import Any

import httpx

from app.config.settings import get_settings  # ajustar import al layout real


# Espejo de los 12 métodos del CryptoLinkClient.java -> path de la API v2.
# (símbolos CSV + fiat como query; x-api-key como header; salvo snapshot.)
_ENDPOINTS = {
    "snapshot": "/v1/snapshot",
    "prices": "/v1/prices",
    "movers": "/v1/movers",
    "trends": "/v1/trends",
    "price_spark": "/v1/prices/spark",
    "momentum": "/v1/momentum",
    "regime": "/v1/regime",
    "risk_flags": "/v1/risk-flags",
    "anomalies": "/v1/anomalies",
    "market_health": "/v1/market-health",
    "social_pulse": "/v1/social-pulse",
}


class CryptoLinkClient:
    """Cliente HTTP a la API v2 de CryptoLink. Reusa el AsyncClient de MCPOne."""

    def __init__(self, http: httpx.AsyncClient | None = None) -> None:
        s = get_settings()
        self._base_url = s.cryptolink_base_url
        self._api_key = s.cryptolink_api_key
        self._timeout = s.cryptolink_timeout_seconds
        # AsyncClient perezoso: se crea en el primer request (dentro del loop),
        # no en __init__. Así el cliente puede instanciarse fuera de contexto async
        # (p.ej. en el factory cacheado del binding) sin abrir conexiones.
        self._http = http
        self._owns_http = http is None

    def _client(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(base_url=self._base_url)
        return self._http

    async def aclose(self) -> None:
        if self._owns_http and self._http is not None:
            await self._http.aclose()

    # ---- ejecutor genérico -------------------------------------------------

    async def _get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        headers = {"x-api-key": self._api_key} if self._api_key else {}
        resp = await self._client().get(
            path, params=params, headers=headers, timeout=self._timeout
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _q(symbols: list[str], fiat: str, **extra: Any) -> dict[str, Any]:
        params: dict[str, Any] = {"symbols": ",".join(symbols), "fiat": fiat}
        params.update({k: v for k, v in extra.items() if v is not None})
        return params

    # ---- 12 wrappers (uno por método del original) -------------------------
    # Default USD en todos. El símbolo del cambio: ya no hay MXN.

    async def get_snapshot(self) -> dict[str, Any]:
        return await self._get(_ENDPOINTS["snapshot"])

    async def get_prices(self, symbols: list[str], fiat: str = "USD") -> dict[str, Any]:
        return await self._get(_ENDPOINTS["prices"], self._q(symbols, fiat))

    async def get_movers(
        self, symbols: list[str], fiat: str = "USD", limit: int = 10
    ) -> dict[str, Any]:
        return await self._get(_ENDPOINTS["movers"], self._q(symbols, fiat, limit=limit))

    async def get_trends(self, symbols: list[str], fiat: str = "USD") -> dict[str, Any]:
        return await self._get(_ENDPOINTS["trends"], self._q(symbols, fiat))

    async def get_price_spark(self, symbols: list[str], fiat: str = "USD") -> dict[str, Any]:
        return await self._get(_ENDPOINTS["price_spark"], self._q(symbols, fiat))

    async def get_momentum(self, symbols: list[str], fiat: str = "USD") -> dict[str, Any]:
        return await self._get(_ENDPOINTS["momentum"], self._q(symbols, fiat))

    async def get_regime(self, symbols: list[str], fiat: str = "USD") -> dict[str, Any]:
        return await self._get(_ENDPOINTS["regime"], self._q(symbols, fiat))

    async def get_risk_flags(self, symbols: list[str], fiat: str = "USD") -> dict[str, Any]:
        return await self._get(_ENDPOINTS["risk_flags"], self._q(symbols, fiat))

    async def get_anomalies(self, symbols: list[str], fiat: str = "USD") -> dict[str, Any]:
        return await self._get(_ENDPOINTS["anomalies"], self._q(symbols, fiat))

    async def get_market_health(self, symbols: list[str], fiat: str = "USD") -> dict[str, Any]:
        return await self._get(_ENDPOINTS["market_health"], self._q(symbols, fiat))

    async def get_social_pulse(self, symbols: list[str], fiat: str = "USD") -> dict[str, Any]:
        return await self._get(_ENDPOINTS["social_pulse"], self._q(symbols, fiat))
