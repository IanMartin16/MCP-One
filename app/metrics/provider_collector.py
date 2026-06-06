from __future__ import annotations

from app.metrics.store import metrics_store
from app.models.provider import ProviderResponse


def record_provider_metrics(response: ProviderResponse) -> None:
    metrics_store.record_provider_usage(
        provider=response.provider,
        model=response.model,
        success=response.success,
    )