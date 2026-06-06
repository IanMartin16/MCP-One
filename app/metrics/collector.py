from __future__ import annotations

from app.metrics.store import metrics_store
from app.models.resolution import ResolutionResult


def record_resolution_metrics(resolution: ResolutionResult) -> None:
    duration_ms = None
    if resolution.execution_context is not None:
        duration_ms = resolution.execution_context.duration_ms
        
    metrics_store.record(
        status=resolution.status,
        mode=resolution.mode,
        plan_strategy=resolution.plan.strategy if resolution.plan else None,
        recommended_module=resolution.recommended_module,
        intent_family=resolution.intent_family,
        rule_id=resolution.rule_id,
        duration_ms=duration_ms,
    )