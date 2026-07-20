"""
enrichment.py — enriquecimiento del summary de RECOMENDACIÓN.  (MCPOne)
                (app/orchestration/enrichment.py)

Cambios:
  - `enrich_summary` ahora es `async` (el provider client.generate es async).
  - Ya NO se llama desde compose_output (síncrono). Se llama desde el endpoint
    orchestrate (async), y SÓLO cuando no hubo ejecución (recomendación pura) —
    porque en ejecución el widget usa el tool_result, no el summary.

Esto separa las dos narrativas por carril:
  - recomendación -> enrich_summary (este archivo, inglés, sobre la decisión)
  - ejecución     -> generate_narrative (narrative.py, español, sobre los datos)
Cada una en su caso, sin redundancia ni doble llamada al LLM.
"""

from __future__ import annotations

from app.config.settings import get_settings
from app.metrics.provider_collector import record_provider_metrics
from app.models.provider import ProviderRequest
from app.models.resolution import ResolutionResult
from app.providers.factory import get_provider_client


async def enrich_summary(summary: str, resolution: ResolutionResult) -> str:
    settings = get_settings()

    if not settings.enable_provider_enrichment:
        return summary

    if resolution.mode not in settings.provider_enrichment_modes:
        return summary

    client = get_provider_client()

    request = ProviderRequest(
        system_prompt=(
            "You are a concise orchestration narrator for MCP-One. "
            "Rewrite the provided orchestration summary clearly and professionally. "
            "Do not invent capabilities, modules, or actions."
        ),
        prompt=(
            f"Original summary:\n{summary}\n\n"
            f"Resolution mode: {resolution.mode}\n"
            f"Recommended module: {resolution.recommended_module}\n"
            f"Reason codes: {', '.join(resolution.reason_codes)}\n"
            f"Restrictions: {', '.join(resolution.restrictions) if resolution.restrictions else 'none'}\n\n"
            "Return only the improved summary."
        ),
        metadata={
            "feature": "summary_enrichment",
            "mode": resolution.mode,
            "recommended_module": resolution.recommended_module,
            "request_id": resolution.request_id,
        },
    )

    response = await client.generate(request)   # <- await (antes era síncrono)
    record_provider_metrics(response)

    if not response.success or not response.content:
        return summary

    return response.content.strip()
