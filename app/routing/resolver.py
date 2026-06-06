from __future__ import annotations

from app.config.settings import get_settings
from app.models.resolution import ResolutionResult
from app.models.routing import OrchestrationInput
from app.orchestration.planner import build_plan
from app.policies.exposure import resolve_output_mode
from app.policies.handoff import should_handoff
from app.registry.access import get_capability, get_module
from app.routing.matcher import detect_intent_family
from app.utils.reason_codes import ReasonCodes
from app.utils.trace import generate_request_id
from app.orchestration.logging_mapper import build_resolution_log_payload
from app.utils.logging import log_event
from app.utils.client_context import sanitize_client_context
from app.models.execution import ExecutionContext
import time
from app.utils.time import elapsed_ms, utc_now_iso
from app.orchestration.status import resolve_result_status
from app.metrics.collector import record_resolution_metrics
from app.metrics.recent_store import recent_resolution_store
from app.orchestration.recent_mapper import build_recent_resolution_item


def _filter_allowed_modules(module_ids: list[str], allowed_modules: list[str]) -> list[str]:
    if not allowed_modules:
        return module_ids
    allowed = set(allowed_modules)
    return [module_id for module_id in module_ids if module_id in allowed]


def _finalize_result(result: ResolutionResult, start_perf: float) -> ResolutionResult:
    result.plan = build_plan(result)
    result.status = resolve_result_status(result)


    if result.execution_context is not None:
        end_perf = time.perf_counter()
        result.execution_context.duration_ms = elapsed_ms(start_perf, end_perf)

    record_resolution_metrics(result)

    recent_resolution_store.append(
        build_recent_resolution_item(result)
    )    

    log_event(
        "resolution_completed",
        build_resolution_log_payload(result),
    )

    return result


def resolve_input(payload: OrchestrationInput) -> ResolutionResult:
    settings = get_settings()
    start_perf = time.perf_counter()
    started_at = utc_now_iso()

    request_id = payload.request_id or generate_request_id()
    client_context = sanitize_client_context(payload.client_context)
    execution_context = ExecutionContext(
        request_id=request_id,
        client_context=client_context,
        app_env=settings.app_env,
        active_provider=settings.active_provider,
        enable_composition=settings.enable_composition,
        enable_provider_enrichment=settings.enable_provider_enrichment,
        enable_structured_logging=settings.enable_structured_logging,
        started_at=started_at,
        duration_ms=None,
    )
    match = detect_intent_family(payload.user_input)

    if not match.matched_rule:
        result = ResolutionResult(
            request_id=request_id,
            client_context=client_context,
            execution_context=execution_context,
            intent_family=None,
            rule_id=None,
            matched_patterns=[],
            candidate_modules=[],
            candidate_capabilities=[],
            selected_modules=[],
            selected_capabilities=[],
            recommended_module=None,
            mode="summary",
            should_compose=False,
            handoff=False,
            restrictions=["No matching intent rule found."],
            confidence=settings.default_confidence_floor,
            reason_codes=[
                ReasonCodes.NO_RULE_MATCH,
                ReasonCodes.FALLBACK_PATH,
            ],
            reasoning_notes=[
                "Fallback path used because no rule matched the input."
            ],
        )
        return _finalize_result(result, start_perf)

    rule = match.matched_rule

    candidate_modules = list(rule.preferred_modules)
    candidate_capabilities = list(rule.preferred_capabilities)

    selected_modules = _filter_allowed_modules(
        candidate_modules,
        payload.allowed_modules,
    )

    selected_capabilities: list[str] = []
    for capability_id in candidate_capabilities:
        capability = get_capability(capability_id)
        if capability and capability.module_id in selected_modules:
            selected_capabilities.append(capability_id)

    if not selected_modules or not selected_capabilities:
        result = ResolutionResult(
            request_id=request_id,
            client_context=client_context,
            execution_context=execution_context,
            intent_family=rule.intent_family,
            rule_id=rule.rule_id,
            matched_patterns=match.matched_patterns,
            candidate_modules=candidate_modules,
            candidate_capabilities=candidate_capabilities,
            selected_modules=[],
            selected_capabilities=[],
            recommended_module=None,
            mode="handoff" if rule.handoff_if_unavailable else "summary",
            should_compose=False,
            handoff=rule.handoff_if_unavailable,
            restrictions=["No eligible modules/capabilities after allowed_modules filter."],
            confidence=max(settings.default_confidence_floor, match.confidence - 0.2),
            reason_codes=[
                ReasonCodes.RULE_MATCHED,
                ReasonCodes.ALLOWED_MODULES_FILTER_APPLIED,
                ReasonCodes.NO_ELIGIBLE_MODULES,
            ],
            reasoning_notes=[
                "A rule matched, but no module remained eligible after filtering."
            ],
        )
        return _finalize_result(result, start_perf)

    primary_module = get_module(selected_modules[0])
    primary_capability = get_capability(selected_capabilities[0])

    if not primary_module or not primary_capability:
        result = ResolutionResult(
            request_id=request_id,
            client_context=client_context,
            execution_context=execution_context,
            intent_family=rule.intent_family,
            rule_id=rule.rule_id,
            matched_patterns=match.matched_patterns,
            candidate_modules=candidate_modules,
            candidate_capabilities=candidate_capabilities,
            selected_modules=[],
            selected_capabilities=[],
            recommended_module=None,
            mode="handoff",
            should_compose=False,
            handoff=True,
            restrictions=["Registry inconsistency detected."],
            confidence=settings.default_confidence_floor,
            reason_codes=[
                ReasonCodes.RULE_MATCHED,
                ReasonCodes.REGISTRY_INCONSISTENCY,
            ],
            reasoning_notes=[
                "Primary module/capability could not be resolved from registry."
            ],
        )
        return _finalize_result(result, start_perf)

    mode = resolve_output_mode(primary_module, primary_capability)
    handoff = should_handoff(primary_module, primary_capability)

    if mode == "preview":
        handoff = False

    if not settings.enable_composition:
        should_compose = False
    else:
        should_compose = (
            rule.allow_composition
            and len(selected_modules) > 1
            and len(selected_capabilities) > 1
        )

    final_modules = selected_modules if should_compose else [selected_modules[0]]
    final_capabilities = (
        selected_capabilities if should_compose else [selected_capabilities[0]]
    )

    if should_compose and mode == "summary":
        mode = "composed_summary"

    restrictions = list(primary_capability.restrictions)
    reason_codes = [
        ReasonCodes.RULE_MATCHED,
        ReasonCodes.PRIMARY_MODULE_SELECTED,
    ]

    if payload.allowed_modules:
        reason_codes.append(ReasonCodes.ALLOWED_MODULES_FILTER_APPLIED)

    if should_compose:
        reason_codes.append(ReasonCodes.COMPOSITION_ENABLED)
    else:
        reason_codes.append(ReasonCodes.SINGLE_MODULE_PATH)

    if mode == "preview":
        reason_codes.append(ReasonCodes.PREVIEW_MODE)

    if mode == "handoff":
        reason_codes.append(ReasonCodes.HANDOFF_MODE)

    if handoff:
        reason_codes.append(ReasonCodes.HANDOFF_REQUIRED)

    if primary_module.status == "planned":
        reason_codes.append(ReasonCodes.PLANNED_MODULE_SELECTED)
    elif primary_module.status == "beta":
        reason_codes.append(ReasonCodes.BETA_MODULE_SELECTED)
    elif primary_module.status == "active":
        reason_codes.append(ReasonCodes.ACTIVE_MODULE_SELECTED)

    result = ResolutionResult(
        request_id=request_id,
        client_context=client_context,
        execution_context=execution_context,
        intent_family=rule.intent_family,
        rule_id=rule.rule_id,
        matched_patterns=match.matched_patterns,
        candidate_modules=candidate_modules,
        candidate_capabilities=candidate_capabilities,
        selected_modules=final_modules,
        selected_capabilities=final_capabilities,
        recommended_module=selected_modules[0],
        mode=mode,
        should_compose=should_compose,
        handoff=handoff,
        restrictions=restrictions,
        confidence=min(settings.default_confidence_cap, match.confidence),
        reason_codes=reason_codes,
        reasoning_notes=[
            f"Matched rule: {rule.rule_id}",
            f"Matched patterns: {', '.join(match.matched_patterns) if match.matched_patterns else 'none'}",
            f"Composition enabled: {should_compose}",
        ],
    )
    return _finalize_result(result, start_perf)