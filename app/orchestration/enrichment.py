from __future__ import annotations

from app.config.settings import get_settings
from app.metrics.provider_collector import record_provider_metrics
from app.models.provider import ProviderRequest
from app.models.resolution import ResolutionResult
from app.providers.factory import get_provider_client


def enrich_summary(summary: str, resolution: ResolutionResult) -> str:
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

    response = client.generate(request)
    record_provider_metrics(response)

    if not response.success or not response.content:
        return summary

    return response.content.strip()