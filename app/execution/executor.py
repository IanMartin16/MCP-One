"""
executor.py — el órgano motor de MCPOne.

Convierte una capability de ejecución (output_mode=tool_execution) en una llamada
real al cliente y emite un toolResult NEUTRAL (kind + data + meta). No arma
sections: la presentación es de nexus-slim. MCPOne ejecuta y razona; nunca presenta.

AGNÓSTICO AL DISPARADOR. La entrada es ExecutionRequest("ejecuta esta capability
con estos símbolos"), sin importar quién la originó:
  - hoy: el router del widget (next_step: execute)
  - mañana: SSC, por iniciativa propia (superagente activo)
El ejecutor no sabe ni le importa de dónde vino la orden. Ese desacople es lo
que vuelve esto el primer órgano motor del superagente, no un endpoint del widget.

Single-capability en este primer corte. La composición (varias capabilities ->
varios toolResults en el envelope `results: [...]`) se agrega después iterando
sobre N; el contrato ya es plural, así que no se rediseña.
"""

from __future__ import annotations

import re
import time
from typing import Any

from pydantic import BaseModel, Field

from app.utils.cryptolink_client import CryptoLinkClient
from app.models.registry import CapabilityDef
from app.execution.normalizers import normalize_data


# Conocimiento de dominio de Cryptolink (portado del extractSymbols de Nexus).
# Vive en el ejecutor, NO en el router: el router enruta, esto es de crypto.
KNOWN_SYMBOLS = {"BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "AVAX", "DOT", "LINK", "BNB"}
DEFAULT_SYMBOLS = ["BTC", "ETH", "SOL", "ZEC", "USDT"]

# Endpoints que no requieren símbolos.
NO_SYMBOL_ENDPOINTS = {"get_snapshot"}


def extract_symbols(message: str | None) -> list[str]:
    """Portado fiel del extractSymbols de Nexus. Default lo decide el caller."""
    if not message:
        return []
    found: list[str] = []
    for token in re.split(r"[^A-Z0-9]+", message.upper()):
        if token in KNOWN_SYMBOLS and token not in found:
            found.append(token)
    return found


class ExecutionRequest(BaseModel):
    """Lo que el ejecutor necesita, desacoplado de quién lo disparó."""

    model_config = {"arbitrary_types_allowed": True}

    capability: CapabilityDef
    message: str | None = None          # para extraer símbolos
    symbols: list[str] | None = None    # si ya vienen resueltos, se respetan
    fiat: str = "USD"                   # alineado a v4; ya no MXN


class ToolResult(BaseModel):
    """Resultado NEUTRAL. Sin sections. nexus-slim lo viste después."""

    kind: str
    ok: bool
    tool: str                            # capability_id ejecutada
    data: dict[str, Any] | None = None   # materia prima (resp de la API)
    narrative: str | None = None 
    source: str | None = None
    as_of: str | None = None
    fiat: str = "USD"
    latency_ms: int = 0
    error: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class CryptoLinkExecutor:
    """
    Ejecutor genérico. No conoce los 11 endpoints uno por uno: lee lo que la
    CapabilityDef declara (execution_endpoint, output_kind) y actúa.
    """

    def __init__(self, client: CryptoLinkClient):
        self._client = client

    async def execute(self, req: ExecutionRequest) -> ToolResult:
        cap = req.capability

        # Guardas: la capability debe ser de ejecución y estar bien declarada.
        if "tool_execution" not in (cap.output_modes or []):
            return self._fail(cap, "capability_not_executable")
        endpoint = cap.execution_endpoint
        kind = cap.output_kind
        if not endpoint or not kind:
            return self._fail(cap, "capability_missing_execution_binding")

        method = getattr(self._client, endpoint, None)
        if method is None or not callable(method):
            return self._fail(cap, f"client_has_no_endpoint:{endpoint}", kind=kind)

        # Resolución de símbolos: respeta los provistos; si no, extrae; si no, default.
        if endpoint in NO_SYMBOL_ENDPOINTS:
            args: tuple = ()
        else:
            symbols = req.symbols or extract_symbols(req.message) or DEFAULT_SYMBOLS
            args = (symbols, req.fiat)

        t0 = time.monotonic()
        try:
            resp: dict[str, Any] = await method(*args)
        except Exception as exc:  # noqa: BLE001 — un fallo de endpoint no tumba el motor
            return self._fail(
                cap, f"{kind}_not_available: {exc}", kind=kind,
                latency_ms=int((time.monotonic() - t0) * 1000),
            )
        latency_ms = int((time.monotonic() - t0) * 1000)

        ok = bool(resp) and resp.get("ok") is True
        if not ok:
            return self._fail(
                cap, f"{kind}_not_available: {resp}", kind=kind, latency_ms=latency_ms
            )

        # Normalización ESTRUCTURAL: reubica la carga cruda a forma uniforme
        # (rows / campos planos) sin inspeccionar su contenido. Los campos de
        # sobre (source, ts, fiat) se leen del crudo antes de normalizar.
        source = resp.get("source")
        as_of = resp.get("ts") or resp.get("asOf")
        fiat = resp.get("fiat") or req.fiat
        normalized = normalize_data(resp, kind=kind)

        # toolResult NEUTRAL: data uniforme (a diferencia del Nexus viejo, que
        # subía el crudo a sections). nexus-slim lo baja a kpi_grid/chart/text.
        return ToolResult(
            kind=kind,
            ok=True,
            tool=cap.capability_id,
            data=normalized,
            source=source,
            as_of=as_of,
            fiat=fiat,
            latency_ms=latency_ms,
        )

    @staticmethod
    def _fail(
        cap: CapabilityDef, error: str, kind: str | None = None, latency_ms: int = 0
    ) -> ToolResult:
        return ToolResult(
            kind=kind or (cap.output_kind or "unknown"),
            ok=False,
            tool=cap.capability_id,
            error=error,
            latency_ms=latency_ms,
        )
