from __future__ import annotations

from app.models.debug import DebugResolutionView
from app.models.resolution import ResolutionResult


def build_debug_view(resolution: ResolutionResult) -> DebugResolutionView:
    return DebugResolutionView(
        request_id=resolution.request_id,
        status=resolution.status,
        execution_context=resolution.execution_context,
        intent_family=resolution.intent_family,
        rule_id=resolution.rule_id,
        matched_patterns=resolution.matched_patterns,
        candidate_modules=resolution.candidate_modules,
        candidate_capabilities=resolution.candidate_capabilities,
        selected_modules=resolution.selected_modules,
        selected_capabilities=resolution.selected_capabilities,
        recommended_module=resolution.recommended_module,
        mode=resolution.mode,
        should_compose=resolution.should_compose,
        handoff=resolution.handoff,
        restrictions=resolution.restrictions,
        confidence=resolution.confidence,
        reason_codes=resolution.reason_codes,
        reasoning_notes=resolution.reasoning_notes,
        plan=resolution.plan,
    )