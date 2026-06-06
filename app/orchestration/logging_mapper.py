from __future__ import annotations

from app.models.resolution import ResolutionResult


def build_resolution_log_payload(resolution: ResolutionResult) -> dict:
    execution_context = resolution.execution_context

    return {
        "request_id": resolution.request_id,
        "status": resolution.status,
        "client_context": resolution.client_context,
        "app_env": execution_context.app_env if execution_context else None,
        "active_provider": execution_context.active_provider if execution_context else None,
        "started_at": execution_context.started_at if execution_context else None,
        "duration_ms": execution_context.duration_ms if execution_context else None,
        "intent_family": resolution.intent_family,
        "rule_id": resolution.rule_id,
        "recommended_module": resolution.recommended_module,
        "mode": resolution.mode,
        "handoff": resolution.handoff,
        "confidence": resolution.confidence,
        "matched_patterns": resolution.matched_patterns,
        "reason_codes": resolution.reason_codes,
        "selected_modules": resolution.selected_modules,
        "selected_capabilities": resolution.selected_capabilities,
        "plan_strategy": resolution.plan.strategy if resolution.plan else None,
    }