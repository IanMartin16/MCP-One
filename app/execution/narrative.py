"""
narrative.py — genera la narrativa que explica un tool_result.  (MCPOne)

Ruta sugerida: app/execution/narrative.py

Toma el tool_result NEUTRAL (kind + data), arma un prompt en español, llama al
provider activo (OpenAI o Anthropic según settings), y devuelve el texto. La
narrativa es ENRIQUECIMIENTO: si el flag está apagado o el provider falla, se
devuelve None y el flujo sigue con el tool_result intacto (sin narrativa).

Estrategia de despliegue: `enable_provider_enrichment=False` por defecto → se
despliega con narrativa apagada; se enciende (flag a True) tras el decomiso de
Nexus. El carril token de nexus-slim ya está listo para recibirla.
"""

from __future__ import annotations

from typing import Any

from app.config.settings import get_settings
from app.models.provider import ProviderRequest
from app.providers.factory import get_provider_client

SYSTEM_PROMPT = (
    "Eres un analista de mercado del ecosistema Evilink. "
    "Explica los datos que te dan en UNA sola frase, natural y clara, en español. "
    "No inventes cifras ni agregues datos que no estén. No uses jerga técnica "
    "innecesaria. Sé conciso y directo, como quien resume de un vistazo."
)

# Plantillas de contexto por kind — le dan al LLM el marco de qué está explicando.
KIND_CONTEXT = {
    "momentum": "Estos son datos de momentum (fuerza y dirección) de criptoactivos.",
    "trends": "Estos son datos de tendencia de criptoactivos.",
    "prices": "Estos son precios actuales de criptoactivos.",
    "movers": "Estos son los activos con mayor movimiento (subidas/bajadas).",
    "regime": "Este es el régimen o estado general del mercado cripto.",
    "market_health": "Esta es la salud general del mercado cripto.",
    "risk_flags": "Estas son alertas de riesgo del mercado cripto.",
    "anomalies": "Estas son anomalías detectadas en el mercado cripto.",
    "social_pulse": "Este es el pulso social / narrativa del mercado cripto.",
    "snapshot": "Esta es una foto general del mercado cripto.",
}


async def generate_narrative(kind: str, data: dict[str, Any]) -> str | None:
    """Devuelve la narrativa en español, o None si está apagada o falla."""
    settings = get_settings()

    # Flag maestro: si el enriquecimiento está apagado, no hay narrativa.
    if not settings.enable_provider_enrichment:
        return None
    # Sin provider activo, tampoco.
    if settings.active_provider not in ("openai", "anthropic"):
        return None

    context = KIND_CONTEXT.get(kind, "Estos son datos del ecosistema Evilink.")
    prompt = (
        f"{context}\n\n"
        f"Datos ({kind}):\n{_format_data(data)}\n\n"
        "Explícalos en una sola frase natural en español."
    )

    client = get_provider_client()
    response = await client.generate(
        ProviderRequest(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=160,
            metadata={"kind": kind},
        )
    )

    # Enriquecimiento: si el LLM falló, no rompemos nada — narrativa None.
    if not response.success or not response.content:
        return None
    return response.content


def _format_data(data: dict[str, Any]) -> str:
    """Aplana el data a un texto compacto y legible para el prompt.
    No inspecciona semántica; solo lo hace legible para el LLM."""
    if not isinstance(data, dict):
        return str(data)

    lines: list[str] = []
    rows = data.get("rows")
    if isinstance(rows, list) and rows:
        for row in rows[:6]:
            if isinstance(row, dict):
                parts = [f"{k}={v}" for k, v in row.items() if v is not None]
                lines.append("- " + ", ".join(parts))
    # Campos planos (agregados: state, score, etc.) que no sean rows.
    flat = {
        k: v for k, v in data.items()
        if k != "rows" and not isinstance(v, (list, dict)) and v is not None
    }
    if flat:
        lines.append(", ".join(f"{k}={v}" for k, v in flat.items()))
    return "\n".join(lines) if lines else str(data)
