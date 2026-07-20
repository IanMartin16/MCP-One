from __future__ import annotations

from app.models.outputs import NextStep, OrchestrationOutput
from app.models.plan import OrchestrationPlan
from app.models.resolution import ResolutionResult
from app.registry.access import get_capability, get_module
from app.orchestration.planner import build_plan
from app.orchestration.user_facing_mapper import build_user_facing_payload

def _module_name(module_id: str | None) -> str | None:
    if not module_id:
        return None
    module = get_module(module_id)
    return module.name if module else module_id


def _capability_name(capability_id: str | None) -> str | None:
    if not capability_id:
        return None
    capability = get_capability(capability_id)
    return capability.name if capability else capability_id


def _build_summary_from_plan(plan: OrchestrationPlan | None) -> str:
    if not plan:
        return "MCP-One generó una resolución sin plan estructurado."

    primary_module_name = _module_name(plan.primary_module)
    primary_capability_name = _capability_name(plan.primary_capability)

    if plan.strategy == "fallback":
        return "MCP-One no encontró un módulo elegible para resolver la solicitud actual."

    if plan.strategy == "handoff":
        if primary_module_name and primary_capability_name:
            return (
                f"MCP-One identificó a {primary_module_name} con la capability "
                f"{primary_capability_name}, pero el flujo requiere handoff antes de continuar."
            )
        if primary_module_name:
            return (
                f"MCP-One identificó a {primary_module_name}, pero el flujo requiere handoff "
                f"antes de continuar."
            )
        return "MCP-One requiere handoff antes de continuar con la solicitud."

    if plan.strategy == "composed":
        primary = primary_module_name or "un módulo principal"
        secondary_names = [_module_name(module_id) or module_id for module_id in plan.secondary_modules]

        if secondary_names:
            return (
                f"MCP-One recomienda una respuesta compuesta con {primary} como módulo principal "
                f"y apoyo de {', '.join(secondary_names)}."
            )

        return f"MCP-One recomienda una respuesta compuesta con {primary}."

    if plan.strategy == "single_module":
        if primary_module_name and primary_capability_name:
            return (
                f"MCP-One resolvió la solicitud con {primary_module_name} "
                f"usando la capability {primary_capability_name}."
            )

        if primary_module_name:
            return f"MCP-One recomienda usar el módulo {primary_module_name}."

    return "MCP-One generó una resolución parcial."


def _build_insight_from_plan(plan: OrchestrationPlan | None, resolution: ResolutionResult) -> str | None:
    if not plan:
        return "La resolución no generó un plan estructurado."

    if plan.strategy == "fallback":
        return "No hubo coincidencia suficiente con el registry actual."

    if plan.strategy == "handoff":
        return "La solicitud requiere escalamiento o exposición limitada antes de ejecución."

    if plan.preview_only:
        return "La resolución quedó en modo preview por el estado actual del módulo o capability."

    if plan.strategy == "composed":
        return "La intención detectada se beneficia de una orquestación ligera entre múltiples módulos."

    if plan.strategy == "single_module":
        return "La intención pudo resolverse con un solo módulo."

    if resolution.handoff:
        return "La solicitud requiere handoff."

    return "MCP-One completó una resolución válida."


def _build_next_step(resolution: ResolutionResult) -> NextStep | None:
    if not resolution.recommended_module:
        return NextStep(
            type="review",
            reason="No eligible module found for this request.",
        )

    if resolution.handoff:
        return NextStep(
            type="handoff",
            module=resolution.recommended_module,
            reason="Escalar a módulo o flujo especializado.",
        )

    if resolution.mode == "preview":
        return NextStep(
            type="preview",
            module=resolution.recommended_module,
            reason="Mostrar capacidad disponible en modo limitado.",
        )

    return NextStep(
        type="execute",
        module=resolution.recommended_module,
        reason="Módulo recomendado para continuar el flujo.",
    )

def compose_output(resolution: ResolutionResult) -> OrchestrationOutput:
    effective_plan = resolution.plan or build_plan(resolution)
    raw_summary = _build_summary_from_plan(effective_plan)

    user_facing = build_user_facing_payload(resolution)

    return OrchestrationOutput(
        request_id=resolution.request_id,
        status=resolution.status,
        mode=resolution.mode,
        modules_used=resolution.selected_modules,
        capabilities_used=resolution.selected_capabilities,
        summary=raw_summary,
        insight=_build_insight_from_plan(effective_plan, resolution),
        recommended_module=resolution.recommended_module,
        next_step=_build_next_step(resolution),
        handoff=resolution.handoff,
        restrictions=resolution.restrictions,
        confidence=resolution.confidence,
        matched_patterns=resolution.matched_patterns,
        reason_codes=resolution.reason_codes,

        # nuevos campos
        product_name=user_facing["product_name"],
        capability_name=user_facing["capability_name"],
        discovery_mode=user_facing["discovery_mode"],
        user_facing_title=user_facing["user_facing_title"],
        user_facing_summary=user_facing["user_facing_summary"],
        user_facing_context=user_facing["user_facing_context"],
        next_step_hint=user_facing["next_step_hint"],
    )