from fastapi import APIRouter

from app.api.guards import require_debug_routes_enabled
from app.models.debug import OrchestrationDebugOutput
from app.models.routing import OrchestrationInput
from app.orchestration.composer import compose_output
from app.orchestration.debug_mapper import build_debug_view
from app.routing.resolver import resolve_input
from app.execution.narrative import generate_narrative
from app.orchestration.enrichment import enrich_summary

# nuevos imports para la costura de ejecución
from app.execution.provider import get_execution_binding
from app.execution.binding import RouterOutcome

router = APIRouter(tags=["orchestration"])


async def _maybe_execute(payload: OrchestrationInput, resolution, output):
    """Si el composer determinó un execute real, ejecuta y adjunta el toolResult
    neutral. Si la intención no mapea a ejecución de crypto, no hace nada
    (MCPOne sigue su flujo de recomendación normal)."""
    if output.next_step and output.next_step.type == "execute":
            binding = get_execution_binding()
            tool_result = await binding.resolve_and_execute(
                RouterOutcome(
                    module=resolution.recommended_module,
                    intent_family=resolution.intent_family,
                    message=payload.user_input,
                    selected_capabilities=resolution.selected_capabilities,
                )
            )
            if tool_result is not None:
                # Enriquecimiento con narrativa (detrás del flag; None si apagado).
                if tool_result.ok and tool_result.data:
                    narrative = await generate_narrative(
                        tool_result.kind, tool_result.data
                    )
                    if narrative:
                        tool_result.narrative = narrative
                output.tool_result = tool_result
    return output


@router.post("/orchestrate")
async def orchestrate(payload: OrchestrationInput):
    resolution = resolve_input(payload)
    output = compose_output(resolution)
    output = await _maybe_execute(payload, resolution, output)
    # Recomendación pura (sin ejecución): enriquecer el summary si el flag aplica.
    if output.tool_result is None:
          output.summary = await enrich_summary(output.summary, resolution)

    return output


@router.post("/orchestrate/debug", response_model=OrchestrationDebugOutput)
async def orchestrate_debug(payload: OrchestrationInput):
    disabled = require_debug_routes_enabled()
    if disabled is not None:
        return disabled

    resolution = resolve_input(payload)
    result = compose_output(resolution)
    result = await _maybe_execute(payload, resolution, result)
    if result.tool_result is None:
        result.summary = await enrich_summary(result.summary, resolution)
    debug = build_debug_view(resolution)

    return OrchestrationDebugOutput(
        result=result,
        debug=debug,
    )
